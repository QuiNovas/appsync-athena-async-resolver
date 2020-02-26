from binascii import a2b_hex
from boto3 import client
from datetime import datetime
from decimal import Decimal
from distutils.util import strtobool
from json import dumps as jsondumps, loads as jsonloads
from logging import getLogger, INFO
from os import environ


def __query(event):
    response = __ATHENA.start_query_execution(
        QueryString=event['query'],
        QueryExecutionContext={
            'Database': event.get('database', environ.get('DATABASE', 'default'))
        },
        WorkGroup=event.get('workgroup', environ.get('WORKGROUP', 'primary'))
    )
    return __get_status(response['QueryExecutionId'])


def __status(event):
    return __get_status(event['id'])


def __results(event):
    params = {
        'QueryExecutionId': event['id'],
        'MaxResults': int(event.get('limit', environ.get('LIMIT', 100)))
    }
    if 'nextToken' in event:
        params['NextToken'] = event['nextToken']
    response = __ATHENA.get_query_results(**params)
    meta_data = __map_meta_data(response['ResultSet']['ResultSetMetadata']['ColumnInfo'])
    results = []
    rows = response['ResultSet']['Rows']
    for n in range(1, len(rows)):
        results.append(__map_result(meta_data, rows[n]['Data']))
    result = {
        'results': results
    }
    if 'NextToken' in response:
        result['nextToken'] = response['NextToken']
    return result


getLogger().setLevel(INFO)
__ACTIONS = {
    'query': __query,
    'status': __status,
    'results': __results
}
__ATHENA = client('athena')
__ATHENA_TYPE_CONVERTERS = {
    'boolean': lambda x: bool(strtobool(x)) if x else None,
    'tinyint': lambda x: int(x) if x else None,
    'smallint': lambda x: int(x) if x else None,
    'integer': lambda x: int(x) if x else None,
    'bigint': lambda x: int(x) if x else None,
    'float': lambda x: float(x) if x else None,
    'real': lambda x: float(x) if x else None,
    'double': lambda x: float(x) if x else None,
    'char': lambda x: x,
    'varchar': lambda x: x,
    'string': lambda x: x,
    'timestamp': lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f').isoformat() if x else None,
    'date': lambda x: datetime.strptime(x, '%Y-%m-%d').date().isoformat() if x else None,
    'time': lambda x: datetime.strptime(x, '%H:%M:%S.%f').time().isoformat() if x else None,
    'varbinary': lambda x: a2b_hex(''.join(x.split(' '))) if x else None,
    'array': lambda x: x,
    'map': lambda x: x,
    'row': lambda x: x,
    'decimal': lambda x: Decimal(x) if x else None,
    'json': lambda x: jsonloads(x) if x else None,
}


def handler(event, context):
    getLogger().debug('Processing event {}'.format(jsondumps(event)))
    return __ACTIONS.get(event['action'], __unsupported_action)(event['arguments'])


def __get_status(query_execution_id):
    response = __ATHENA.get_query_execution(
        QueryExecutionId=query_execution_id
    )
    status = {}
    execution = response['QueryExecution']
    status['id'] = execution['QueryExecutionId']
    response_status = execution['Status']
    status['state'] = response_status['State']
    if 'StateChangeReason' in response_status:
        status['stateChangeReason'] = response_status['StateChangeReason']
    status['submissionDateTime'] = response_status['SubmissionDateTime'].isoformat()
    if 'CompletionDateTime' in response_status:
        status['completionDateTime'] = response_status['CompletionDateTime'].isoformat()
    return status


def __map_meta_data(meta_data):
    mapped_meta_data = []
    for column in meta_data:
        mapped_meta_data.append((column['Name'], __ATHENA_TYPE_CONVERTERS[column['Type']]))
    return mapped_meta_data


def __map_result(meta_data, data):
    result = {}
    for n in range(len(data)):
        result[meta_data[n][0]] = meta_data[n][1](data[n].get('VarCharValue', None))
    return result


def __unsupported_action(event):
    raise ValueError('Action {} is not supported'.format(event['action']))
