# SliceCommander
Tool for manipulating FABRIC slices on the command line.

## Installing

```
pip3 install -e .
```

 * slice-commander (fablib) expects a valid `fabric_rc` file at `$HOME/work/fabric_config/fabric_rc`

## Usage

```
$ slice-commander -h
Usage:
  slice-commander [options]
  slice-commander [options] show
  slice-commander [options] renew DAYS
  slice-commander [options] delete
  slice-commander (-h | --help)

Options:
  -h --help
  -s SLICE --slice SLICE
```

 * When run without arguments, `slice-commander` will attempt to load all of your active slices.
 * Once loaded, you may interact with the shell similar to a *nix bash shell with completion.
 
 Example:
 
 ```
 fabric-sc (/)> ?

Documented commands (type help <topic>):
========================================
EOF  cd  delete  exit  help  ls  lsd  pwd  renew  show  ssh  sync

fabric-sc (/)> help ssh
SSH to a node: ssh [node_path]
The ssh command can also be used within a node leaf
fabric-sc (/)> show --> [tab]
components  interfaces  keys        networks    nodes       
```
