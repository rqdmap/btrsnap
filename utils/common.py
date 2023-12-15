import sys
import functools
import os
import logging
import subprocess

def do_cmd(cmd: str):
    logging.info(cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def get_snap_path(path: str, period: str):
    base_path = '/'.join(path.split('/')[:-1])
    return base_path + f'/snapshots/gen/{period}'

def get_base_name(path: str):
    return path.split('/')[-2]

# 按照从新到旧的顺序排序
def get_local_snap(path: str):
    if not os.path.isdir(path):
        raise Exception(f'snap_path "{path}" is not directory')
    snaps = sorted(os.listdir(path))
    snaps.reverse()
    return snaps

