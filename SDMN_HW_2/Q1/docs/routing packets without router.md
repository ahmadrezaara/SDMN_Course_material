# Figure 2: Inter‑Subnet Connectivity Without a Separate Router

In this scenario, rather than dedicating a container or namespace to route between `172.0.0.0/24` (on `br1`) and `10.10.0.0/24` (on `br2`), we leverage the host’s own network stack to bridge the gap at Layer 3.

---

## Overview

1. **Dual‑stack the Host Bridges**  
   Assign usable IP addresses on both bridges so the host becomes the “gateway” for each subnet.

2. **Activate Kernel Forwarding**  
   Turn on IP forwarding in the host kernel so that packets arriving on one bridge can exit on the other.

3. **Point Containers to the Host**  
   In each namespace, set the host’s bridge IP as the default route.

---

## Step‑by‑Step Guide

1. **Give the Host Two Gateway Addresses**
   ```bash
   # On your host (not inside any netns)
   ip addr add 172.0.0.1/24 dev br1
   ip addr add 10.10.0.1/24 dev br2
   ```

````

Now `br1` and `br2` each have a local gateway IP.

2. **Enable Cross‑Bridge Routing**

   ```bash
   sysctl -w net.ipv4.ip_forward=1
   ```

   This single command allows the Linux kernel to pass traffic between `br1` and `br2` automatically.

3. **Reconfigure Namespaces to Use the Host as Their Gateway**

   ```bash
   for ns in node1 node2; do
     ip netns exec $ns ip route replace default via 172.0.0.1 dev ${ns}-veth
   done

   for ns in node3 node4; do
     ip netns exec $ns ip route replace default via 10.10.0.1 dev ${ns}-veth
   done
   ```

   Each container now sends off‑subnet packets to the host’s bridge IP.
````
