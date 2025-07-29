import os
import logging
import click
from pathlib import Path
from rich.logging import RichHandler
from dotenv import load_dotenv
from camera_server import start_camera_server

load_dotenv()

logging.basicConfig(
    level="WARNING",
    format="%(name)s, %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logging.getLogger("urllib3").setLevel(logging.WARNING) # decrease the log level passed through from requests

log = logging.getLogger("rpi-babycam")

def set_log_level(ctx, param, value):
    """ Callback function for click.option to cleanly set log level. """
    log.setLevel(value.upper())

@click.command()
@click.version_option(version="1.0.0", package_name="rpi-babycam")
@click.option(
    "--log-level",
    default="WARNING",
    is_eager=True,
    envvar="LOG_LEVEL",
    callback=set_log_level,
    help="Set log level to one of CRITICAL, ERROR, WARNING, INFO or DEBUG. Default is WARNING."
)
@click.option(
    "--record-motion",
    is_flag=True,
    envvar="RECORD_MOTION",
    help="Enable circular buffer recording on motion detection."
)
@click.option(
    "--bounding-box",
    is_flag=True,
    envvar="BOUNDING_BOX",
    help="Draw bounding boxes around detected motion."
)
@click.option(
    "--sensitivity",
    type=float,
    envvar="SENSITIVITY",
    default=5.0,
    help="Set the motion detection sensitivity. 5.0 by default."
)
@click.option(
    "--mqtt-broker",
    type=str,
    envvar="MQTT_BROKER",
    help="MQTT broker address to publish motion detection events."
)
@click.option(
    "--port",
    type=int,
    envvar="SERVER_PORT",
    default=8000,
    help="HTTP Port for streaming server to bind to. 8000 by default."
)
@click.option(
    "--save-path",
    type=click.Path(path_type=Path),
    envvar="SAVE_PATH",
    default=os.path.expanduser("~/Video/rpi-babycam/"),
    help="Directory to save captured video to, when run with motion recording enabled. ~/Video/rpi-babycam/ by default."
)

def main(log_level, record_motion, bounding_box, sensitivity, mqtt_broker, port, save_path):
    
    # Start the camera server
    start_camera_server(record_motion, bounding_box, sensitivity, mqtt_broker, port, save_path)

if __name__ == "__main__":
    main()
