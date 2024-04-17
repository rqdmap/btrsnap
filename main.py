import os
import sys
import re
import yaml
import logging
from typing import List

from utils.snap import SnapItem
from utils.config import Config
from utils.sync import Sync
logger = logging.getLogger().setLevel(logging.INFO)


def usage():
    print("""Usage: [sudo] python3 main.py <Options>

Options:
    -h, --help: show this help message and exit
    -s, --snap: take snapshots
    -r, --roll: roll snap list
    -u, --upload: upload snapshots to remote server
    """)


if not os.geteuid() == 0:
    logging.error("must run as root")
    exit()


config = Config("config.yaml")
snap_items: List[SnapItem] = [SnapItem(i) for i in config['snap']]
sync = Sync(config['sync'])

if len(sys.argv) != 2 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
    usage()
    exit()

if sys.argv[1] == '-s' or sys.argv[1] == '--snap':
    for item in snap_items:
        item.snap()

if sys.argv[1] == '-r' or sys.argv[1] == '--roll':
    for item in snap_items:
        item.roll()

if sys.argv[1] == '-u' or sys.argv[1] == '--upload':
    for item in snap_items:
        sync.update(item)

