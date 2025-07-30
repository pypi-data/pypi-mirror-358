#! /usr/bin/env python3

import sys
import os
import subprocess
from pathlib import Path

default_config = {
    "arch": "/usr/bin/qemu-system-x86_64",
    "mac": "00:aa:31:25:2a:00",
    "memory": "2048",
    "cores": "2",
    "sambashare": "$HOME/share_quickqemu",
    "output": os.environ.get("QUICK_QEMU_OUTPUT", "spice-app"),
    "glrendering": "QUICK_QEMU_NOGL" not in os.environ,
    "cpu": os.environ.get("QUICK_QEMU_CPU", "Opteron_G1"),
    "machine": os.environ.get("QUICK_QEMU_MACHINE", "pc,accel=kvm"),
}


def resolve_path(path):
    return Path(os.path.realpath(os.path.expandvars(os.path.expanduser(path))))


def qemu_args(qemu_argv, config):
    cmdargs = [config["arch"]]
    cmdargs += ["-machine", config["machine"]]
    cmdargs += ["-cpu", config["cpu"]]
    cmdargs += ["-rtc", "base=localtime,driftfix=slew"]
    cmdargs += ["-global", "kvm-pit.lost_tick_policy=discard"]
    cmdargs += ["-enable-kvm"]
    cmdargs += ["-device", "virtio-balloon"]
    cmdargs += ["-smp", "cpus={cores},threads=1".format(cores=config["cores"])]
    cmdargs += ["-m", config["memory"]]
    cmdargs += ["-vga", "qxl"]
    cmdargs += ["-display", config["output"]]
    if config["glrendering"] and config["output"] == "spice-app":
        cmdargs += ["-spice", "gl=on"]
    # sound
    cmdargs += ["-device", "intel-hda", "-device", "hda-duplex"]
    cmdargs += ["-boot", "order=cd,once=dc"]
    cmdargs += [
        "-netdev",
        "user,id=qemunet0,net=10.0.2.0/24,dhcpstart=10.0.2.15",
    ]

    if config["sambashare"]:
        sambashare = resolve_path(config["sambashare"])
        if sambashare.is_dir():
            cmdargs[-1] += ",smb={},smbserver=10.0.2.4".format(sambashare)
        else:
            print('"{}" does not exist, disable sambashare'.format(sambashare))
    else:
        print("Sambashare disabled")
    cmdargs += [
        "-device",
        "virtio-net-pci,mac={},netdev=qemunet0".format(config["mac"]),
    ]

    is_part_argument = False
    for elem in qemu_argv:
        if elem[0] != "-" and not is_part_argument:
            path = resolve_path(elem)
            if path.is_file():
                if path.suffix == ".iso":
                    params = "media=cdrom,readonly=on"
                    cmdargs += [
                        "-drive",
                        "file={path},{params}".format(
                            path=path, params=params
                        ),
                    ]
                else:
                    if os.access(str(path), os.W_OK):
                        params = "media=disk,cache=writeback"
                    else:
                        params = "media=disk,readonly=on"
                    cmdargs += [
                        "-drive",
                        "file={path},{params}".format(
                            path=path, params=params
                        ),
                    ]
            elif path.is_block_device():
                if os.access(str(path), os.W_OK):
                    params = "media=disk,discard=on,cache=none,format=raw"
                else:
                    params = "media=disk,readonly=on"
                cmdargs += [
                    "-drive",
                    "file={path},{params}".format(  # noqa: 501
                        path=path, params=params
                    ),
                ]
            else:
                print(
                    "Not a valid file: {}, ({})".format(path, elem),
                    file=sys.stderr,
                )
                return None
                # cmdargs.append(elem)  # not path
            # first check if it is a valid file then check read access
            if not os.access(str(path), os.R_OK):
                print("No permission:", path, file=sys.stderr)
                return None
        else:
            # switch if - less argument is encountered
            if elem[0] != "-":
                is_part_argument = False
            else:
                is_part_argument = True
            cmdargs.append(elem)
    return cmdargs


def help():
    print(
        "Usage: quick_quemu [<isofile>|<discfile>|<devicefile>|-<parameter>"
        " <argument>]..."
    )


def main(argv=None, config=default_config):
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "-help", "--help"):
        help()
        return

    if not os.access(config["arch"], os.X_OK):
        print(
            "Qemu not found or not executable:",
            config["arch"],
            file=sys.stderr,
        )
        return
    cmds = qemu_args(argv, config)
    if cmds:
        subprocess.run(cmds)
