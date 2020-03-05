from athena_type_converter import convert_result_set
from boto3 import client
from json import dumps as jsondumps
from logging import getLogger, INFO
from os import environ


__DATABASE = environ.get('DATABASE', 'default')
__LIMIT = environ.get('LIMIT', 100)
__WORKGROUP = environ.get('WORKGROUP', 'primary')


def __query(event):
    response = __ATHENA.start_query_execution(
        QueryString=event['query'].format(**event.get('params', {})),
        QueryExecutionContext={
            'Database': event.get('database', __DATABASE)
        },
        WorkGroup=event.get('workgroup', __WORKGROUP)
    )
    return __get_status(response['QueryExecutionId'])


def __status(event):
    return __get_status(event['id'])


def __results(event):
    params = {
        'QueryExecutionId': event['id'],
        'MaxResults': int(event.get('limit', __LIMIT))
    }
    if event.get('nextToken'):
        params['NextToken'] = event['nextToken']
    response = __ATHENA.get_query_results(**params)
    result = {
        'results': convert_result_set(response['ResultSet'])
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


def __unsupported_action(event):
    raise ValueError('Action {} is not supported'.format(event['action']))
