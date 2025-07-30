import sys 
import logging
from typing import Callable


DEBUG = "DEBUG"
OK = "OK"
WARN = "WARN"
WARNING = "WARNING"
CRITICAL = "CRITICAL"
ERROR = "ERROR"
UNKNOWN = "UNKNOWN"



def terminate_check(status, msg):
    # -----------------------------------------   
    #   DO NOT MODIFY THIS FUNCTION
    # -----------------------------------------    
    print(f"{status} - {msg}")
    if status == OK:
        sys.exit(0)
    elif status == WARNING:
        sys.exit(1)
    elif status == CRITICAL:
        sys.exit(2)
    else:
        sys.exit(3)


def validate_terminate_check_func(func: Callable, logger: logging.Logger):
    if not callable(func):
        logger.error(f"terminate_check must be a function -> get type={type(func)}") 
        raise ValueError("terminate_check must be a function")