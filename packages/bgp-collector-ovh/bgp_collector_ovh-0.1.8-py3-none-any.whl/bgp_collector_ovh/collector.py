import sys
import json
import logging
import logging.config
import pika
import redis
import uuid
from bgp_collector_ovh.db_tools.db_queries import get_host, get_next_hop
import os
from pathlib import Path


try:
    default_path = Path(__file__).resolve().parent / "logging.conf"

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


def generate_session_token():
    return str(uuid.uuid4())


def write_raw(packet):
    raw_file = open("/tmp/bgp_raw.json", "a")

    for p in packet:
        raw_file.write(p)
        raw_file.write(";")
        if p == "neighbor":
            for n in packet[p]:
                raw_file.write(n)
                raw_file.write(";")
    raw_file.write("\n")

    raw_file.close()


# RabbitMQ Producer
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()

# Declare Queue
channel.queue_declare(queue="postgres")

Running = True
while Running:

    session_token = generate_session_token()

    raw_input = sys.stdin.readline().strip()

    # Check if input is empty
    if not raw_input:
        # logger.warning("Received empty input from stdin. Skipping...")
        continue

    try:
        data = json.loads(raw_input)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON received: {raw_input} | Error: {e}")
        continue

    time = data["time"]
    redis_client.setex(f"{session_token}:time", 300, time)
    # Check Host
    host = get_host(data["host"])
    # rabbitmq host
    if host is None:
        message = json.dumps(
            {"type": "host", "hostname": data["host"], "session_token": session_token}
        )
        channel.basic_publish(exchange="", routing_key="postgres", body=message)

    if "neighbor" in data:
        # Check Neighbor
        message = json.dumps(
            {
                "type": "neighbor",
                "ip": data["neighbor"]["address"]["peer"],
                "asn": data["neighbor"]["asn"]["peer"],
                "host_id": host.id if host else None,
                "hostname": data["host"],
                "session_token": session_token,
            }
        )
        channel.basic_publish(exchange="", routing_key="postgres", body=message)
        # Proceed with the message
        if "type" in data:
            if data["type"] == "update":
                # Create a new entry:
                if "announce" in data["neighbor"]["message"]["update"]:
                    update_type = "announce"
                elif "withdraw" in data["neighbor"]["message"]["update"]:
                    update_type = "withdraw"

                if "l2vpn evpn" in data["neighbor"]["message"]["update"][update_type]:
                    family = "evpn"
                # rabbitmq update
                message = json.dumps(
                    {
                        "type": "update",
                        "update_type": update_type,
                        "family": family,
                        "session_token": session_token,
                    }
                )
                channel.basic_publish(exchange="", routing_key="postgres", body=message)
                if update_type == "announce":
                    # Proceed with the prefix attributes
                    routermac = None
                    if "as-path" in data["neighbor"]["message"]["update"]["attribute"]:
                        aspath = data["neighbor"]["message"]["update"]["attribute"][
                            "as-path"
                        ]
                        # Get list len
                        if len(aspath) > 20:
                            aspath = "too long"
                    else:
                        aspath = ""
                    if (
                        "local-preference"
                        in data["neighbor"]["message"]["update"]["attribute"]
                    ):
                        local_pref = int(
                            data["neighbor"]["message"]["update"]["attribute"][
                                "local-preference"
                            ]
                        )
                    else:
                        local_pref = 0
                    if "med" in data["neighbor"]["message"]["update"]["attribute"]:
                        med = int(
                            data["neighbor"]["message"]["update"]["attribute"]["med"]
                        )
                    else:
                        med = 0
                    if (
                        "extended-community"
                        in data["neighbor"]["message"]["update"]["attribute"]
                    ):
                        for extcomm in data["neighbor"]["message"]["update"][
                            "attribute"
                        ]["extended-community"]:
                            if extcomm["string"] == "":
                                routermac = extcomm["value"]
                else:
                    med = 0
                    local_pref = 0
                    aspath = ""
                    routermac = 0
                if routermac is None:
                    routermac = ""
                redis_client.setex(f"{session_token}:med", 300, med)
                redis_client.setex(f"{session_token}:local_pref", 300, local_pref)
                redis_client.setex(f"{session_token}:routermac", 300, routermac)
                aspath_string = ",".join(map(str, aspath))
                redis_client.setex(f"{session_token}:aspath", 300, aspath_string)
                # Get prefix nexthop
                for family in data["neighbor"]["message"]["update"][update_type]:
                    if update_type == "announce":
                        for node in data["neighbor"]["message"]["update"][update_type][
                            family
                        ]:
                            # Lookfor Nexthop
                            nexthop = get_next_hop(node)
                            if nexthop is None:
                                logger.info(
                                    "can't find node {} please add it to DB".format(
                                        node
                                    )
                                )
                                continue
                            redis_client.setex(
                                f"{session_token}:nexthop_id", 300, nexthop.id
                            )

                            # Parse each prefix_entry of the announce
                            for index, prefix_entry in enumerate(
                                data["neighbor"]["message"]["update"][update_type][
                                    family
                                ][node]
                            ):
                                last_one = False
                                if index == (
                                    len(
                                        data["neighbor"]["message"]["update"][
                                            update_type
                                        ][family][node]
                                    )
                                    - 1
                                ):
                                    last_one = True

                                if prefix_entry["code"] == 5:
                                    # IP Prefix Type
                                    if "iplen" in prefix_entry:
                                        iplen = int(prefix_entry["iplen"])
                                    else:
                                        iplen = 0
                                    ip = prefix_entry["ip"]
                                    rd = prefix_entry["rd"]

                                    message = json.dumps(
                                        {
                                            "type": "prefixT5",
                                            "ip": ip,
                                            "iplen": iplen,
                                            "rd": rd,
                                            "session_token": session_token,
                                            "last_one": last_one,
                                        }
                                    )
                                    channel.basic_publish(
                                        exchange="",
                                        routing_key="postgres",
                                        body=message,
                                    )

                                elif prefix_entry["code"] == 2:
                                    # L2 mac
                                    rd = prefix_entry["rd"]
                                    mac = prefix_entry["mac"]
                                    message = json.dumps(
                                        {
                                            "type": "prefixT2",
                                            "mac": mac,
                                            "rd": rd,
                                            "session_token": session_token,
                                            "last_one": last_one,
                                        }
                                    )
                                    channel.basic_publish(
                                        exchange="",
                                        routing_key="postgres",
                                        body=message,
                                    )

                                if prefix_entry["code"] == 3:
                                    # IP Prefix Type
                                    ip = prefix_entry["ip"]
                                    rd = prefix_entry["rd"]
                                    ethernet_tag = prefix_entry["ethernet-tag"]

                                    message = json.dumps(
                                        {
                                            "type": "prefixT3",
                                            "ip": ip,
                                            "rd": rd,
                                            "ethernet_tag": ethernet_tag,
                                            "session_token": session_token,
                                            "last_one": last_one,
                                        }
                                    )
                                    channel.basic_publish(
                                        exchange="",
                                        routing_key="postgres",
                                        body=message,
                                    )

                                else:
                                    logger.info(
                                        "received prefix code {}".format(
                                            prefix_entry["code"]
                                        )
                                    )
                                    # write_raw(data)

                    else:
                        # Withdraw
                        last_one = False
                        for index, prefix_entry in enumerate(
                            data["neighbor"]["message"]["update"][update_type][family]
                        ):
                            if index == (
                                len(
                                    data["neighbor"]["message"]["update"][update_type][
                                        family
                                    ]
                                )
                                - 1
                            ):
                                last_one = True
                            if prefix_entry["code"] == 5:
                                # IP Prefix Type
                                if "iplen" in prefix_entry:
                                    iplen = int(prefix_entry["iplen"])
                                else:
                                    iplen = 0
                                ip = prefix_entry["ip"]
                                rd = prefix_entry["rd"]
                                message = json.dumps(
                                    {
                                        "type": "withdraw_T5",
                                        "ip": ip,
                                        "rd": rd,
                                        "iplen": iplen,
                                        "session_token": session_token,
                                        "last_one": last_one,
                                    }
                                )
                                channel.basic_publish(
                                    exchange="", routing_key="postgres", body=message
                                )

                            elif prefix_entry["code"] == 2:
                                # L2 Prefix Withdraw
                                rd = prefix_entry["rd"]
                                mac = prefix_entry["mac"]
                                message = json.dumps(
                                    {
                                        "type": "withdraw_T2",
                                        "rd": rd,
                                        "mac": mac,
                                        "session_token": session_token,
                                        "last_one": last_one,
                                    }
                                )
                                channel.basic_publish(
                                    exchange="", routing_key="postgres", body=message
                                )

                            elif prefix_entry["code"] == 3:
                                # IP Prefix Type
                                if "iplen" in prefix_entry:
                                    iplen = int(prefix_entry["iplen"])
                                else:
                                    iplen = 0
                                ip = prefix_entry["ip"]
                                rd = prefix_entry["rd"]
                                message = json.dumps(
                                    {
                                        "type": "withdraw_T3",
                                        "ip": ip,
                                        "rd": rd,
                                        "iplen": iplen,
                                        "session_token": session_token,
                                        "last_one": last_one,
                                    }
                                )
                                channel.basic_publish(
                                    exchange="", routing_key="postgres", body=message
                                )

    else:
        write_raw(data)

connection.close()
