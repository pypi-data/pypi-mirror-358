import logging
import requests
import urllib3
from typing import Callable
from .logger import build_log_extra_api_resp
from .status import terminate_check as _terminate_check
from .status import UNKNOWN
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from .locals import local_vars


class FakeResponse():
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data


def get_test_data(
    logger: logging.Logger,     
    stage_id: str = None,
    terminate_check: Callable =_terminate_check, 
    headers: dict = {},
):
    response = None
    fake_response = FakeResponse(200, None)
    try:
        logger.info(f'Using test server to make request -> {local_vars.test_server_domain}')
        url = f'{local_vars.test_server_domain}/testcase/api/stage/response/'
        headers = {
            **headers, 
            'x-pid': local_vars.project_id,
            'x-fid': local_vars.feature_id,
            'x-tcsid': stage_id or local_vars.testcase_stage_id,
        }
        response = requests.request('GET', url, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            json_resp = response.json() 
            if json_resp.get('success'):
                fake_response.json_data = json_resp.get('data')
                return fake_response
            
        terminate_check(UNKNOWN, f"something wrong with simulation Server response [{response.status_code}]: {response.text}")
            
    except requests.exceptions.ConnectTimeout:
        extra_info = build_log_extra_api_resp(response)
        logger.warning(f"ConnectTimeout when connect to {url}", extra=extra_info)
        terminate_check(UNKNOWN, f"Timeout when connect to {url} -> extra_info: {extra_info}")
    except requests.exceptions.ReadTimeout:
        extra_info = build_log_extra_api_resp(response)
        logger.warning(f"ReadTimeout when connect to {url}", extra=extra_info)
        terminate_check(UNKNOWN, f"Timeout when read data from {url} -> extra_info: {extra_info}")
    except Exception as e:
        extra_info = build_log_extra_api_resp(response)
        logger.exception(f"Get exception {e} when connect to {url}", extra=extra_info)
        _msg = f"Error when request to {url} with error: {e} -> extra_info: {extra_info}"
        if isinstance(response, requests.Response):
            _msg += f" -> response: {response.text}"
        terminate_check(UNKNOWN, _msg)
