import boto3
import json
import logging

from django.conf import settings


endpoint_url = settings.SQS_ENDPOINT
sqs = boto3.client('sqs', endpoint_url=endpoint_url)


logger = logging.getLogger('sqs')


def sqs_func_factory(queue_url, receive_params):
    def send_message(MessageBody: dict, MessageAttributes: dict = None):
        response = sqs.send_message(QueueUrl=queue_url,
                                    MessageAttributes=MessageAttributes,
                                    MessageBody=json.dumps(MessageBody),
                                    DelaySeconds=10
                                    )
        return response

    def receive_message():
        response = sqs.receive_message(QueueUrl=queue_url, **receive_params)
        return response

    def delete_message(receipt_handle):
        response = sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logger.debug(f"[sqs_func_factory] message {receipt_handle} deleted")
        else:
            logger.error(f"[sqs_func_factory] message {receipt_handle} NOT deleted")

    return send_message, receive_message, delete_message
