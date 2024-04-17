import os
import logging
import subprocess

#
# def sh(cmd: str):
#     logging.info(cmd)
#     return 0, '', ''


def sh(cmd: str):
    logging.info(cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def subvolume_to_subdir(s: str):
    return '/'.join(s.split('/')[:-1]) + '/snapshots/gen'


def subdir_to_subvolume(s: str):
    pass


def read_from_subdir(path: str, reverse=False):
    if not os.path.isdir(path):
        raise Exception(f'snap_path "{path}" is not directory')
    snaps = sorted(os.listdir(path))
    if reverse:
        snaps.reverse()
    return snaps


# 将 s, m, h, d 等单位统一转换为秒
def format_period(period: str) -> int:
    if period[-1] == 's':
        return int(period[:-1])
    elif period[-1] == 'm':
        return int(period[:-1]) * 60
    elif period[-1] == 'h':
        return int(period[:-1]) * 60 * 60
    elif period[-1] == 'd':
        return int(period[:-1]) * 60 * 60 * 24

    raise Exception('period must be in m, h, d')


def confirm():
    print('\033[33m[WARN] Continue? (y/n) \033[0m', end='')
    ans = input()
    if ans.lower() == 'n':
        exit(0)
    return True

def green(s):
    return '\033[32m' + s + '\033[0m'

def red(s):
    return '\033[31m' + s + '\033[0m'
