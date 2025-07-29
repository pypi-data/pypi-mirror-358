import sys
import yaml
import argparse
from bgp_collector_ovh.db_tools.db_queries import get_db_session
from bgp_collector_ovh.models import NextHop

db_session = get_db_session()


def get_args():
    parser = argparse.ArgumentParser(description="Configure NextHop")
    parser.add_argument(
        "-f", dest="file", required=True, help="NextHop Config in YAML format"
    )
    return parser.parse_args()


# Get command line arguments
args = get_args()

# Load YAML file safely
try:
    with open(args.file, "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    print(f"Error: The file '{args.file}' was not found.")
    sys.exit(1)
except yaml.YAMLError as e:
    print(f"Error: Failed to parse YAML file '{args.file}': {e}")
    sys.exit(1)

print("Loaded YAML config:")
print(config)

# Process NextHop entries
try:
    for item in config:
        for nexthop in config[item]:
            # Check if it exists
            query_hop = (
                db_session.query(NextHop).filter_by(ip=nexthop["ip"]).one_or_none()
            )
            if query_hop is not None:
                print(f"NextHop {nexthop['ip']} already exists.")
                continue

            # Add new NextHop entry
            myHop = NextHop(
                ip=nexthop["ip"],
                hostname=nexthop["hostname"],
                code_location=nexthop["code_location"],
            )
            db_session.add(myHop)
            db_session.commit()
            print(f"Added NextHop {nexthop['ip']} successfully.")

except Exception as e:
    print(f"Error while processing NextHop data: {e}")
    sys.exit(1)
