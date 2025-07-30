# -*- coding: utf-8 -*-
# author: NhanDD3 <hp.duongducnhan@gmail.com>


__version__ = '2.1.1'


from .logger import setup_time_rotation_logger, setup_log
from .redis_semaphore import (
    RedisSemaphore,
    run_with_semaphore,
    run_with_semaphore_decorator,
)
from .rest_request import make_request, is_test_device
from .status import terminate_check, OK, WARN, WARNING, CRITICAL, ERROR, UNKNOWN
from .mkp_packer import pack_mkp
from .rest_request_v2 import make_request_v2
from .locals import set_plugin_id, detect_is_test_host   
from .elk_client import elk_search, new_elk_client


__all__ = [
    "RedisSemaphore",

    "setup_time_rotation_logger",
    "setup_log",

    "run_with_semaphore",
    "run_with_semaphore_decorator",

    "make_request",
    'is_test_device',

    "terminate_check",
    "OK",
    "WARN",
    "WARNING",
    "CRITICAL",
    "ERROR",
    "UNKNOWN",
    
    'pack_mkp',

    'make_request_v2',
    'set_plugin_id',
    'detect_is_test_host',

    'elk_search', 
    'new_elk_client',

]
