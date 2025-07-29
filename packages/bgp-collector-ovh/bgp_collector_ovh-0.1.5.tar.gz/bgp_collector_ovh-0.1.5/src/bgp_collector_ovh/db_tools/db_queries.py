import sys
import os
import logging
import logging.config
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound
from bgp_collector_ovh.models import (
    Base,
    Prefix,
    Update,
    PrefixT3,
    PrefixT5,
    PrefixT2,
    Host,
    Neighbor,
    NextHop,
    PrefixState,
    SystemState,
    RD,
)
from bgp_collector_ovh.tools.time_handler import unix_timestamp_to_datetime
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


db_url = os.getenv("DATABASE_URL")
if not db_url:
    logger.error("DATABASE_URL environment variable not set.")
    sys.exit(1)

try:
    engine = create_engine(db_url, echo=True)
except Exception as e:
    logger.error(f"Error opening DB: {e}")
    sys.exit(1)

Session = sessionmaker(bind=engine)


def get_db_session():
    return Session()


def init_db():
    Base.metadata.create_all(engine)
    PrefixState.create_hypertable(engine)


def create_hypertables():
    PrefixState.create_hypertable(engine)


def get_rd(community):

    session = Session()
    try:
        rd = session.query(RD).filter_by(community=community).one_or_none()
        return rd
    except Exception:
        logger.error("Error getting RD")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
    finally:
        session.close()


def add_rd(community, type: str = "real"):
    session = Session()
    try:
        new_rd = RD(community=community, type=type)
        session.add(new_rd)
        session.commit()
        return new_rd
    except Exception:
        logger.error("Error adding RD")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def clean_prefixes(community, ip, iplen):

    session = Session()
    try:
        rd = get_rd(community)
        prefixes = (
            session.query(Prefix)
            .join(Prefix.update)
            .filter(
                and_(
                    Prefix.rd == rd,
                    Update.type == "announce",
                    Prefix.state == "active",
                    Prefix.fk_nexthop_id is not None,
                    Prefix.fk_1stupdate_id is not None,
                    or_(
                        PrefixT3.ip == ip,
                        PrefixT5.ip == ip,
                    ),
                    or_(
                        PrefixT3.iplen == iplen,
                        PrefixT5.iplen == iplen,
                    ),
                ),
            )
        )
        for prefix in prefixes:
            prefix.state = "down"
            session.add(prefix)
        session.commit()
    except Exception:
        logger.error("Error cleaning prefixes")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def get_active_prefixes():
    session = Session()
    try:
        active_prefixes = session.query(Prefix).filter(Prefix.state == "active").all()
        return [row.id for row in active_prefixes]
    except Exception:
        logger.error("Error getting active prefixes")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
    finally:
        session.close()


def get_withdrawed_prefix(withdrawed_prefix_id):
    session = Session()
    try:
        withdrawed_prefix = (
            session.query(Prefix)
            .filter(Prefix.id == withdrawed_prefix_id)
            .one_or_none()
        )
        return withdrawed_prefix.id
    except Exception:
        logger.error("Error getting withdrawed prefixes")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
    finally:
        session.close()


def add_prefix_state(time, prefix_list, system_state_id):
    session = Session()
    datetimetz = unix_timestamp_to_datetime(time)
    try:
        for prefix in prefix_list:
            prefix_state = PrefixState(
                time=datetimetz,
                fk_prefix_id=prefix,
                fk_system_state_time=system_state_id,
            )
            session.add(prefix_state)
        session.commit()
    except Exception:
        logger.error("Error adding prefix state")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def get_neighbors_ids():
    session = Session()
    try:
        neighbors = session.query(Neighbor).all()
        logger.info("Neighbors here:")
        logger.info(f"{neighbors}")
        return [row.id for row in neighbors]
    except Exception:
        logger.error("Error getting neighbors ids")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
    finally:
        session.close()


def get_total_active_prefixs_count():
    session = Session()
    try:
        total_active_prefixs = (
            session.query(Prefix).filter(Prefix.state == "active").count()
        )
        return total_active_prefixs
    except Exception:
        logger.error("Error getting total active prefixes")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
    finally:
        session.close()


