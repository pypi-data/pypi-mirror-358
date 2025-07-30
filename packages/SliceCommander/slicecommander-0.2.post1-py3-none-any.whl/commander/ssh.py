import os
import sys
import glob
import libtmux
import ptyprocess
import threading
import signal
import shlex
from pathlib import Path
from .util import CText


cout = CText()

try:
    tmux = libtmux.Server()
    tenv = os.getenv("TMUX")
    tid = tenv.split(",")[-1]
    tsess = tmux.sessions.get(session_name=tid)
except Exception:
    tsess = None

SSHOPTS = "-t -o StrictHostKeyChecking=no -q"
home = str(Path.home())


def get_pubkeys(path=f"{home}/.ssh"):
    ret = ""
    try:
        for fname in glob.glob(f"{path}/*.pub"):
            f = open(fname, 'r')
            ret += f.read()
    except Exception:
        pass
    return ret


def ssh_pty(obj, params):
    def handler(signum, frame):
        ssh.sendintr()

    def output_reader(proc):
        while True:
            try:
                s = proc.read()
                sys.stdout.write(s)
                sys.stdout.flush()
            except EOFError:
                proc.close()
                break

    sshcmd = obj.get_ssh_command()
    if params:
        sshcmd = " ".join([sshcmd, params])
    ssh = ptyprocess.PtyProcessUnicode.spawn(shlex.split(sshcmd), echo=False)
    signal.signal(signal.SIGINT, handler)

    t = threading.Thread(target=output_reader, args=(ssh,))
    t.start()

    while True:
        try:
            s = sys.stdin.read(1)
            if s == '':
                ssh.sendeof()
            if s == '\f':
                ssh.sendcontrol('l')
                continue
            if ssh.closed:
                break
            ssh.write(s)
        except IOError:
            break
    t.join()


def ssh_tmux(obj, params):
    def tpane(cmd):
        window = tsess.attached_window
        pane = window.split_window(attach=False)
        window.select_layout("even-vertical")
        pane.clear()
        pane.send_keys(cmd)

    cmd = obj.get_ssh_command()
    if params:
        cmd = " ".join([cmd, params])
    tpane(cmd)


def handle_ssh(args, cwc):
    if 'management_ip' not in cwc:
        cout.error("No host or port information on this path")
        return
    if not cwc.get('management_ip') or cwc.get('management_ip') == 'None':
        cout.error("No management IP available for this node")
        return
    obj = cwc.get('_obj', None)
    if not obj:
        cout.error("Could not find Node object in current path")
        return

    params = None
    parts = shlex.split(args)
    if len(parts) > 1:
        params = " ".join(parts[1:])

    if tsess:
        ssh_tmux(obj, params)
    else:
        ssh_pty(obj, params)
