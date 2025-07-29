import sys
import re
import os
import time
import uuid
import logging
from typing import Callable, Tuple, Any
from .logger import build_log_extra_api_resp
from .status import UNKNOWN, validate_terminate_check_func
from .status import terminate_check as _terminate_check
from .locals import local_vars
from .call_test_server import get_test_data
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def make_request_v2(
    url, 
    method: str, 
    params: dict = None,
    data: dict =None,
    json = None,
    headers: dict = {}, 
    verify=False, 
    auth=None, 
    terminate_check: Callable =_terminate_check,
    proxies: dict = None,
    stage_id: str = '',
    feature_id: str = '',
    timeout: tuple | int = (10, 30,),
    raise_exc: bool = False,
    **kwargs
) -> requests.Response: 
    logger = logging.getLogger(feature_id or local_vars.feature_id)
    validate_terminate_check_func(terminate_check, logger)
    _req_uuid = str(uuid.uuid4())
    _req_start = time.perf_counter()
    logger.info(
        f'start request to [{method}] {url}',
        extra={
            'api_request_uuid': _req_uuid,
        }
    )

    method_upper = method.upper()
    if method_upper not in ['GET', 'POST', 'PUT', 'DELETE']:
        logger.error(
            f"method must be get/post/put/delete -> get method={method}",
            extra={'api_request_method': method}
        ) 
        terminate_check(UNKNOWN, f"request API method >>{method}<< not supported")
    
    if local_vars.test_server_enabled and stage_id:
        # run test only, for development stage or testing stage
        return get_test_data(logger, stage_id, terminate_check, headers)

    response = None
    try:
        if method_upper in ('GET', 'DELETE'):
            response = requests.request(method, url, headers=headers, params=params, verify=verify, proxies=proxies, auth=auth, timeout=timeout) 
        else:
            response = requests.request(method, url, headers=headers, data=data, verify=verify, json=json, proxies=proxies, auth=auth, timeout=timeout)
        logger.info(f"Request to {url} with method {method} successfully", extra=build_log_extra_api_resp(response, _req_uuid))
        response.raise_for_status()
        
    except requests.exceptions.ConnectTimeout as e:
        logger.warning(f"ConnectTimeout when connect to {url}", extra=build_log_extra_api_resp(response, _req_uuid))
        if raise_exc:
            raise e
        else:
            terminate_check(UNKNOWN, f"Timeout when connect to {url}")
    except requests.exceptions.ReadTimeout as e:
        logger.warning(f"ReadTimeout when connect to {url}", extra=build_log_extra_api_resp(response, _req_uuid))
        if raise_exc:
            raise e
        else:
            terminate_check(UNKNOWN, f"Timeout when read data from {url}")
    except Exception as e:
        logger.exception(f"Get exception {e} when connect to {url}", extra=build_log_extra_api_resp(response, _req_uuid))
        if raise_exc:
            raise e
        else:
            terminate_check(UNKNOWN, f"Error when request to {url} with error: {e}")
    finally:
        logger.info(
            f'finish request to [{method}] {url}',
            extra={
                'api_request_uuid': _req_uuid,
                'api_request_time': round(time.perf_counter() - _req_start, 4),
            }
        )
    return response