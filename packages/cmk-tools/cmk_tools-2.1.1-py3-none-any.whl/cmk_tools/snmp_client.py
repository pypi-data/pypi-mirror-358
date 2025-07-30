
# 
# ATTENTION: Make sure use this file within CHECKMK 
# because CheckMK has its own netsnmp library
#
import logging
from typing import Dict, Callable
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from .status import UNKNOWN, validate_terminate_check_func
from .status import terminate_check as _terminate_check
from .locals import local_vars
from .call_test_server import get_test_data
import netsnmp


def snmp_get(
    dest_host: str,
    community: str, 
    data: netsnmp.VarList,
    snmp_timeout: int = 1000000,
    snmp_version: int = 2,
    retries: int = 2,
    terminate_check: Callable =_terminate_check,
    stage_id: str = '',
    feature_id: str = '',
    raise_exc: bool = False,
):
    logger = logging.getLogger(feature_id or local_vars.feature_id)
    validate_terminate_check_func(terminate_check, logger)

    if local_vars.test_server_enabled and stage_id:
        return get_test_data(logger, stage_id, terminate_check)

    try:
        sess = netsnmp.Session(
            DestHost=dest_host, Community=community, 
            Version=snmp_version, Timeout=snmp_timeout, 
            Retries=retries
        )

        res = sess.get(data)
        decoded_res = []
        for item in res:
            if item is None:
                decoded_res.append(None)
            else:
                decoded_res.append(item.decode())
        
        return decoded_res
    except Exception as e:
        logger.exception(
            f"Get exception {e} when connect to {dest_host}",
            extra={'snmp_host': dest_host, 'snmp_req_data': str(data)}
        )
        if raise_exc:
            raise e
        else:
            terminate_check(UNKNOWN, f"Error when request to {dest_host} with error: {e}")