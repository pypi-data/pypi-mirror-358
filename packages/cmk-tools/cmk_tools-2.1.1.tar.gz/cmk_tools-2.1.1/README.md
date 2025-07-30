# CmkRedisTools

## Installation

To install the CmkRedisTools package, you can use pip:

```sh
pip install cmk-tools
```
or

```sh
poetry add cmk-tools
```

## Testing

To run tests for CmkRedisTools, use the following command:

```sh
pytest
```

## Example 
All connector must provide `unique stage_id` for testing purrpose

### Using `redis semaphore`
Here is a simple example of how to use CmkRedisTools:

```python
from cmk_tools import RedisSemaphore, run_with_semaphore

semaphore = RedisSemaphore(
    'redis://localhost:6379/0',
    name="my_semaphore",
    limit=3,            # limit concurrent running task
    timeout=10          # accquire timeout
)

run_with_semaphore(
    your_func,
    func_args,
    func_kwargs,
    execute_when_timeout=True       # execute function if accquired timeout
)
```

For more detailed documentation, email me.


### Using `make_request_v2`

Here is an example of how to use the `make_request_v2` function:

```python
from cmk_tools import make_request_v2

response = make_request_v2(
    url='https://api.example.com/data',
    method='GET',
    headers={'Authorization': 'Bearer YOUR_TOKEN'},
    params={'key': 'value'},
    data={'key': 'value'},
    stage_id='unique-id',
)
print(response.json())
```

### Using `es_client`

Here is an example of how to use the `es_client` function:

```python
from cmk_tools import new_elk_client, elk_search

es_client = new_elk_client('host', 'port', 'username', 'password')
body = {"query": {}, "sort": []}
search_res = elk_search(
    es_client, 
    'index', body, 
    with_scroll=False, 
    stage_id='unique-id'
)

# search_res should be an arrays of inner hits
print(search_res)
```

Here is an example of how to use the `es_client` search `with scroll` for get many data:

```python
from cmk_tools import new_elk_client, elk_search

es_client = new_elk_client('host', 'port', 'username', 'password')
body = {"query": {}, "sort": []}
search_res = elk_search(
    es_client, 
    'index', body, 
    with_scroll=True, 
    stage_id='unique-id'
)

# search_res should be an arrays of inner hits
print(search_res)
```


### Using `snmp_get`

Here is an example of how to use the `snmp_get` function:

```python
from cmk_tools.snmp_client import snmp_get

data = netsnmp.VarList(
    '....',
)
result = snmp_get(
    host='192.168.1.1',
    community='public',
    data=data,
    stage_id='unique-id'
)

print(result)
```