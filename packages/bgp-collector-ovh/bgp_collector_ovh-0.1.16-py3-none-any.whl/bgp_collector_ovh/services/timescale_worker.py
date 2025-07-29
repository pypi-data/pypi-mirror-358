import pika
import logging
import logging.config
import sys
import redis
import json
from bgp_collector_ovh.db_tools.db_queries import (
    get_active_prefixes,
    add_prefix_state,
    get_neighbors_ids,
    get_total_active_prefixs_count,
    get_total_updates_count,
    add_system_state,
    check_system_state,
)
import os
from pathlib import Path

try:
    default_path = Path(__file__).resolve().parents[1] / "logging.conf"

    if default_path.exists():
        logging.config.fileConfig(default_path)
    else:
        raise FileNotFoundError(
            f"No valid logging configuration file found at {default_path}"
        )

    logger = logging.getLogger("root")

except Exception:
    print("Error with logging:", sys.exc_info()[0], sys.exc_info()[1])
    sys.exit(1)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")

redis_client = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
)

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()

channel.queue_declare(queue="timescale")


def capture_prefix_state(time=None, withdrawed_prefix_list=[], system_state_id=None):
    active_prefixes = get_active_prefixes()
    if len(withdrawed_prefix_list) != 0:
        prefix_list = active_prefixes.append()
    else:
        prefix_list = active_prefixes
    add_prefix_state(time, prefix_list, system_state_id)
    logger.info(
        f"Captured {len(prefix_list)} prefix states into PrefixState table for SystemState ID: {system_state_id}"
    )


def capture_system_state(time=None, withdrawed_prefix_list=[]):
    neighbors_list = get_neighbors_ids()
    total_prefixes = get_total_active_prefixs_count()
    total_updates = get_total_updates_count()
    system_state_id = check_system_state(time)
    if system_state_id is None:
        system_state_id = add_system_state(
            time, neighbors_list, total_prefixes, total_updates
        )

    capture_prefix_state(time, withdrawed_prefix_list, system_state_id)
    logger.info(f"Captured SystemState ID: {system_state_id}")


def callback(ch, method, properties, body):
    try:
        logger.info("Received %r" % body)
        message = json.loads(body)
        time = message["time"]

        if message["type"] == "prefix-announce":
            capture_system_state(time)

        elif message["type"] == "prefix-withdraw":
            capture_system_state(time)

    except Exception:
        logger.error("Error in callback", sys.exc_info()[0], sys.exc_info()[1])


channel.basic_consume(queue="timescale", on_message_callback=callback, auto_ack=True)

channel.start_consuming()
