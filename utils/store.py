# Execute command at the file system level

from utils.common import read_from_subdir, sh, green, red

def snap(src: str, dst: str):
    dst_path = '/'.join(dst.split('/')[:-1])
    dst_name = dst.split('/')[-1]

    cmd = f'mkdir -p {dst_path}'
    code, _, err = sh(cmd)
    if code != 0:
        raise Exception(f'mkdir failed: {err}')

    cmd = f'btrfs subvolume snapshot -r {src} {dst_path}/{dst_name}'
    code, _, err = sh(cmd)
    if code != 0:
        raise Exception(f'make snapshot failed: {err}')

def delete_snap(path: str):
    cmd = f'btrfs subvolume delete {path}'
    code, _, err = sh(cmd)
    if code != 0:
        raise Exception(f'mkdir failed: {err}')


def sync_snap_local(src: str, dst: str):
    print(green(f'sync_snap_local {src} {dst}'))
    src_list = read_from_subdir(src)
    dst_list = read_from_subdir(dst)

    prev_snap = None
    idx = -1
    flag = True if len(dst_list) == 0 else False
    if src_list[0] in dst_list:
        for i in range(1, len(src_list)):
            now = src_list[i]
            if now not in dst_list:
                prev_snap = src_list[i - 1]
                idx = i
                flag = True
                break

    if flag is False:
        print("no new snapshot to sync")
        return

    if prev_snap is None:
        prev_snap = src_list[0]
        idx = 1
        print(f'full send {src}/{prev_snap}')
        code, out, err = sh(f"btrfs send {src}/{prev_snap} | btrfs receive {dst}")
        if code != 0:
            print(red(out), red(err), sep='\n')
            return

    for i in range(idx, len(src_list)):
        print(f'incremental send {src}/{prev_snap} -> {src_list[i]}')
        code, out, err = sh(f"btrfs send -p {src}/{prev_snap} {src}/{src_list[i]} | btrfs receive {dst}")
        if code != 0:
            print(red(out), red(err), sep='\n')
            return
        prev_snap = src_list[i]


def sync_snap_remote(src: str, dst: str, connect_config: dict):
    print(green(f'sync_snap_remote {src} {dst}'))
