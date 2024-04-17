import logging
import os
from datetime import datetime

from utils.common import confirm, format_period, subvolume_to_subdir, read_from_subdir, green, red
import utils.store as store


class SnapItem():
    # Read config from yaml
    def __init__(self, config: dict):
        self.name = config['name']
        self.local_path = config['path']                    # Raw subvolumn path
        self.rules = config['rules']
        self.subdir = subvolume_to_subdir(self.local_path)  # Snapshots directory
        self.sync_rules = config['sync']

    # Snap locally
    def snap(self):
        name = self.name + '_' + datetime.now().strftime("%Y%m%d%H%M%S")
        store.snap(self.local_path, self.subdir + '/' + name)

    # Rolltate local snap list
    def roll(self):
        # Traverse from the latest to the oldest
        snaps = read_from_subdir(self.subdir, reverse=True)
        valid = [False for _ in range(len(snaps))]

        for rule in self.rules:
            period = rule['period']
            assert period
            period = format_period(rule['period'])
            cnt = rule.get('cnt', 0x3f3f3f3f)

            prev = snaps[0]
            valid[0] = True
            cnt -= 1

            for i in range(0, len(snaps)):
                if i == 0 or cnt <= 0:
                    continue

                now = snaps[i]
                now_time = datetime.strptime(now.split('_')[-1], "%Y%m%d%H%M%S")
                pre_time = datetime.strptime(prev.split('_')[-1], "%Y%m%d%H%M%S")

                if (pre_time - now_time).total_seconds() > period:
                    prev = now
                    valid[i] = True
                    cnt -= 1

        res = list(zip(snaps, valid))
        display_roll_res(res)

        if confirm():
            for i in filter(lambda x: not x[1], res):
                store.delete_snap(self.subdir + '/' + i[0])


def display_roll_res(res):
    def col():
        return '        |'

    def row():
        return '         ---'

    length = len(res)
    print(green(res[0][0]))

    for i in range(1, length):
        reserved = res[i][1]
        print(col())

        now = res[i][0]

        latest_time = datetime.strptime(res[0][0].split('_')[-1], "%Y%m%d%H%M%S")
        now_time = datetime.strptime(now.split('_')[-1], "%Y%m%d%H%M%S")
        difference = latest_time - now_time
        days = difference.days
        hours, remainder = divmod(difference.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        formatted_difference = f"{days} days {hours} hours {minutes} minutes"

        if reserved:
            print(green(now), formatted_difference, "ago")
        else:
            print(row(), red(now), formatted_difference, "ago")
    print()
