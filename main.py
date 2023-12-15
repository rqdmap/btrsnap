import os, yaml, re, sys
import logging

from utils.snap import snap
from utils.sync import SSH
logger = logging.getLogger().setLevel(logging.INFO)

# 检查 root 权限
def check_root():
    return os.geteuid() == 0
if not check_root():
    logging.error("must run as root")
    exit()

# 导入配置文件
filename = 'config.yaml'
with open(filename, 'r') as file:
    config = yaml.safe_load(file)

#  替换环境变量
def replace_variables_in_string(string):
    def replace_variables(match):
        variable_name = match.group(1)
        variable_value = os.environ.get(variable_name, '')
        return variable_value
    pattern = r'\$(\w+)'
    replaced_string = re.sub(pattern, replace_variables, string)
    return replaced_string

config = replace_variables_in_string(str(config))
config = eval(config)

def __snap():
    for snap_config in config['snap']:
        path = snap_config['path']
        for rule in snap_config.get('rules', {}):
            try:
                snap(path, rule.get('period'), rule.get('cnt', -1))
            except Exception as e:
                logging.error('snap failed: %s' % e)
                exit()

def __sync():
    # ssh 连接试探
    ssh_key = config['ssh']['identity_file']
    ssh_target = config['ssh']['target']
    ssh = None
    for target in ssh_target:
        _ssh = SSH(
            target.get('user', 'root'),
            target['host'],
            target.get('port', 22),
            ssh_key,
            config['sync']['use_file']
        )
        if _ssh.test():
            ssh = _ssh
            break
        del _ssh

    if ssh is None:
        logging.error('ssh connect failed')
        exit()

    # 远端同步
    sync_list = []
    for snap_config in config['snap']:
        target = dict()
        target['path'] = snap_config['path']
        target['rules'] = []
        for rule in snap_config.get('rules', {}):
            if rule.get('sync', {}):
                target['rules'].append(rule)
        if len(target['rules']) > 0:
            sync_list.append(target)

    ssh.sync(sync_list)


def usage():
    print("""Usage: [sudo] python3 main.py <Options>

Options:
    -h, --help: show this help message and exit
    -s, --snap: take snapshots
    -u, --upload: upload snapshots to remote server
    """)

if len(sys.argv) != 2:
    usage()
    exit()

if sys.argv[1] == '-h' or sys.argv[1] == '--help':
    usage()
    exit()

if sys.argv[1] == '-s' or sys.argv[1] == '--snap':
    __snap()
    exit()

if sys.argv[1] == '-u' or sys.argv[1] == '--upload':
    __sync()
    exit()
