import boto3
import json
import logging.config
import os

from logging import getLogger, INFO

getLogger().setLevel(INFO)


def handler(event, context):
    getLogger().debug('Processing event {}'.format(json.dumps(event)))
