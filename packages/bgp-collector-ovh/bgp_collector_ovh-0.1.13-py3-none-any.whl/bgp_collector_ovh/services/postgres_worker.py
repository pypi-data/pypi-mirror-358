import pika
import logging
import logging.config
import sys
import json
import redis
from bgp_collector_ovh.db_tools.db_queries import (
    add_host,
    get_neighbor,
    add_neighbor,
    add_update,
    check_prefixT5,
    update_prefixT5,
    add_prefixT5,
    add_prefixT2,
    get_prefixT2,
    update_prefixT2,
    add_prefixT3,
    get_prefixT3,
    update_prefixT3,
    kill_prefixT5,
    kill_prefixT3,
    kill_prefixT2,
    add_dead_prefixT5,
    add_dead_prefixT3,
    get_rd,
    add_rd,
)
import os
from pathlib import Path
import time

# try:
#     default_path = Path(__file__).resolve().parents[1] / "logging.conf"

#     if default_path.exists():
#         logging.config.fileConfig(default_path)
#     else:
#         raise FileNotFoundError(
#             f"No valid logging configuration file found at {default_path}"
#         )

#     logger = logging.getLogger("root")

# except Exception:
#     print("Error with logging:", sys.exc_info()[0], sys.exc_info()[1])
#     sys.exit(1)

# REDIS_HOST = os.getenv("REDIS_HOST", "redis")
# REDIS_PORT = os.getenv("REDIS_PORT", "6379")
# RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
# RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")

# redis_client = redis.StrictRedis(
#     host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
# )

# connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
# channel = connection.channel()

# channel.queue_declare(queue="postgres")
# channel.queue_declare(queue="timescale")


# def callback(ch, method, properties, body):
#     try:
#         logger.info("Received in Postgres worker %r" % body)
#         message = json.loads(body)

#         if message["type"] == "host":
#             host_id = add_host(message["hostname"])
#             redis_client.setex(f"{message['session_token']}:host_id", 300, host_id)

#         elif message["type"] == "neighbor":
#             host_id = None
#             if message["host_id"] is None:
#                 host_id = redis_client.get(f"{message['session_token']}:host_id")
#             neighbor = get_neighbor(
#                 host_id if host_id is not None else message["host_id"], message["ip"]
#             )
#             if neighbor is None:
#                 neighbor_id = add_neighbor(
#                     host_id if host_id is not None else message["host_id"],
#                     message["ip"],
#                     message["asn"],
#                 )
#                 redis_client.setex(
#                     f"{message['session_token']}:neighbor_id", 300, neighbor_id
#                 )
#             else:
#                 redis_client.setex(
#                     f"{message['session_token']}:neighbor_id", 300, neighbor.id
#                 )

#         elif message["type"] == "update":
#             neighbor_id = redis_client.get(f"{message['session_token']}:neighbor_id")
#             if neighbor_id is None:
#                 logger.error("Neighbor id not found")
#                 return
#             update_id = add_update(
#                 neighbor_id,
#                 "update",
#                 message["update_type"],
#                 message["family"],
#                 redis_client.get(f"{message['session_token']}:time"),
#             )
#             redis_client.setex(f"{message['session_token']}:update_id", 300, update_id)

#         elif message["type"] == "prefixT5":
#             # Check if RD exists
#             rd_obj = get_rd(message["rd"])
#             if rd_obj is None:
#                 add_rd(message["rd"])

#             prefix = check_prefixT5(message["ip"], message["iplen"], message["rd"])
#             if prefix is not None:
#                 if (
#                     prefix.med
#                     == int(redis_client.get(f"{message['session_token']}:med"))
#                     and prefix.localpref
#                     == int(redis_client.get(f"{message['session_token']}:local_pref"))
#                     and prefix.routermac
#                     == int(redis_client.get(f"{message['session_token']}:routermac"))
#                 ):
#                     # Strictly identical, update entry
#                     update_prefixT5(
#                         prefix,
#                         int(redis_client.get(f"{message['session_token']}:update_id")),
#                     )
#                 else:
#                     add_prefixT5(
#                         int(redis_client.get(f"{message['session_token']}:nexthop_id")),
#                         int(redis_client.get(f"{message['session_token']}:update_id")),
#                         message["rd"],
#                         message["ip"],
#                         message["iplen"],
#                         redis_client.get(f"{message['session_token']}:aspath"),
#                         int(redis_client.get(f"{message['session_token']}:med")),
#                         int(redis_client.get(f"{message['session_token']}:local_pref")),
#                         int(redis_client.get(f"{message['session_token']}:routermac")),
#                     )
#             else:
#                 add_prefixT5(
#                     int(redis_client.get(f"{message['session_token']}:nexthop_id")),
#                     int(redis_client.get(f"{message['session_token']}:update_id")),
#                     message["rd"],
#                     message["ip"],
#                     message["iplen"],
#                     redis_client.get(f"{message['session_token']}:aspath"),
#                     int(redis_client.get(f"{message['session_token']}:med")),
#                     int(redis_client.get(f"{message['session_token']}:local_pref")),
#                     int(redis_client.get(f"{message['session_token']}:routermac")),
#                 )
#             if message["last_one"] is True:
#                 message = json.dumps(
#                     {
#                         "type": "prefix-announce",
#                         "time": redis_client.get(f"{message['session_token']}:time"),
#                     }
#                 )
#                 channel.basic_publish(
#                     exchange="", routing_key="timescale", body=message
#                 )