def get_total_updates_count():
    session = Session()
    try:
        total_updates = session.query(Update).count()
        return total_updates
    except Exception:
        logger.error("Error getting total updates")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
    finally:
        session.close()


def add_system_state(time, neighbors_list, total_prefixes, total_updates):
    datetimetz = unix_timestamp_to_datetime(time)
    session = Session()
    try:
        system_state = SystemState(
            time=datetimetz,
            state_description="System state",
            active_neighbors=neighbors_list,
            total_prefixes=total_prefixes,
            total_updates=total_updates,
        )
        session.add(system_state)
        session.commit()
        return system_state.time
    except Exception:
        logger.error("Error adding system state")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def get_host(hostname):
    session = Session()
    try:
        host = session.query(Host).filter_by(hostname=hostname).one_or_none()
        return host
    except Exception:
        logger.error("Error getting host")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
    finally:
        session.close()


def add_host(hostname):
    session = Session()
    try:
        existing_host = session.query(Host).filter_by(hostname=hostname).first()
        if existing_host:
            return existing_host.id

        host = Host(hostname=hostname)
        session.add(host)
        session.commit()
        return host.id
    except Exception:
        logger.error("Error adding host")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def get_neighbor(id, ip):
    session = Session()
    try:
        neighbor = session.query(Neighbor).filter_by(fk_host_id=id, ip=ip).one_or_none()
        return neighbor
    except Exception:
        logger.error("Error getting neighbor")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
    finally:
        session.close()


def add_neighbor(id, ip, asn):
    session = Session()
    try:
        neighbor = Neighbor(fk_host_id=id, ip=ip, asn=asn)
        session.add(neighbor)
        session.commit()
        return neighbor.id
    except Exception:
        logger.error("Error adding neighbor")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def add_update(neighbor_id, message_type, type, family, time):
    session = Session()
    try:
        update = Update(
            fk_neighbor_id=neighbor_id,
            message_type=message_type,
            type=type,
            family=family,
            ts=unix_timestamp_to_datetime(time),
        )
        session.add(update)
        session.commit()
        return update.id
    except Exception:
        logger.error("Error adding update")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def get_next_hop(node):
    session = Session()
    try:
        next_hop = session.query(NextHop).filter_by(ip=node).one_or_none()
        return next_hop
    except Exception:
        logger.error("Error getting next hop")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
    finally:
        session.close()


def check_prefixT5(ip, iplen, community):
    session = Session()
    rd = get_rd(community)
    try:
        prefix = (
            session.query(PrefixT5)
            .join(PrefixT5.update)
            .filter(
                and_(
                    PrefixT5.ip == ip,
                    PrefixT5.iplen == iplen,
                    PrefixT5.rd == rd,
                    Update.type == "announce",
                    PrefixT5.state == "active",
                    PrefixT5.fk_nexthop_id is not None,
                    PrefixT5.fk_1stupdate_id is not None,
                )
            )
            .one_or_none()
        )
        return prefix
    except MultipleResultsFound:
        logger.info("prefix active twice:" + community + " " + ip + "/" + str(iplen))
        clean_prefixes(community, ip, iplen)
        logger.info("cleaning done")
        return None
    except Exception:
        logging.error(
            "error querying prefix:" + community + " " + ip + "/" + str(iplen)
        )
        logging.error("error type: {}".format(sys.exc_info()[0]))
        logging.error("error detail: {}".format(sys.exc_info()[1]))
        exit(1)
    finally:
        session.close()


