#!/usr/bin/env python3

'''
Usage:
  slice-commander [options]
  slice-commander [options] show
  slice-commander [options] renew DAYS
  slice-commander [options] delete
  slice-commander (-h | --help)

Options:
  -h --help
  -s SLICE --slice SLICE
  --prefetch
'''

from docopt import docopt
import cmd
import json
import pprint
import signal
import shlex
from datetime import datetime, timezone, timedelta

from .util import Util, col, CText, wrap
from .ssh import get_pubkeys, handle_ssh
from .spinner import Spinner


SYNC_ITEMS = list()
FABLIB_ITEMS = ["verify_and_configure", "show_config", "save_config"]
LIST_ITEMS = ["facility_ports", "sites", "hosts", "links", "artifacts"]
SHOW_ITEMS = ["keys", "components", "nodes", "networks", "interfaces"]
SHOW_ITEMS.extend(LIST_ITEMS)
SKIP_ATTRS = ["_obj", "_error", "_shallow"]
SLICE_GETTERS = ["components",
                 "nodes",
                 "interfaces",
                 "networks"]

cout = CText()


class ConfigurationError(Exception):
    def __init__(self, num, key, dir_list):
        self.num = num
        self.key = key
        self.dir = "/" + "/".join(dir_list)

    def __str__(self):
        return f"No such path through config at pos: {self.num} {self.key} in {self.dir}"


