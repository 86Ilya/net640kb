import json
import logging
import asyncio

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer

from Net640.apps.ws_eventbus.sqs_connect import sqs_func_factory


CHANNEL_LAYER = get_channel_layer()
logger = logging.getLogger('eventbus')


class SQSProcessing:
    def __init__(self, queue_url, recv_params):
        self.queue_url = queue_url
        self.recv_params = recv_params
        _, self._receive_message, self._delete_message = sqs_func_factory(queue_url, recv_params)

    def start(self):
        self.loop_over_sqs_messages_task = asyncio.ensure_future(self.loop_over_sqs_messages())

    async def loop_over_sqs_messages(self):

        while True:
            try:
                response = await sync_to_async(self._receive_message)()
                messages = response.get('Messages', None)
                # if we have not received messages
                if messages is None:
                    continue
            except Exception as error:
                logger.error(f"[SQSProcessing.loop_over_sqs_messages] "
                             f"error while getting message from queue: {error}",
                             exc_info=True)
                continue

            try:
                for message in messages:
                    logger.debug(f"SQSProcessing.loop_over_sqs_messages get {message}")
                    try:
                        room_name = message['MessageAttributes']['room_name']['StringValue']
                        body = json.loads(message['Body'])
                        # TODO: no wait, error handle
                        await CHANNEL_LAYER.group_send(room_name, body)
                        logger.debug(f"SQSProcessing.loop_over_sqs_messages sent {message} to {room_name}")
                    except Exception as error:
                        logging.error(f"error {error}, {message}")
                    finally:
                        asyncio.ensure_future(sync_to_async(self._delete_message)(message['ReceiptHandle']))
                        self._delete_message(message['ReceiptHandle'])
            except Exception as error:
                logger.error(f"[SQSProcessing.loop_over_sqs_messages] "
                             f"error while putting message to storage: {error}",
                             exc_info=True)

    async def _delete_message(self, receipt_handle):
        """
        Метод удаляет обработанное сообщение.
        :param receipt_handle: идентификатор хендлера получения сообщения
        :type receipt_handle: str
        :returns: None
        :rtype: None
        """
        try:
            await sync_to_async(self.delete_message)(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
        except Exception as error:
            logger.error(f"[ResultsDistributor.delete_message] "
                         f"error while deleting message from queue: {error}",
                         exc_info=True)