def update_prefixT5(prefix, update):
    session = Session()
    try:
        prefix.fk_update_id = update.id
        prefix.state = "active"
        session.add(prefix)
        session.commit()
    except Exception:
        logger.error("Error updating prefixT5")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def add_prefixT5(
    nexthop_id, update_id, community, ip, iplen, aspath, med, local_pref, routermac
):
    session = Session()
    rd = get_rd(community)
    try:
        new_prefix = PrefixT5(
            fk_nexthop_id=nexthop_id,
            fk_update_id=update_id,
            fk_1stupdate_id=update_id,
            rd_id=rd.id,
            ip=ip,
            iplen=iplen,
            aspath=aspath,
            med=med,
            localpref=local_pref,
            routermac=routermac,
            state="active",
            prefix_type="T5",
        )
        session.add(new_prefix)
        session.commit()
    except Exception:
        logger.error("Error adding prefixT5")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def kill_prefixT5(prefix):
    session = Session()
    try:
        prefix.state = "down"
        session.add(prefix)
        session.commit()
    except Exception:
        logger.error("Error killing prefixT5")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def add_dead_prefixT5(
    update_id, community, ip, iplen, aspath, med, local_pref, routermac
):
    session = Session()
    rd = get_rd(community)
    try:
        new_prefix = PrefixT5(
            fk_update_id=update_id,
            rd_id=rd.id,
            ip=ip,
            iplen=iplen,
            aspath=aspath,
            med=med,
            localpref=local_pref,
            routermac=routermac,
            state="down",
            prefix_type="T5",
        )
        session.add(new_prefix)
        session.commit()
        return new_prefix
    except MultipleResultsFound:
        logger.info("prefix active twice:" + community + " " + ip + "/" + str(iplen))
        clean_prefixes(community, ip, iplen)
        logger.info("cleaning done")
    except Exception:
        logging.error(
            "error withdraw L3 prefix:" + community + " " + ip + "/" + str(iplen)
        )
        logging.error("error type: {}".format(sys.exc_info()[0]))
        logging.error("error detail: {}".format(sys.exc_info()[1]))
        session.rollback()
        exit(1)
    finally:
        session.close()


def add_dead_prefixT3(update_id, community, ip, ethernet_tag):
    session = Session()
    rd = get_rd(community)
    try:
        new_prefix = PrefixT3(
            fk_update_id=update_id,
            rd_id=rd.id,
            ip=ip,
            ethernet_tag=ethernet_tag,
            state="down",
            prefix_type="T3",
        )
        session.add(new_prefix)
        session.commit()
        return new_prefix
    except MultipleResultsFound:
        logger.info("prefix active twice:" + community + " " + ip)
        # clean_prefixes(community, ip, iplen)
        logger.info("cleaning done")
    except Exception:
        logging.error("error withdraw L3 prefix:" + community + " " + ip + "/")
        logging.error("error type: {}".format(sys.exc_info()[0]))
        logging.error("error detail: {}".format(sys.exc_info()[1]))
        session.rollback()
        exit(1)
    finally:
        session.close()


def kill_prefixT3(prefix):
    session = Session()
    try:
        prefix.state = "down"
        session.add(prefix)
        session.commit()
    except Exception:
        logger.error("Error killing prefixT3")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def get_prefixT2(mac, community):
    session = Session()
    rd = get_rd(community)
    logger.info("getting the prefix")
    try:
        prefix = (
            session.query(PrefixT2)
            .join(PrefixT2.update)
            .filter(
                and_(
                    PrefixT2.mac == mac,
                    PrefixT2.rd_id == rd.id,
                    PrefixT2.fk_nexthop_id is not None,
                    PrefixT2.fk_1stupdate_id is not None,
                )
            )
            .one_or_none()
        )

        if prefix is not None:
            logger.info("duplicate")
        else:
            logger.info("new one")

        return prefix

    except MultipleResultsFound:
        logger.info("prefix active twice: %s %s", community, mac)
        return None

    except Exception:
        logger.error("error querying prefix: %s %s", community, mac)
        logger.error("error type: %s", sys.exc_info()[0])
        logger.error("error detail: %s", sys.exc_info()[1])
        exit(1)

    finally:
        session.close()