class FabricCmd(cmd.Cmd):
    prompt_fmt = "fabric-sc {}> "

    def __init__(self, slice_name=None, prefetch=False):
        from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager

        self.prompt = FabricCmd.prompt_fmt.format('(/)')
        self.config = dict()
        self.prefetch = prefetch
        self.cwc = self.config
        self.cwd_list = []
        self.curr = None
        self.util = Util()
        self.pp = pprint.PrettyPrinter(indent=1, width=80, depth=None, stream=None)
        try:
            self.fablib = fablib_manager()
            self.fablib.show_config()
        except Exception as e:
            print(f"Init Error: {repr(e)}, check fabric_rc!")
            exit(-1)
        self._init_slices(slice_name)
        cmd.Cmd.__init__(self)

    def _init_slice(self, slice_name, shallow=False):
        try:
            s = self.fablib.get_slice(name=slice_name)
        except Exception as e:
            cout.error(f"{e}")
            return
        js = json.loads(s.show(output='json', quiet=True))
        js['_obj'] = s
        js['_error'] = False
        name = js['name']
        self.config[name] = js
        if shallow:
            js['_shallow'] = True
            return self.config[name]

        with Spinner():
            for prop in SLICE_GETTERS:
                if not getattr(self, prop, False):
                    setattr(self, prop, dict())
                _fn_name = f"get_{prop}"
                _fn = getattr(s, _fn_name)
                res = _fn()
                new = list()
                for r in res:
                    js = json.loads(r.show(output='json', quiet=True))
                    js['_obj'] = r
                    new.append(js)
                    propkey = f"{name}/{js.get('name', None)}"
                    pdict = getattr(self, prop)
                    pdict.update({propkey: js})
                self.config[name][prop] = new
                # XXX build a sliver entry
                self.config[name]["slivers"] = list()
                for sv in s.get_slivers():
                    err = True if sv.state.lower() in ["error", "closed"] else False
                    if err:
                        self.config[name]['_error'] = True
                    sliver = {"name": sv.sliver_id,
                              "notice": sv.notice,
                              "type": sv.sliver_type,
                              "state": sv.state,
                              "sliver": sv.sliver,
                              "_error": err
                              }
                    self.config[name]["slivers"].append(sliver)
        return self.config[name]

    def _init_slices(self, slice_name=None):
        try:
            print(col.WARNING + "Getting slices..." + col.ENDC, end='')
            slices = json.loads(self.fablib.list_slices(output='json', quiet=True))
            for s in slices:
                name = s.get('name')
                if slice_name and slice_name != name:
                    continue
                print(name+"..", end='')
                if self.prefetch:
                    self._init_slice(s['name'])
                else:
                    self.config[name] = dict()
            print(f"done [{len(slices)} slices]")
        except Exception as e:
            import traceback
            traceback.print_exc()
            cout.error(f"Slice Load Error: {repr(e)}")

    def _cleanup(self):
        pass

    def do_renew(self, args):
        'Renew one or more slices: renew <days> [SliceName1, SliceName2, ...]'
        from fabrictestbed_extensions.fablib.fablib import Slice
        usage = "Usage: renew <days> [SliceName1, SliceName2, ...]"
        if not len(args):
            cout.error("Can only renew slices, or specify slice name.")
            return
        parts = shlex.split(args)
        if len(parts) < 2:
            obj = self.cwc.get("_obj", None)
            if obj and isinstance(obj, Slice):
                try:
                    days = int(parts[0])
                except Exception:
                    cout.error(usage)
                    return
                parts = [obj.get_name()]
            else:
                cout.error(usage)
                return
        else:
            try:
                days = int(parts[0])
            except Exception:
                cout.error(usage)
                return
            parts = parts[1:]
        end_date = (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S %z")
        for p in parts:
            if p not in self.config.keys():
                cout.error(f"Slice \"{p}\" not found")
                continue
            else:
                obj = self.config.get(p)
                if not obj:
                    obj = self._init_slice(p, shallow=True)
                try:
                    obj = obj['_obj']
                    obj.renew(end_date)
                    obj.update()
                    cout.warn(f"Lease End (UTC) : {obj.get_lease_end()}")
                except Exception as e:
                    cout.error(f"{e}")

    def complete_renew(self, text, line, b, e):
        parts = line.split(" ")
        return [wrap(x) for x in self.config.keys() if x.startswith(parts[-1])]

    def do_delete(self, args):
        'Delete one or more slices: delete [SliceName1, SliceName2, ...] [*]'
        parts = shlex.split(args)
        if not len(parts):
            cout.error("Must specify at least one slice name.")
            return
        if "*" in parts:
            msg = "Really delete ALL SLICES? (y/N): "
            parts = [*self.config.keys()]
        else:
            msg = "Really delete? (y/N): "
        try:
            r = input(msg)
            if r.lower() != "y":
                return
        except Exception:
            print("\n")
            return
        for p in parts:
            if p not in self.config.keys():
                cout.error(f"Slice \"{p}\" not found")
                continue
            else:
                obj = self.config.get(p)
                if not obj:
                    obj = self._init_slice(p, shallow=True)
                try:
                    obj = obj['_obj']
                    obj.delete()
                    del self.config[p]
                    cout.warn(f"Slice \"{p}\" deleted.")
                except Exception as e:
                    cout.error(f"{e}")

    def complete_delete(self, text, line, b, e):
        parts = line.split(" ")
        return [wrap(x) for x in self.config.keys() if x.startswith(parts[-1])]

    def do_sync(self, args):
        'Update all or specified slice information from CF: sync [slice_name]'
        if len(args) > 1:
            slice = args.split(" ")[0]
        else:
            slice = None
        self._init_slices(slice)
        self.do_cd("/")

    def complete_sync(self, text, line, b, e):
        return [x[b-5:] for x in SYNC_ITEMS if x.startswith(line[5:])]

    def do_fablib(self, args):
        'Execute various fablib methods'
        if not len(args):
            return
        parts = args.split(" ")
        fname = parts[0]
        if fname in FABLIB_ITEMS:
            _fn = getattr(self.fablib, fname)
            _fn()

    def complete_fablib(self, text, line, b, e):
        return [x[b-7:] for x in FABLIB_ITEMS if x.startswith(line[7:])]

    def do_ssh(self, args):
        'SSH to a node: ssh [node_path] [SSH parameters]\nThe ssh command can also be used within a node leaf'
        parts = shlex.split(wrap(args))
        if len(parts) and parts[0]:
            try:
                (sname, node) = parts[0].split("/")
                self.do_cd(f"/{sname}/nodes/{node}")
            except Exception:
                cout.error("Node not found.")
                return
        handle_ssh(wrap(args), self.cwc)

    def complete_ssh(self, text, line, b, e):
        return [x[b-4:] for x in self.nodes.keys() if x.startswith(line[4:])]

    def do_show(self, args):
        'Show top-level information on available resources: show <item>\nUse tab-completion to view possible options'
        if not len(args):
            return
        parts = args.split(" ")
        if parts[0] == "keys":
            cout.info(get_pubkeys())
        if parts[0] in LIST_ITEMS:
            key = f".{parts[0]}"
            if not self.config.get(key, None):
                with Spinner():
                    _fn_name = f"list_{parts[0]}"
                    _fn = getattr(self.fablib, _fn_name)
                    sobj = _fn(output='json', quiet=True)
                    data = json.loads(sobj)
                    self.config[key] = data
            else:
                data = self.config[key]
            if len(data) and data[0].get('name'):
                cout.info("\n".join([f"{n['name']}" for n in data]))
            else:
                cout.info("\n".join([f"{n['title']}" for n in data]))
        elif parts[0] in SHOW_ITEMS:
            pdict = getattr(self, parts[0], [])
            for p in pdict:
                cout.info(p)

    def complete_show(self, text, line, b, e):
        return [x[b-5:] for x in SHOW_ITEMS if x.startswith(line[5:])]

    def emptyline(self):
        pass

    def do_cd(self, path):
        'Change the current level of view of the config: cd [key]'
        if path == "" or path == "~" or path[0] == "/":
            new_wd_list = path[1:].split("/")
        else:
            new_wd_list = self.cwd_list + path.split("/")
        try:
            cwc, new_wd_list = self._conf_for_list(new_wd_list)
            if (not cwc and path in self.config.keys()) or (cwc and cwc.get("_shallow")):
                self._init_slice(path)
                cwc, new_wd_list = self._conf_for_list(new_wd_list)
        except ConfigurationError as e:
            cout.error(str(e))
            return
        self.cwd_list = new_wd_list
        self.cwc = cwc
        path = "/" + "/".join(self.cwd_list)
        self.prompt = FabricCmd.prompt_fmt.format(f'({path})')

    def complete_cd(self, text, line, b, e):
        return [x[b-3:] for x, y in self.cwc.items() if x.startswith(line[3:])]

    def do_ls(self, key):
        'Show the top level of the current working config: ls [key]'
        conf = self.cwc
        if key:
            try:
                conf = conf[key]
            except KeyError:
                cout.error(f"No such key {key}")
                return
            self.pp.pprint(conf)
            return

        try:
            # leaf item case
            if not isinstance(conf, dict):
                print(f"{conf}")
                return
            for k, v in conf.items():
                if k in SKIP_ATTRS:
                    continue
                if k == "name" or k== "title":
                    cout.warn(f"{k}: {v}")
                elif isinstance(v, dict) or isinstance(v, list):
                    scol = col.DIR if v else col.EDIR
                    if "_shallow" in v:
                        scol = col.EDIR
                    if "_error" in v and v["_error"]:
                        scol = col.FAIL
                    if "type" in v:
                        disp = f"{k} ({v['type']})"
                    else:
                        disp = f"{k}"
                    cout._color(scol, disp)
                else:
                    cout.info(f"{k}: {v}")
        except Exception:
            import traceback
            traceback.print_exc()
            cout.info(f"{conf}")

    def complete_ls(self, text, line, b, e):
        return [x[b-3:] for x, y in self.cwc.items() if x.startswith(line[3:])]

    def do_lsd(self, key):
        'Show all config from current level down, or all config under a key: lsd [key]'
        conf = self.cwc
        if conf and hasattr(conf, "json"):
            conf = conf.json()
        if key:
            try:
                conf = next((sub for sub in conf if sub['name'] == key), None)
            except KeyError:
                cout.info(f"No such key {key}")
        self.pp.pprint(conf)

    def complete_lsd(self, text, line, b, e):
        return [x for x, y in self.cwc.iteritems()
                if isinstance(y, dict) and x.startswith(text)]

    def do_pwd(self, key):
        'Show current path in config separated by slashes: pwd'
        cout.info("/" + "/".join(self.cwd_list))

    def do_exit(self, line):
        '''Exit'''
        self._cleanup()
        return True

    def do_EOF(self, line):
        '''Exit'''
        try:
            r = input("\nReally quit? (y/N) ")
            if r.lower() == "y":
                self._cleanup()
                return True
        except Exception:
            print("\n")
            pass
        return False

    def _set_cwc(self):
        '''Set the current working configuration to what it should be
        based on the cwd_list. If the path doesn't exist, set cwc to
        the top level and clear the cwd_list.
        '''
        try:
            self.cwc, self.cwd_list = self._conf_for_list()
        except ConfigurationError:
            self.cwc = self.config
            self.cwd_list = []

    def _conf_for_list(self, cwd_list=None):
        '''Takes in a list representing a path through the config
        returns a tuple containing the current working config, and the
        "collapsed" final path (meaning it has no .. entries.
        '''
        if not cwd_list:
            cwd_list = self.cwd_list
        cwc_stack = []
        cwc = self._ep_to_dict(self.config, None)
        num = 0
        for kdir in cwd_list:
            if kdir == "":
                continue
            num += 1
            if kdir == ".." and cwc_stack:
                cwc = cwc_stack.pop()[0]
                continue
            elif kdir == "..":
                continue
            try:
                ocwc = cwc
                cwc = self._ep_to_dict(cwc[kdir], kdir)
                cwc_stack.append((ocwc, kdir))
            except KeyError:
                raise ConfigurationError(num, kdir, cwd_list)
        return (cwc, [x[1] for x in cwc_stack])

    def _ep_to_dict(self, cfg, k):
        if isinstance(cfg, list):
            new = {}
            for d in cfg:
                if type(d) is dict and "name" in d:
                    new[d['name']] = d
                if type(d) is dict and "title" in d:
                    new[d['title']] = d
                elif type(d) is dict:
                    for k, v in d.items():
                        new[str(k)] = v
                else:
                    new[d] = None
            cfg = new
        return cfg


def handle_opt(slice_name, **kwargs):
    from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager
    try:
        fablib = fablib_manager()
        with Spinner():
            sobj = fablib.get_slice(name=slice_name)
        if kwargs.get("renew"):
            days = kwargs.get("DAYS")
            if not days:
                cout.error("Must specify renewal time in days")
                return
            else:
                days = int(days)
            end_date = (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S %z")
            sobj.renew(end_date)
            cout.info(f"Slice \"{slice_name}\" renewed until {end_date}")
        elif kwargs.get("show"):
            js = sobj.show(output='text', quiet=True)
            cout.info(js)
        elif kwargs.get("delete"):
            sobj.delete()
            cout.info(f"Slice \"{slice_name}\" deleted")
    except IndexError:
        cout.error("Slice not found")
    except Exception as e:
        import traceback
        traceback.print_exc()
        cout.error(f"Error: {e}")


def sig_handler(signum, frame):
    Spinner.stop = True
    raise KeyboardInterrupt()


def main(args=None):
    args = docopt(__doc__, version='0.1')
    sname = args.get("--slice")
    prefetch = args.get("--prefetch")
    commands = ["show", "renew", "delete"]
    opt = None
    signal.signal(signal.SIGINT, sig_handler)
    for c in commands:
        opt = args.get(c, False)
        if opt:
            break
    if opt:
        if not sname:
            cout.error("Must specify a slice name!")
            exit(-1)
        try:
            handle_opt(sname, **args)
        except Exception as e:
            cout.error(f"Error: {e}")
            exit(-1)
    else:
        cmd = FabricCmd(slice_name=sname, prefetch=prefetch)
        while True:
            try:
                cmd.cmdloop()
                break
            except KeyboardInterrupt:
                cout.warn("Press control-c again to quit")
                try:
                    input()
                except KeyboardInterrupt:
                    break
                except Exception:
                    pass


if __name__ == '__main__':
    main()