#         elif message["type"] == "prefixT2":
#             if get_rd(message["rd"]) is None:
#                 add_rd(message["rd"])

#             prefix = get_prefixT2(message["mac"], message["rd"])
#             try:
#                 nexthop_id = int(
#                     int(redis_client.get(f"{message['session_token']}:nexthop_id")) or 0
#                 )
#                 update_id = int(
#                     int(redis_client.get(f"{message['session_token']}:update_id")) or 0
#                 )
#             except ValueError:
#                 logger.error("Invalid nexthop_id or update_id in Redis")
#                 return

#             if prefix is not None:
#                 logger.info(
#                     "prefix.nhid %d , nhid %d", prefix.fk_nexthop_id, nexthop_id
#                 )

#             if prefix is not None and prefix.fk_nexthop_id == nexthop_id:
#                 update_prefixT2(prefix, update_id)
#                 logger.info("once")
#             else:
#                 if prefix is not None:
#                     kill_prefixT2(prefix)
#                 add_prefixT2(nexthop_id, update_id, message["rd"], message["mac"])
#                 logger.info("adding prefix T2")

#             if message.get("last_one") is True:
#                 final_message = json.dumps(
#                     {
#                         "type": "prefix-announce",
#                         "time": redis_client.get(f"{message['session_token']}:time"),
#                     }
#                 )
#                 channel.basic_publish(
#                     exchange="", routing_key="timescale", body=final_message
#                 )

#         elif message["type"] == "prefixT3":
#             rd_obj = get_rd(message["rd"])
#             if rd_obj is None:
#                 add_rd(message["rd"])
#             prefix = get_prefixT3(message["ip"], message["ethernet_tag"], message["rd"])
#             if prefix is not None:
#                 update_prefixT3(
#                     prefix,
#                     int(redis_client.get(f"{message['session_token']}:update_id")),
#                 )
#             else:
#                 add_prefixT3(
#                     int(redis_client.get(f"{message['session_token']}:nexthop_id")),
#                     int(redis_client.get(f"{message['session_token']}:update_id")),
#                     message["rd"],
#                     message["ip"],
#                     message["ethernet_tag"],
#                 )
#             if message["last_one"] is True:
#                 message = json.dumps(
#                     {
#                         "type": "prefix-announce",
#                         "time": redis_client.get(f"{message['session_token']}:time"),
#                     }
#                 )
#                 channel.basic_publish(
#                     exchange="", routing_key="timescale", body=message
#                 )

#         elif message["type"] == "withdraw_T5":
#             rd_obj = get_rd(message["rd"])
#             if rd_obj is None:
#                 add_rd(message["rd"])
#             prefix = check_prefixT5(message["ip"], message["iplen"], message["rd"])
#             if prefix is not None:
#                 kill_prefixT5(prefix)
#             else:
#                 add_dead_prefixT5(
#                     int(redis_client.get(f"{message['session_token']}:update_id")),
#                     message["rd"],
#                     message["ip"],
#                     message["iplen"],
#                     redis_client.get(f"{message['session_token']}:aspath"),
#                     int(redis_client.get(f"{message['session_token']}:med")),
#                     int(redis_client.get(f"{message['session_token']}:local_pref")),
#                     int(redis_client.get(f"{message['session_token']}:routermac")),
#                 )
#             if message["last_one"] is True:
#                 message = json.dumps(
#                     {
#                         "type": "prefix-withdraw",
#                         "time": redis_client.get(f"{message['session_token']}:time"),
#                     }
#                 )
#                 channel.basic_publish(
#                     exchange="", routing_key="timescale", body=message
#                 )

#         elif message["type"] == "withdraw_T3":
#             rd_obj = get_rd(message["rd"])
#             if rd_obj is None:
#                 add_rd(message["rd"])
#             prefix = get_prefixT3(message["ip"], message["rd"], message["ethernet_tag"])
#             if prefix is not None:
#                 kill_prefixT3(prefix)
#             else:
#                 add_dead_prefixT3(
#                     int(redis_client.get(f"{message['session_token']}:update_id")),
#                     message["rd"],
#                     message["ip"],
#                     message["iplen"],
#                 )
#             if message["last_one"] is True:
#                 message = json.dumps(
#                     {
#                         "type": "prefix-withdraw",
#                         "time": redis_client.get(f"{message['session_token']}:time"),
#                     }
#                 )
#                 channel.basic_publish(
#                     exchange="", routing_key="timescale", body=message
#                 )

#         elif message["type"] == "withdraw_T2":
#             rd_obj = get_rd(message["rd"])
#             if rd_obj is None:
#                 add_rd(message["rd"])
#             prefix = get_prefixT2(message["mac"], message["rd"])
#             if prefix is not None:
#                 kill_prefixT2(
#                     prefix,
#                     int(redis_client.get(f"{message['session_token']}:update_id")),
#                 )
#             if message["last_one"] is True:
#                 message = json.dumps(
#                     {
#                         "type": "prefix-withdraw",
#                         "time": redis_client.get(f"{message['session_token']}:time"),
#                     }
#                 )
#                 channel.basic_publish(
#                     exchange="", routing_key="timescale", body=message
#                 )

#         else:
#             logger.error("Unknown type %r" % message)
#     except Exception:
#         logger.error("Error in callback", sys.exc_info()[0], sys.exc_info()[1])


# channel.basic_consume(queue="postgres", on_message_callback=callback, auto_ack=True)

# channel.start_consuming()

running = True

while running:
    print("im working fine", flush=True)
    time.sleep(20)
