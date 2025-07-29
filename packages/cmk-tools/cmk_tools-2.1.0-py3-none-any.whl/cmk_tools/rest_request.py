import sys
import re
import os
import logging
from typing import Callable
from .logger import build_log_extra_api_resp
from .utils import replace_domain
from .status import OK, WARNING, CRITICAL, UNKNOWN
from .status import terminate_check as _terminate_check
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


KEY_ACTIVE_CHECK_ID = 'ACTIVE_CHECK_ID'
# SCC_USE_TEST_SERVER = 'http://testserver/'
SCC_USE_TEST_SERVER = os.getenv("SCC_USE_TEST_SERVER")
if SCC_USE_TEST_SERVER and not 'http' in SCC_USE_TEST_SERVER:
    raise ValueError("SCC_USE_TEST_SERVER must be a valid URL")

def is_test_device(name: str) -> bool:
    try:
        if name and name.lower().startswith('SCC_TEST_SVR_'):
            search_res = re.search(r'SCC_TEST_SVR_([\w\d\.\:]*)_', name)
            if search_res:
                domain_or_ipport = search_res.group(1)
                if domain_or_ipport:
                    if not domain_or_ipport.startswith('http'):
                        # because of local using, we need to add https
                        domain_or_ipport = f'http://{domain_or_ipport}'
                    os.environ['SCC_USE_TEST_SERVER'] = domain_or_ipport
                    return True
    except Exception as e:
        return False

def make_request(
    plugin_id: str,
    method: str, 
    url, 
    params: dict = None,
    data: dict =None,
    json = None,
    headers: dict = {}, 
    verify=False, 
    terminate_check: Callable =_terminate_check,
    proxies: dict = None,
    logger_name: str = "cmk-tools",
    **kwargs
): 
    logger = logging.getLogger(os.environ.get('KEY_ACTIVE_CHECK_ID', logger_name))
    if not callable(terminate_check):
        raise ValueError("terminate_check must be a function")

    method_upper = method.upper()
    if method_upper not in ['GET', 'POST', 'PUT', 'DELETE']:
        return terminate_check(UNKNOWN, f"request API method >>{method}<< not supported")
    
    response = None
    try:
        if SCC_USE_TEST_SERVER:
            new_url = f'{SCC_USE_TEST_SERVER}/cmk-plugin/api/testcase/response/'
            headers = {
                **headers, 
                'x-plugin-id': plugin_id,
                'x-original-url': url,
            }
            response = requests.request('POST', new_url, headers=headers, data=data, verify=verify, proxies=proxies, json=json)
        else:
            if method_upper in ('GET', 'DELETE'):
                response = requests.request(method, url, headers=headers, params=params, verify=verify, proxies=proxies) 
            else:
                response = requests.request(method, url, headers=headers, data=data, verify=verify, json=json, proxies=proxies)
        response.raise_for_status()
        logger.debug(f"Request to {url} with method {method} successfully", extra=build_log_extra_api_resp(response))
    except requests.exceptions.ConnectTimeout:
        logger.warning(f"ConnectTimeout when connect to {url}", extra=build_log_extra_api_resp(response))
        terminate_check(UNKNOWN, f"Timeout when connect to {url}")
    except requests.exceptions.ReadTimeout:
        logger.warning(f"ReadTimeout when connect to {url}", extra=build_log_extra_api_resp(response))
        terminate_check(UNKNOWN, f"Timeout when read data from {url}")
    except Exception as e:
        logger.exception(f"Get exception {e} when connect to {url}", extra=build_log_extra_api_resp(response))
        terminate_check(UNKNOWN, f"Error when request to {url} with error: {e}")
    finally:
        return response