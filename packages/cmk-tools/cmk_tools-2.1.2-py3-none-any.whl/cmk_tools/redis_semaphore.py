# -*- coding: utf-8 -*-
# author: NhanDD3 <hp.duongducnhan@gmail.com>

import logging
import time
import uuid
import redis
from .utils import get_func_name


logger = logging.getLogger("cmkredistools")


class RedisSemaphore:
    def __init__(self, redis_url: str, name, limit=-1, timeout=10):
        self.name = name  # Name of the semaphore key in Redis
        self.limit = limit  # Semaphore limit
        self.df_limit = 100  # Default limit
        self.redis_url = redis_url
        self.redis: redis.Redis = redis.from_url(
            redis_url, socket_timeout=5, decode_responses=True
        )  # Redis connection object
        self.timeout = timeout  # Timeout for acquiring the semaphore
        self.ttl = 2 * timeout + 1  # TTL for each semaphore lock (deadlock prevention)
        if self.is_redis_connected:
            logger.info(f"Connected to Redis")
        else:
            logger.error(f"Failed to connect to Redis at {redis_url}")

        if self.limit < 0:
            self.get_limit()
        else:
            self.set_limit()

        logger.info(
            f"Semaphore {self.name} initialized with limit: {self.limit} with key {self._limit_key_name()}, timeout: {self.timeout}, TTL: {self.ttl}."
        )

    def set_limit(self, limit=None) -> int:
        if not limit:
            limit = self.limit
        # set limit to redis
        limit_key = self._limit_key_name()
        return self.redis.set(limit_key, limit)

    def get_limit(self) -> int:
        # get limit from redis
        limit_key = self._limit_key_name()
        str_limit = self.redis.get(limit_key)
        if not str_limit:
            self.set_default_limit()
            self.limit = self.df_limit
        else:
            try:
                self.limit = int(str_limit)
            except ValueError:
                logger.error(
                    f"Invalid limit value: {str_limit}, set default limit = {self.df_limit}."
                )
                self.limit = self.df_limit  # Set default limit
        return self.limit

    def set_default_limit(self):
        limit_key = self._limit_key_name()
        return self.redis.set(limit_key, self.df_limit)

    def _limit_key_name(self):
        return f"{self.name}:limit"

    def _lock_name(self, lock_id):
        return f"{self.name}:{lock_id}"

    @property
    def is_redis_connected(self):
        if not self.redis:
            raise ValueError("No Redis connection found.")
        return self.redis.ping()

    def count(self):
        """
        Get the current count of the semaphore.
        """
        current_value = self.redis.get(self.name)
        return int(current_value) if current_value else 0

    def clear(self):
        """
        Clear the semaphore count and all lock IDs.
        """
        pipeline = self.redis.pipeline(True)
        pipeline.delete(self.name)
        pipeline.delete(self._lock_name("*"))
        pipeline.delete(self._limit_key_name())
        pipeline.execute()

    def acquire(self, timeout: float = None):
        """
        Acquire a semaphore slot with a unique identifier and set TTL to avoid deadlock.
        """
        if not timeout:
            timeout = self.timeout

        # Generate a unique ID for the semaphore slot
        lock_id = f'{uuid.uuid4()}___{int(time.time())}'
        start_time = time.time()
        while True:
            current_value = self.redis.get(self.name)
            current_value = int(current_value) if current_value else 0

            if current_value < self.limit:
                pipeline = self.redis.pipeline(True)
                pipeline.incr(self.name)  # Increment the semaphore count
                pipeline.expire(self.name, self.ttl)  # Set a TTL for the semaphore count
                # Set a unique lock ID with an expiration (TTL)
                pipeline.set(self._lock_name(lock_id), '1', ex=self.ttl, nx=True)
                pipeline.keys(self._lock_name("*"))  # Get all lock IDs

                # result = [semaphore_count, set_log_id_res, lock_id_keys,]
                result = pipeline.execute()

                if result[0] <= self.limit:  # Check if we acquired the semaphore successfully
                    return lock_id  # Return the unique lock ID
                else:
                    keys_to_delete = []
                    decr_count = 1
                    if result[2]:
                        for key in result[2]:
                            key_time = key.split("___")[-1]
                            if time.time() - float(key_time) > self.ttl:
                                keys_to_delete.append(key)
                                decr_count += 1
                    logger.debug(
                        f'found {len(keys_to_delete)} keys to delete', 
                        extra={
                            'keys_to_delete': keys_to_delete,
                            'decr_count': decr_count,
                        }
                    )
                    # Revert the count increment if the semaphore limit was exceeded
                    if decr_count > 1:
                        pipeline = self.redis.pipeline(True)
                        pipeline.decr(self.name, decr_count)
                        for key in keys_to_delete:
                            pipeline.delete(key)
                        pipeline.execute()
                    else:
                        self.redis.decr(self.name)
            else:
                if self.timeout > 0 and time.time() - start_time >= self.timeout:
                    logger.warning(f'Timeout lock {lock_id} acquiring the semaphore after {timeout} seconds.')
                    return None  # Timeout occurred
                time.sleep(0.05)  # Sleep briefly to avoid busy-waiting

    def release(self, lock_id):
        """
        Release the semaphore only if the lock_id matches to ensure proper release.
        """
        lock_name = self._lock_name(lock_id)
        if self.redis.exists(lock_name):
            pipeline = self.redis.pipeline(True)
            pipeline.decr(self.name)  # Decrement the semaphore count
            pipeline.delete(lock_name)  # Remove the lock ID key
            pipeline.execute()
            logger.info(f"Lock ID {lock_id} released.")
        else:
            logger.warning(f"Lock ID {lock_id} not found or already released.")


def run_with_semaphore(
    semaphore: RedisSemaphore,
    func,
    func_args=(),
    func_kwargs={},
    execute_when_timeout=True,
):
    """
    Run a function with a semaphore acquired and released automatically.
    """
    if not isinstance(semaphore, RedisSemaphore):
        raise ValueError(
            "The 'semaphore' argument must be an instance of RedisSemaphore."
        )

    lock_id = semaphore.acquire()
    if lock_id:
        try:
            logger.info(
                f"Acquired the semaphore for Function {get_func_name(func)} with lock ID: {lock_id}"
            )
            return func(*func_args, **func_kwargs)
        finally:
            semaphore.release(lock_id)
    else:
        if execute_when_timeout:
            logger.warning(
                f"Failed to acquire the semaphore (timeout). Function {get_func_name(func)} executed anyway"
            )
            return func(*func_args, **func_kwargs)
        else:
            logger.warning(
                f"Failed to acquire the semaphore (timeout). Function {get_func_name(func)} NOT executed."
            )


def run_with_semaphore_decorator(semaphore: RedisSemaphore):
    """
    Decorator to run a function with a semaphore acquired and released automatically.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            return run_with_semaphore(semaphore, func, args, kwargs)

        return wrapper

    return decorator


# Usage example
if __name__ == "__main__":
    redis_conn = redis.StrictRedis(host="localhost", port=6379, db=0)
    semaphore = RedisSemaphore(
        "redis://localhost:6379/0", name="my_semaphore", limit=10, timeout=10
    )

    lock_id = semaphore.acquire()
    if lock_id:
        try:
            print(f"Acquired the semaphore with lock ID: {lock_id}, performing task...")
            # Do some work here
            time.sleep(2)  # Simulate a task
        finally:
            semaphore.release(lock_id)
            print(f"Released the semaphore with lock ID: {lock_id}.")
    else:
        print("Failed to acquire the semaphore (timeout).")
