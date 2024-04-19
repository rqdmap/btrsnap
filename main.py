import os
import sys
import re
import yaml
import logging
from typing import List

from utils.common import green, yellow
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


print("Select target snap items to perform action:")
for i in range(0, len(snap_items)):
    print("\t{i} => {name} at {path}".format(i=i, name=snap_items[i].name, path=snap_items[i].local_path))

target_list = list(range(0, len(snap_items)))
print(f'\033[33m[WARN] Input index separated by comma (default: {", ".join(map(lambda x: str(x), target_list))}): \033[0m', end='')
ans = input()
if ans:
    try:
        target_list = list(map(lambda x: int(x), ans.split(',')))
    except Exception as e:
        logging.error(e)
        exit(1)


print(yellow("\t=> Selected snap items:"), yellow(", ".join(map(lambda x: str(x), target_list))))
snap_items = [snap_items[i] for i in target_list]

if sys.argv[1] == '-s' or sys.argv[1] == '--snap':
    for item in snap_items:
        item.snap()

if sys.argv[1] == '-r' or sys.argv[1] == '--roll':
    for item in snap_items:
        item.roll()

if sys.argv[1] == '-u' or sys.argv[1] == '--upload':
    for item in snap_items:
        if item.sync_rules:
            sync.update(item)

