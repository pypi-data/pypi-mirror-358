import os
from datetime import datetime, timedelta, timezone
from .utils import to_json, load_json
from jsonschema import ValidationError

from logging import getLogger, getLevelName, INFO
logger = getLogger(__name__)
level = getLevelName(os.environ.get('LOG_LEVEL'))
logger.setLevel(level if isinstance(level, int) else INFO)

def execute(event, mod, result_root_key, post_function, invoke_on_error_only, validate_schema):
    """"""
    error = {}
    try:
        command_id = event.get('request', {}).get('command_id') or 'main'
        logger.info(f"START: '{mod.__module__}.{command_id}'")

        if validate_schema:
            from . import schema
            if waring := schema.validate_schema(event):
                logger.warning(waring)

        # exec __init__
        with mod(event) as client:
            cmd = getattr(client, command_id)
            result = cmd()  # exec

    except ValidationError as e:
        error = {'name': e.__class__.__name__, 'message': e.message}

    except AttributeError as e:
        # invalid command
        error = {'name': 'CommandError', 'message': f'Invalid command: "{command_id}"'}

    except Exception as e:
        error = {'name': e.__class__.__name__, 'message': str(e)}
    
    finally:
        if error:
            logger.error(f"{error['name']}: {error['message']}")
            result = {'exceptions': [error]}

    if result_root_key:
        result = {
            result_root_key: result
        }

    invoke_disabled = False
    if isinstance(result, dict):
        if 'invoke_disabled' in result:
            invoke_disabled = result['invoke_disabled']
            del result['invoke_disabled']

        if not result.get('date_time'):
            dt = datetime.now().astimezone(timezone(timedelta(hours=9)))
            result['date_time'] = dt.replace(microsecond=0).isoformat()

        if not result.get('result_id'):
            result['result_id'] = command_id

    if post_function:
        post_function(result, event)

    payload = {
        'message_log_id': event.get('message_log_id'),
        'result': result,
        'source': event.get('thing_dest_address'),
        'service_id': event.get('service_id'),
    }
    logger.info(f'response: {payload}')

    if not invoke_disabled and not event.get('standalone_invoke') and HUB_FUNCTION_NAME:
        valid = True
        if not payload['message_log_id']:
            logger.error('\'message_log_id\' is not available.')
            valid = False

        if not payload['source']:
            logger.error('\'thing_dest_address\' is not available.')
            valid = False

        if not payload['service_id']:
            logger.error('\'service_id\' is not available.')
            valid = False

        if valid and (not invoke_on_error_only or error):

            try:
                import boto3
                client = boto3.client('lambda')
                sts = client.invoke(
                    FunctionName=HUB_FUNCTION_NAME,
                    InvocationType='Event',
                    Payload=to_json(payload),
                )
                responseMetadata = sts['ResponseMetadata']
                logger.info('invoked: {0}, RequestId={1}, HTTPStatusCode={2}, RetryAttempts={3}'.format(HUB_FUNCTION_NAME,
                    responseMetadata['RequestId'], responseMetadata['HTTPStatusCode'], responseMetadata['RetryAttempts']))

            except Exception as e:
                logger.error(e)

    return payload


def handler(event, context, result_root_key = None, post_function = None, invoke_on_error_only = False, validate_schema = True):
    """"""
    logger.debug(f'request: {event}')

    if not isinstance(event, dict):
        raise Exception(f'invalid payload: {event}')

    global HUB_FUNCTION_NAME
    HUB_FUNCTION_NAME = os.environ.get('HUB_FUNCTION_NAME')

    if isinstance(context, str):
        driver_id = context
    else:
        driver_id = event.get('driver_id') or os.environ.get('DRIVER_NAME') or context.function_name
        if HUB_FUNCTION_NAME and HUB_FUNCTION_NAME.count(':') == 0 and context.invoked_function_arn.count(':') > 6:
            HUB_FUNCTION_NAME = HUB_FUNCTION_NAME + ':' + context.invoked_function_arn.split(':')[-1]

    components = f'drivers.{driver_id}.command.handler'.split('.')
    logger.debug(components)

    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)

    if records := event.get('Records'):
        payload = []
        for record in records:
            body = load_json(record['body'])
            if isinstance(body, dict):
                payload.append(execute(body, mod, result_root_key, post_function, invoke_on_error_only, validate_schema))
            else:
                logger.error(f'invalid payload: {event}')
        if len(payload) == 1:
            payload = payload[0]

    else:
        payload = execute(event, mod, result_root_key, post_function, invoke_on_error_only, validate_schema)

    return payload
