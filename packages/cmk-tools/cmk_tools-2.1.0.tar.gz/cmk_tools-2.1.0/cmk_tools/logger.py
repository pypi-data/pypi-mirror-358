# -*- coding: utf-8 -*-
# author: NhanDD3 <hp.duongducnhan@gmail.com>
import logging
import os
import json
import requests
import threading
from datetime import datetime
from functools import wraps
from typing import Dict, List
from typing import Callable
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from pythonjsonlogger import jsonlogger
from .locals import local_vars


def json_translate_obj(obj):
    # for example, serialize a custom object
    # if isinstance(obj, MyClass):
    #     return {"special": obj.special}
    if isinstance(obj, Exception):
        return {'exception': str(obj)}
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def setup_time_rotation_logger(
    name, 
    level, 
    log_file_dir=None, 
    format_json=False, 
    json_translator=json_translate_obj
):
    if not log_file_dir:
        log_file_dir = os.path.join(Path.home(), "cmk-tools", "logs")

    if not os.path.isdir(log_file_dir):
        os.makedirs(log_file_dir, exist_ok=True)
    
    log_file_path = os.path.join(log_file_dir, f"{name}.log")
    # print("log files will be saved at:", log_file_path)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(
        log_file_path, when="midnight", interval=1, backupCount=7
    )

    if format_json:
        formatter = jsonlogger.JsonFormatter(
            timestamp=True,
            json_encoder=json.JSONEncoder,
            json_default=json_translator,
        )
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler.setFormatter(formatter)
    handler.setLevel(level)
    logger.addHandler(handler)
    return logger


def setup_log(name: str, level: int = logging.INFO):
    home_path = Path.home()
    log_dir = os.path.join(home_path, "fmon_active_check_logs")

    active_check_log_dir_name = name
    if active_check_log_dir_name.endswith((".log", ".txt",)):
        active_check_log_dir_name = active_check_log_dir_name.split(".")[0]
    log_dir = os.path.join(log_dir, active_check_log_dir_name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = setup_time_rotation_logger(name, level, log_file_dir=log_dir, format_json=True)
    logger.debug = restruct_log_method(logger.debug)
    logger.info = restruct_log_method(logger.info)
    logger.warn = restruct_log_method(logger.warn)
    logger.error = restruct_log_method(logger.error)
    logger.critical = restruct_log_method(logger.critical)
    logger.exception = restruct_log_method(logger.exception, True)
    logger.warning = restruct_log_method(logger.warning)
    return logger



def restruct_log_method(func, exc_info: bool = None):
    @wraps(func)
    def structured_method(
        message,
        exc_info: bool = exc_info,
        extra: Dict = None,
        stack_info=False,
        stacklevel=1,
        **kwargs
    ):
        if not extra:
            extra = {}

        extra.update({
            'jid': local_vars.jid,
            'pid': os.getpid(),
            'tid': threading.get_ident(),
        })
        if local_vars.feature_id:
            extra.update({'plugin_id': local_vars.feature_id})
        if local_vars.testcase_stage_id:
            extra.update({'stage_id': local_vars.testcase_stage_id})

        api_resp = None
        for k, v in kwargs.items():
            if k == 'api_resp' and isinstance(v, requests.Response):
                api_resp = v
        for k, v in extra.items():
            if k == 'api_resp' and isinstance(v, requests.Response):
                api_resp = v

        if api_resp and hasattr(api_resp, 'request') and isinstance(api_resp.request, (requests.Request, requests.PreparedRequest)):
            try:
                if api_resp.request.body:
                    req_body = api_resp.request.body.decode('utf-8')
                else:
                    req_body = ''
            except Exception as e:
                req_body = f'SystemError when decode request body -> {e}'
            extra.update({
                'api_request_url': api_resp.request.url,
                'api_request_method': api_resp.request.method,
                'api_request_headers': dict(api_resp.request.headers),
                'api_request_body': req_body,
                'api_status_code': api_resp.status_code,
                'api_response_text': api_resp.text
            })
        try:
            return func(message, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel)
        except Exception as e:
            new_extra = {'exc_extra': str(extra)}
            return func(message, exc_info=exc_info, extra=new_extra, stack_info=stack_info, stacklevel=stacklevel)
    return structured_method

def build_log_extra_api_resp(api_resp: requests.Response, req_uuid: str = ""):
    if not isinstance(api_resp, requests.Response):
        return {}
    
    extra = {
        'api_request_uuid': req_uuid,
        'api_response_status_code': api_resp.status_code,
        'api_response_text': api_resp.text
    }
    if hasattr(api_resp, 'request') and isinstance(api_resp.request, (requests.Request, requests.PreparedRequest)):
        try:
            if api_resp.request.body:
                if isinstance(api_resp.request.body, bytes):
                    req_body = api_resp.request.body.decode('utf-8')
                else:
                    req_body = str(api_resp.request.body)
            else:
                req_body = ''
        except Exception as e:
            req_body = f'SystemError when decode request body -> {e}'
        extra.update({
            'api_request_url': api_resp.request.url,
            'api_request_method': api_resp.request.method,
            'api_request_headers': dict(api_resp.request.headers),
            'api_request_body': req_body,
        })
    return extra