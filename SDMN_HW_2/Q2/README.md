# Minimal Container Runtime

This repository provides a simple "docker-like" CLI (`container_runtime.py`)
that demonstrates the core concepts of Linux containers:

- **Namespaces**: network, mount, PID, and UTS isolation.
- **Filesystem isolation**: pivot into a Ubuntu 20.04 root filesystem.
- **Memory cgroups** (optional): limit container memory usage.

---

## Prerequisites

1. **Ubuntu 20.04 root filesystem**

   ```bash
   sudo mkdir -p /ubuntu_rootfs
   wget -O ubuntu-rootfs.tar.gz \
     https://partner-images.canonical.com/core/focal/current/ubuntu-focal-core-cloudimg-amd64-root.tar.gz
   sudo tar -xzf ubuntu-rootfs.tar.gz -C /ubuntu_rootfs
   ```

2. **Python 3**

   Ensure `python3` is installed:

   ```bash
   python3 --version
   ```

3. **util-linux** (for `unshare` and `mount`)

   ```bash
   sudo apt-get update
   sudo apt-get install -y util-linux
   ```

4. **Permissions**

   Running the CLI requires root privileges:

   ```bash
   sudo -v
   ```

---

## Usage

Make the script executable:

```bash
chmod +x container_runtime.py
```

### 1. Launch container without memory limit

```bash
sudo ./container_runtime.py mycontainer
```

You will be dropped into a new shell inside the container as PID 1.

### 2. Launch container with memory limit (bonus)

```bash
sudo ./container_runtime.py mycontainer --memory 50
```

This sets a 50 MB limit using the memory cgroup v1 controller.

---

## Verifying the Deliverables

Once inside the container shell, run the following steps to confirm each requirement.

### A. Namespaces Isolation

1. **Mount** the proc filesystem:

   ```bash
   mount -t proc proc /proc
   ```

2. **Inspect** each namespace inode:

   ```bash
   for ns in net mnt pid uts; do
     echo -n "$ns: "; readlink /proc/1/ns/$ns
   done
   ```

Each should display a unique identifier different from the host.

### B. Root Filesystem

1. **Check** Ubuntu version:

   ```bash
   cat /etc/os-release
   ```

   You should see “Ubuntu 20.04.6 LTS”.

2. **List** root directory contents:

   ```bash
   ls /
   ```

   You should see standard Ubuntu directories (e.g. `bin`, `etc`, `usr`) without your host’s arbitrary folders.

### C. Memory Limit (Optional)

1. **Locate** the cgroup path and **verify** the limit file:

   ```bash
   ls -l /sys/fs/cgroup/memory/mycontainer
   cat /sys/fs/cgroup/memory/mycontainer/memory.limit_in_bytes
   ```

   Expected value: `52428800` (50 × 1024²).

2. **Test** enforcement by allocating more memory:

   ```bash
   python3 - <<'EOF'
   a = bytearray(60 * 1024 * 1024)
   print("Allocated 60MB successfully")
   EOF
   ```

   The process should be killed by the OOM killer when it exceeds the cgroup limit.

---

## Cleanup

Exit the container shell to return to your host:

```bash
exit
```

No additional cleanup is required.
