import logging
from typing import Dict, Callable
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError as ElasticsearchNotFoundError
from .status import UNKNOWN, validate_terminate_check_func
from .status import terminate_check as _terminate_check
from .locals import local_vars
from .call_test_server import get_test_data

class ScrollContextIsClosed(Exception):
    pass

def new_elk_client(host: str, port: str, username: str, password: str, verify_certs: bool=False):
    es_client = Elasticsearch(
        f'{host}:{port}',
        basic_auth=(username, password,),
        http_auth=(username, password,),
        verify_certs=verify_certs,
    )
    return es_client


def _search_with_scroll(
    client: Elasticsearch,
    index: str, 
    query: Dict, 
    logger: logging.Logger,
    scroll_time: str = '1m', # Specify how long a consistent view of the index should be maintained for scrolled search
    scroll_size: int = 500, # Specify how many results to return per scroll
    terminate_check: Callable =_terminate_check,
    scroll_retry: int = 3,
    raise_exc: bool = False,
    **kwargs,
):  
    if scroll_retry <= 0:
        logger.error(
            "ELK failed to scroll search after 3 retries",
            extra={'elk_query': query, 'elk_index': index}
        )
        terminate_check(UNKNOWN, "Failed to scroll search after 3 retries")

    try:
        scroll_id = None
        resp = client.search(
            index=index, 
            body=query,
            scroll=scroll_time, 
            size=scroll_size,     
        )
        if resp:
            scroll_id = resp.get('_scroll_id')
            inner_hits = resp.get('hits', {}).get('hits', [])
            if not inner_hits:
                return inner_hits
            else:
                yield inner_hits

            while inner_hits:
                try:
                    resp = client.scroll(scroll_id=scroll_id, scroll=scroll_time)
                    if resp:
                        inner_hits = resp.get('hits', {}).get('hits', [])
                        if not inner_hits:
                            return []
                        yield inner_hits
                    else:
                        logger.warning(
                            f'Failed to get response from scroll_id -> {scroll_id=}',
                            extra={'elk_query': query, 'elk_index': index}
                        )
                        terminate_check(UNKNOWN, f"Failed to get response from scroll_id -> {scroll_id=}")
                except ElasticsearchNotFoundError as e:
                    raise ScrollContextIsClosed(f'scroll context is closed or not found: {scroll_id=}')
        else:
            logger.warning(
                f'Failed to get response from scroll_id -> {scroll_id=}',
                extra={'elk_query': query, 'elk_index': index}
            )
            terminate_check(UNKNOWN, f"Failed to get scroll_id from response -> {resp}")
    except ScrollContextIsClosed:
        logger.warning(
            f'scroll context is closed or not found: {scroll_id=} -> retry',
            extra={'elk_query': query, 'elk_index': index}
        )
        return _search_with_scroll(
            client, index, query, 
            scroll_time, scroll_size,
            terminate_check,
            scroll_retry - 1,
            **kwargs,
        )
    except Exception as e:
        logger.exception(
            f"Failed to scroll search -> {e}",
            extra={'elk_query': query, 'elk_index': index}
        )
        if raise_exc:
            raise e
        else:
            terminate_check(UNKNOWN, f"Failed to scroll search -> {e}")


def _search(
    client: Elasticsearch,
    index: str, 
    query: Dict, 
    logger: logging.Logger,
    terminate_check: Callable =_terminate_check,
    raise_exc: bool = False,
    **kwargs,
):  
    try:
        resp = client.search(index=index, body=query)
        return resp.get('hits', {}).get('hits', [])
    except Exception as e:
        logger.exception(
            f"Failed to search -> {e}",
            extra={'elk_query': query, 'elk_index': index}
        )
        if raise_exc:
            raise e
        else:
            terminate_check(UNKNOWN, f"Failed to search -> {e}")

def elk_search(
    client: Elasticsearch,
    index: str, 
    query: Dict, 
    with_scroll: bool,
    scroll_time: str = '1m', # Specify how long a consistent view of the index should be maintained for scrolled search
    scroll_size: int = 500, # Specify how many results to return per scroll
    terminate_check: Callable =_terminate_check,
    stage_id: str = '',
    feature_id: str = '',
    **kwargs,
):
    logger = logging.getLogger(feature_id or local_vars.feature_id)
    validate_terminate_check_func(terminate_check, logger)
    if local_vars.test_server_enabled and stage_id:
        return get_test_data(logger, stage_id, terminate_check)

    if with_scroll:
        return _search_with_scroll(
            client, index, query, logger,
            scroll_time, scroll_size,
            terminate_check, 3, **kwargs,
        )
    else:
        return _search(
            client, index, query, logger,
            terminate_check, **kwargs,
        )
    
