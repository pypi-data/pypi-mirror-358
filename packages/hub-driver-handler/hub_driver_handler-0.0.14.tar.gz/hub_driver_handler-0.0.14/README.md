# hub-driver-handler Package

## standard file structure
```
+ drivers/
   + DRIVER_ID/
      + __init__.py
      + command.py
      + ANYFILES...
   + DRIVER_ID2/...
   + schema/
   + __init__.py
   + requirements.txt
+ .dockerignore
+ app.py
+ Dockerfile
```
- drivers/DRIVER_ID/\_\_init\_\_.py is required and might be empty.
- environment variable 'HUB_FUNCTION_NAME' is required to notify the results to the IoT-hub.
- if 'HUB_FUNCTION_NAME' is not contains alias/version and your function invoked with alias/version, this will be added to invoke.
- environment variable 'LOG_LEVEL' can change the default log level 'INFO'.

## drivers/\_\_init\_\_.py
```
import drivers.{DRIVER_ID}.command
import drivers.{DRIVER_ID2}.command
...
```
- add all drivers for import.

## command.py
```
class handler(object):
    def __init__(self, event):
        # store required data from event value
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __del__(self):
        pass

    def ANY_COMMAND(self):
        ...
        return result
    ...
```
- implement your driver code in this file.
- class name must be 'handler'.
- event["request"]["command_id"] will be executed.

## .dockerignore
```
**/__pycache__
**/.pytest_cache
*.pyc
```
- this is the best practice.

## app.py
```
from hub_driver_handler.handler import handler

def lambda_handler(event, context):
    return handler(event, context, result_root_key = None, post_function = None, invoke_on_error_only = False, validate_schema = True)
```
- driver_id will be determined as below sequence.
    1. event.get('driver_id')
    2. os.environ.get('DRIVER_NAME')
    3. context.function_name

[previous format]
```
import os
from hub_driver_handler.handler import handler

def lambda_handler(event, context):
    driver_id = event.get('driver_id') or os.environ.get('DRIVER_NAME') or context.function_name
    return handler(event, driver_id, result_root_key = None, post_function = None, invoke_on_error_only = False, validate_schema = True)
```
- this code expected 'driver_id' will be passed from the IoT-hub for multiple drivers support, but currently not.
- set enviroment variable 'DRIVER_NAME' explicitly or set lambda function name as driver_id for now.
- set 'result_root_key' if you want to add root key for results, ex: 'result_params'
- 'date_time' and 'result_id' will be added if not present.
- 'post_function' can modify the results from each driver as below:

    def post_function(result, event):
        result['cmd'] = event['request']['command_id']
        ...
- If only send the result to IoT-hub on error, set 'invoke_on_error_only' to True
- SQS paylod by lambda trigger is also supported.
- event data will be validated by JSON Schema file in 'drivers/DRIVER_ID/schema' folder, set 'validate_schema' to False if validation is not needed.

## Dockerfile
```
FROM public.ecr.aws/lambda/python:3

COPY app.py ./
COPY drivers/ ./drivers

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install hub-driver-handler -t .
RUN python3 -m pip install -r drivers/requirements.txt -t .

# Command can be overwritten by providing a different command in the template directly.
CMD ["app.lambda_handler"]
```

## requirements.txt
- add required packages for all drivers
