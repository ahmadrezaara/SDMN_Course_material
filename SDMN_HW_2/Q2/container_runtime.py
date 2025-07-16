#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess

# Constants
NAMESPACE_FLAGS = ["--fork", "--pid", "--mount-proc", "--mount", "--uts", "--net"]
DEFAULT_ROOTFS = "/ubuntu_rootfs"

def parse_args():
    parser = argparse.ArgumentParser(
        description="Minimal container runtime: namespaces, rootfs, and optional memory limit."
    )
    parser.add_argument(
        "name",
        help="Container name (used as hostname and cgroup directory)."
    )
    parser.add_argument(
        "--rootfs",
        default=DEFAULT_ROOTFS,
        help=f"Path to root filesystem (default: {DEFAULT_ROOTFS})."
    )
    parser.add_argument(
        "--memory",
        type=int,
        metavar="MB",
        help="Optional memory limit in megabytes."
    )
    parser.add_argument(
        "--child",
        action="store_true",
        help=argparse.SUPPRESS
    )
    return parser.parse_args()

def mount_proc():
    try:
        subprocess.run(["mount", "-t", "proc", "proc", "/proc"], check=True)
    except subprocess.CalledProcessError:
        print("Warning: failed to mount /proc inside container.")

def setup_rootfs(rootfs_path):
    if not os.path.isdir(rootfs_path):
        sys.exit(f"Error: rootfs path '{rootfs_path}' does not exist or is not a directory.")
    os.chroot(rootfs_path)
    os.chdir("/")

def run_container(args):
    cmd = ["unshare"] + NAMESPACE_FLAGS + [sys.executable, __file__, "--child"]
    cmd += [args.name, "--rootfs", args.rootfs]
    if args.memory is not None:
        cmd += ["--memory", str(args.memory)]
    subprocess.run(cmd, check=True)

def child_routine(args):
    # 1) Set hostname
    subprocess.run(["hostname", args.name], check=True)

    # 2) Mount /proc
    mount_proc()

    # 2.a) If memory limit requested, mount the v1 memory cgroup controller
    if args.memory is not None:
        os.makedirs("/sys/fs/cgroup/memory", exist_ok=True)
        subprocess.run(
            ["mount", "-t", "cgroup", "-o", "memory", "memory", "/sys/fs/cgroup/memory"],
            check=False
        )

    # 3) Pivot into new rootfs
    setup_rootfs(args.rootfs)

    # 4) Apply memory limit if requested
    if args.memory is not None:
        cgroup_path = f"/sys/fs/cgroup/memory/{args.name}"
        os.makedirs(cgroup_path, exist_ok=True)
        with open(f"{cgroup_path}/memory.limit_in_bytes", "w") as f:
            f.write(str(args.memory * 1024 * 1024))
        with open(f"{cgroup_path}/tasks", "w") as f:
            f.write(str(os.getpid()))

    # 5) Exec into shell as PID 1
    os.execv("/bin/bash", ["/bin/bash"])

if __name__ == "__main__":
    options = parse_args()
    if options.child:
        child_routine(options)
    else:
        run_container(options)
