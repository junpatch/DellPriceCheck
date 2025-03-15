import sys

from app import execute_spider


def handler(event, context):
    result = execute_spider()
    
    return result