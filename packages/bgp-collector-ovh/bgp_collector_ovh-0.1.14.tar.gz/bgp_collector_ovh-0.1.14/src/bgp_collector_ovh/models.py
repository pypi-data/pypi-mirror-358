from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
    DateTime,
    Text,
    BigInteger,
    text,
    PrimaryKeyConstraint,
    create_engine,
)
from sqlalchemy.dialects.postgresql import JSONB, INET, ENUM
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.sql import func
import logging
import os
import sys

logger = logging.getLogger()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    logger.error("DATABASE_URL environment variable not set.")
    sys.exit(1)

try:
    engine = create_engine(db_url, echo=True)
except Exception as e:
    logger.error(f"Error opening DB: {e}")
    sys.exit(1)

Session = scoped_session(sessionmaker(bind=engine))


@as_declarative()
class Base:
    query = Session.query_property()


Base.metadata.create_all(engine)


class Host(Base):
    __tablename__ = "host"
    id = Column(Integer, primary_key=True)
    hostname = Column(String(40), nullable=False)
    neighbors = relationship("Neighbor", back_populates="host")


class Neighbor(Base):
    __tablename__ = "neighbor"
    id = Column(Integer, primary_key=True)
    fk_host_id = Column(Integer, ForeignKey("host.id"), nullable=False)
    ip = Column(INET, nullable=False)
    asn = Column(Integer, nullable=False)

    host = relationship("Host", back_populates="neighbors")
    messages = relationship("Message", back_populates="neighbor")

    def to_dict(self):
        return {
            "id": self.id,
            "ip": self.ip,
            "host_id": self.fk_host_id,
            "asn": self.asn,
        }


class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True)
    fk_neighbor_id = Column(Integer, ForeignKey("neighbor.id"), nullable=False)
    timestamp = Column(DateTime, default=func.now())
    message_type = Column(String(20), nullable=False)

    neighbor = relationship("Neighbor", back_populates="messages")
    child_update = relationship(
        "Update", uselist=False, passive_deletes=True, cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_identity": "message",
        "polymorphic_on": message_type,
        "with_polymorphic": "*",
    }


class Notification(Message):
    __tablename__ = "notification"
    id = Column(Integer, ForeignKey("message.id", ondelete="CASCADE"), primary_key=True)
    neighbor_state = Column(String(80), nullable=False)
    __mapper_args__ = {"polymorphic_identity": "notification"}


class Update(Message):
    __tablename__ = "update"
    id = Column(Integer, ForeignKey("message.id", ondelete="CASCADE"), primary_key=True)
    type = Column(
        ENUM(
            "withdraw",
            "announce",
            name="update_type",
            create_type=True,
            checkfirst=True,
        ),
        nullable=False,
    )
    family = Column(
        ENUM("inet", "evpn", name="update_family", create_type=True, checkfirst=True),
        nullable=False,
    )

    ts = Column(DateTime(timezone=True), default=func.now())

    prefixes = relationship(
        "Prefix", back_populates="update", foreign_keys="Prefix.fk_update_id"
    )

    __mapper_args__ = {"polymorphic_identity": "update"}


class NextHop(Base):
    __tablename__ = "nexthop"
    id = Column(Integer, primary_key=True)
    ip = Column(INET, nullable=False)
    hostname = Column(String(80), nullable=False)
    code_location = Column(String(10), nullable=False)

    # One-to-many with Prefix
    prefixes = relationship(
        "Prefix", back_populates="nexthop", foreign_keys="Prefix.fk_nexthop_id"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "ip": self.ip,
            "hostname": self.hostname,
            "code_location": self.code_location,
        }


class Prefix(Base):
    __tablename__ = "prefix"
    id = Column(Integer, primary_key=True)
    prefix_type = Column(String(50), default="T5")
    rd_id = Column(Integer, ForeignKey("rd.id"))
    state = Column(String(20), nullable=False, default="active")
    fk_nexthop_id = Column(Integer, ForeignKey("nexthop.id"))
    fk_update_id = Column(Integer, ForeignKey("update.id"), nullable=False)
    fk_1stupdate_id = Column(Integer, ForeignKey("update.id"))

    rd = relationship("RD", back_populates="prefixes")
    nexthop = relationship(
        "NextHop", back_populates="prefixes", foreign_keys=[fk_nexthop_id]
    )
    update = relationship(
        "Update", back_populates="prefixes", foreign_keys=[fk_update_id]
    )
    first_update_rel = relationship(
        "Update", foreign_keys=[fk_1stupdate_id], backref="first_prefix_list"
    )

    __mapper_args__ = {
        "polymorphic_identity": "prefix",
        "polymorphic_on": "prefix_type",
    }

    def to_dict(self):
        return {
            "id": self.id,
            "rd_id": self.rd_id,
            "state": self.state,
            "fk_update_id": self.fk_update_id,
            "fk_1stupdate_id": self.fk_1stupdate_id,
            "fk_nexthop_id": self.fk_nexthop_id,
            "prefix_type": self.prefix_type,
        }