def update_prefixT2(prefix, update_id):
    session = Session()
    try:
        prefix.fk_update_id = update_id
        if prefix.state == "down":
            prefix.state = "active"
        session.add(prefix)
        session.commit()
    except Exception:
        logger.error("Error updating prefixT2")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def kill_prefixT2(prefix, update_id: None):
    session = Session()
    try:
        prefix.state = "down"
        if update_id is not None:
            prefix.fk_update_id = update_id
        session.add(prefix)
        session.commit()
    except Exception:
        logger.error("Error killing prefixT2")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def delete_prefixT2(prefix):
    session = Session()
    try:
        if not prefix:
            return

        old_update = session.query(Update).get(prefix.fk_update_id)
        first_update = session.query(Update).get(prefix.fk_1stupdate_id)

        session.delete(prefix)
        session.commit()

        if old_update is not None and first_update is not None:
            if old_update.id != first_update.id:
                if first_update.prefix == [] and first_update.first_prefix == []:
                    session.delete(first_update)
                if old_update.prefix == [] and old_update.first_prefix == []:
                    session.delete(old_update)
                session.commit()

        logger.info("Successfully deleted PrefixT2 with id %d", prefix.id)
    except Exception:
        logger.error("Error withdrawing L2 prefix: %s/%s", prefix.rd, prefix.mac)
        logger.error("Error type: %s", sys.exc_info()[0])
        logger.error("Error details: %s", sys.exc_info()[1])
        session.rollback()
    finally:
        session.close()


def add_prefixT2(nexthop_id, update_id, community, mac):
    session = Session()
    rd = get_rd(community)
    try:
        new_prefix = PrefixT2(
            fk_nexthop_id=nexthop_id,
            fk_update_id=update_id,
            fk_1stupdate_id=update_id,
            rd_id=rd.id,
            mac=mac,
            state="active",
            prefix_type="T2",
        )
        session.add(new_prefix)
        session.commit()
    except MultipleResultsFound:
        logging.error("prefix active twice:" + community + "/" + mac)
    except Exception:
        logging.error("error adding L2 prefix:" + community + "/" + mac)
        logging.error("error type: {}".format(sys.exc_info()[0]))
        logging.error("error detail: {}".format(sys.exc_info()[1]))
        exit(1)
    finally:
        session.close()


def get_prefixT3(ip, ethernet_tag, community):
    session = Session()
    rd = get_rd(community)
    try:
        prefix = (
            session.query(PrefixT3)
            .join(PrefixT3.update)
            .filter(
                and_(
                    PrefixT3.ip == ip,
                    PrefixT3.ethernet_tag == ethernet_tag,
                    PrefixT3.rd_id == rd.id,
                    Update.type == "announce",
                    PrefixT3.state == "active",
                    PrefixT3.fk_nexthop_id is not None,
                    PrefixT3.fk_1stupdate_id is not None,
                )
            )
            .one_or_none()
        )
        return prefix
    except MultipleResultsFound:
        # logger.info("prefix active twice:" + community + " " + ip + "/" + str(iplen))
        # clean_prefixes(community, ip, iplen)
        logger.info("cleaning done")
        return None
    except Exception:
        # logging.error(
        #     "error querying prefix:" + community + " " + ip + "/" + str(iplen)
        # )
        logging.error("error type: {}".format(sys.exc_info()[0]))
        logging.error("error detail: {}".format(sys.exc_info()[1]))
        exit(1)
    finally:
        session.close()


def update_prefixT3(prefix, update):
    session = Session()
    try:
        prefix.fk_update_id = update.id
        session.commit()
    except Exception:
        logger.error("Error updating prefixT3")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def add_prefixT3(nexthop_id, update_id, community, ip, ethernet_tag):
    session = Session()
    rd = get_rd(community)
    try:
        new_prefix = PrefixT3(
            fk_nexthop_id=nexthop_id,
            fk_update_id=update_id,
            fk_1stupdate_id=update_id,
            rd_id=rd.id,
            ip=ip,
            ethernet_tag=ethernet_tag,
            state="active",
            prefix_type="T3",
        )
        session.add(new_prefix)
        session.commit()
    except Exception:
        logger.error("Error adding prefixT3")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
    finally:
        session.close()


def check_system_state(time):
    session = Session()
    system_state_id = unix_timestamp_to_datetime(time)
    try:
        system_state = (
            session.query(SystemState).filter_by(time=system_state_id).one_or_none()
        )
        if system_state is not None:
            return system_state.time
        return None
    except Exception:
        logger.error("Error checking system state")
        logger.error(f"Error type: {sys.exc_info()[0]}")
        logger.error(f"Error detail: {sys.exc_info()[1]}")
        session.rollback()
