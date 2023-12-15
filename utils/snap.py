import logging
import os
from datetime import datetime
from utils.common import do_cmd, get_base_name, get_local_snap, get_snap_path

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

# 检查目录下的最新快照时间是否已经超过周期
def check_period(snap_path: str, period: str):
    if not os.path.isdir(snap_path):
        return True

    snaps = sorted(os.listdir(snap_path))
    snaps.reverse()

    if len(snaps) == 0:
        return True

    period_val = format_period(period)
    last_snap_time = snaps[0].split('_')[-1]
    dt = datetime.strptime(last_snap_time, "%Y%m%d%H%M%S")
    res = datetime.now() - dt
    if res.total_seconds() > period_val:
        return True
    return False

def snap(path: str, period: str, cnt = -1):
    # 基本校验
    if not path.startswith('/'):
        raise Exception(f'path "{path}" must be absolute')
    if path.endswith('/'):
        path = path[:-1]
    if path.count('/') < 2:
        raise Exception(f'path "{path}" must have secondary directory')

    base_path = '/'.join(path.split('/')[:-1])
    snap_path = get_snap_path(path, period)

    # 时间周期检查
    if not check_period(snap_path, period):
        logging.info(f'period {period} on {base_path} not reached')
        return 

    # 快照
    base_name = get_base_name(path)
    snap_name = f'{base_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}'

    cmd = f'mkdir -p {snap_path}'
    do_cmd(cmd)

    cmd = f'btrfs subvolume snapshot -r {path} {snap_path}/{snap_name}'
    do_cmd(cmd)

    if cnt == -1:
        return 

    # 检查目录下快照数量, 删除多余的旧快照
    snaps = get_local_snap(snap_path)
    if len(snaps) == 0:
        raise Exception(f'snap_path "{snap_path}" is empty')
    for i in range(cnt, len(snaps)):
        cmd = f'btrfs subvolume delete {snap_path}/{snaps[i]}'
        do_cmd(cmd)