class PrefixT2(Prefix):
    __tablename__ = "prefix_t2"
    id = Column(Integer, ForeignKey("prefix.id"), primary_key=True)
    mac = Column(String(20))

    __mapper_args__ = {"polymorphic_identity": "T2"}

    def to_dict(self):
        base = super().to_dict()
        base.update({"mac": self.mac})
        return base


class PrefixT3(Prefix):
    __tablename__ = "prefix_t3"
    id = Column(Integer, ForeignKey("prefix.id"), primary_key=True)
    ip = Column(INET)
    ethernet_tag = Column(Integer)

    __mapper_args__ = {"polymorphic_identity": "T3"}

    def to_dict(self):
        base = super().to_dict()
        base.update({"ip": self.ip, "ethernet_tag": self.ethernet_tag})
        return base


class PrefixT5(Prefix):
    __tablename__ = "prefix_t5"
    id = Column(Integer, ForeignKey("prefix.id"), primary_key=True)
    ip = Column(INET)
    iplen = Column(Integer)
    aspath = Column(String(120))
    med = Column(Integer)
    localpref = Column(Integer)
    routermac = Column(BigInteger)

    __mapper_args__ = {"polymorphic_identity": "T5"}

    def to_dict(self):
        base = super().to_dict()
        base.update(
            {
                "ip": self.ip,
                "iplen": self.iplen,
                "aspath": self.aspath,
                "med": self.med,
                "localpref": self.localpref,
                "routermac": self.routermac,
            }
        )
        return base


class RD(Base):
    __tablename__ = "rd"
    id = Column(Integer, primary_key=True)
    community = Column(String(20))
    timestamp = Column(DateTime(timezone=True), default=func.now())
    name = Column(String(80))
    type = Column(
        ENUM(
            "real",
            "fictif",
            name="rd_type",
            create_type=True,
            checkfirst=True,
        ),
        nullable=False,
        default="real",
    )

    prefixes = relationship("Prefix", back_populates="rd")

    def to_dict(self):
        return {"id": self.id, "community": self.community}


class SystemState(Base):
    __tablename__ = "system_state"
    time = Column(DateTime(timezone=True), primary_key=True, default=func.now())
    state_description = Column(Text, nullable=False)
    active_neighbors = Column(JSONB, nullable=False)
    total_prefixes = Column(Integer, nullable=False)
    total_updates = Column(Integer, nullable=False)

    prefix_states = relationship(
        "PrefixState",
        back_populates="system_state",
    )

    @classmethod
    def create_hypertable(cls, engine):
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            result = conn.execute(
                text(
                    f"SELECT * FROM timescaledb_information.hypertables "
                    f"WHERE hypertable_name = '{cls.__tablename__}';"
                )
            )
            if not result.fetchone():
                conn.execute(
                    text(f"SELECT create_hypertable('{cls.__tablename__}', 'time');")
                )


class PrefixState(Base):
    __tablename__ = "prefix_state"
    time = Column(DateTime(timezone=True), default=func.now())
    fk_prefix_id = Column(Integer, ForeignKey("prefix.id"), nullable=False)

    fk_system_state_time = Column(
        DateTime(timezone=True), ForeignKey("system_state.time"), nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint("time", "fk_prefix_id"),)

    system_state = relationship(
        "SystemState",
        primaryjoin="PrefixState.fk_system_state_time == SystemState.time",
        back_populates="prefix_states",
        viewonly=True,
    )

    @classmethod
    def create_hypertable(cls, engine):
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            result = conn.execute(
                text(
                    f"SELECT * FROM timescaledb_information.hypertables "
                    f"WHERE hypertable_name = '{cls.__tablename__}';"
                )
            )
            if not result.fetchone():
                conn.execute(
                    text(f"SELECT create_hypertable('{cls.__tablename__}', 'time');")
                )
