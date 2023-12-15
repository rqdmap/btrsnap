import os, logging, sys
from posixpath import basename
from utils.common import do_cmd, get_base_name, get_local_snap, get_snap_path
from typing import Tuple, List

class SSH():
    def __init__(self, user, host, port, identity_file, use_file: bool):
        self.host = host
        self.port = str(port)
        self.user = user
        self.identity_file = identity_file
        self.use_file = use_file

    def test(self):
        ret, _, _ = do_cmd(f'ssh -i {self.identity_file} -p {self.port} {self.user}@{self.host} exit')
        return ret == 0
    
    def cmd(self, cmd):
        cmd = f"ssh -i {self.identity_file} -p {self.port} {self.user}@{self.host} '{cmd}'"
        return do_cmd(cmd)

    def full_send(self, local_snap, remote_path, dry = True):
        if self.use_file:
            pass
        else:
            cmd = f"btrfs send {local_snap} | ssh -i {self.identity_file} -p {self.port} {self.user}@{self.host} 'btrfs receive {remote_path}'"
            if not dry:
                return do_cmd(cmd)
            logging.warn(cmd)

    def inc_send(self, local_par, local_snap, remote_path, dry = True):
        if self.use_file:
            pass
        else:
            cmd = f"btrfs send -p {local_par} {local_snap} | ssh -i {self.identity_file} -p {self.port} {self.user}@{self.host} 'btrfs receive {remote_path}'"
            if not dry:
                return do_cmd(cmd)
            logging.warn(cmd)

    def get_remote_latest(self, remote_path):
        ret = self.cmd(f'ls {remote_path} | sort -r | head -n 1')
        return ret[1]
    
    def get_remote_diff(self, snap_path, remote_path) -> Tuple[bool, List]:
        local_snaps = get_local_snap(snap_path)

        latest = self.get_remote_latest(remote_path)

        # 不存在 -> 初始化
        if not latest:
            self.cmd(f'mkdir -p {remote_path}')
            return False, local_snaps

        idx = -1
        for i in range(0, len(local_snaps)):
            if local_snaps[i] == latest:
                idx = i
                break

        if idx == -1:
            logging.warn('no matched snapshot, doing full backup')
            return False, local_snaps

        return True, local_snaps[:(idx + 1)]

    def stream_sync(self, snap_path: str, remote_path: str):
        exist, diff_list = self.get_remote_diff(snap_path, remote_path)
        # 按从旧到新排序
        diff_list.reverse()

        if not exist:
            self.full_send(
                snap_path + '/' + diff_list[0],
                remote_path,
                dry = False,
            )

        for i in range(1, len(diff_list)):
            self.inc_send(
                snap_path + '/' + diff_list[i - 1],
                snap_path + '/' + diff_list[i],
                remote_path,
                dry = False,
            )

    def sync(self, sync_list: list):
        for target in sync_list:
            path: str = target['path']
            for rule in target['rules']:
                period = rule['period']
                snap_path = get_snap_path(path, period)
                
                base_name = get_base_name(path)
                remote_path = rule.get('sync', {}).get("path", {})
                if not remote_path:
                    logging.warn(f"remote_path of {snap_path} is empty")
                    continue
                remote_path = remote_path + '/' + base_name + f'/gen/{period}'

                logging.info('snap_path %s' % snap_path)
                logging.info('remote_path %s' % remote_path)

                if self.use_file:
                    pass
                else:
                    self.stream_sync(snap_path, remote_path)



