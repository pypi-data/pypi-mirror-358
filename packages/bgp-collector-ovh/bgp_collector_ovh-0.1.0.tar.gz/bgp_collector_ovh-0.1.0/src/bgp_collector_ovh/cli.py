import subprocess
import sys
import click
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


@click.command()
@click.option(
    "--nexthop-config",
    default=str(BASE_DIR / "scripts" / "nexthop_config.yaml"),
    help="Path to nexthop config YAML file",
)
def run(nexthop_config):
    """
    Start the BGP collector components:
    - init_db.py
    - add_nexthop.py
    - postgres_worker.py
    - timescale_worker.py
    """
    try:
        click.echo("Initializing database...")
        subprocess.run(
            [sys.executable, str(BASE_DIR / "db_tools" / "init_db.py")], check=True
        )

        click.echo("Adding nexthops...")
        subprocess.Popen(
            [
                sys.executable,
                str(BASE_DIR / "scripts" / "add_nexthop.py"),
                "-f",
                nexthop_config,
            ]
        )

        click.echo("Starting postgres worker...")
        subprocess.Popen(
            [sys.executable, str(BASE_DIR / "services" / "postgres_worker.py")]
        )

        click.echo("Starting timescale worker...")
        subprocess.Popen(
            [sys.executable, str(BASE_DIR / "services" / "timescale_worker.py")]
        )

        click.echo("BGP collector started successfully.")

    except subprocess.CalledProcessError as e:
        click.echo(f"Error while running command: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    run()
