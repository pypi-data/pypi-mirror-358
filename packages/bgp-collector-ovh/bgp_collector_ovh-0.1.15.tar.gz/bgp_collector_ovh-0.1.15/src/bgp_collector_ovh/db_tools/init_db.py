import logging
import sys
from bgp_collector_ovh.db_tools.db_queries import init_db, create_hypertables
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

init_db()

create_hypertables()
