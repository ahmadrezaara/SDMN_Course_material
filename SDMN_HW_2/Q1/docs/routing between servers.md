# Figure 3: Routing Between Hosts with a GRE Tunnel

When your container namespaces live on different physical or virtual hosts, you can stitch their networks together using a simple GRE tunnel. Below is a rephrased, step‑by‑step setup based on your friend’s answer, with fresh interface names and subnets:

---

## 1. On Host A

Assume Host A’s public IP is `<A_IP>` and Host B’s is `<B_IP>`.

```bash
# 1.1 Create the GRE tunnel interface 'gre0'
ip tunnel add gre0 mode gre local <A_IP> remote <B_IP> ttl 64

# 1.2 Bring it up
ip link set gre0 up

# 1.3 Assign a /30 point‑to‑point address for the tunnel
ip addr add 10.255.255.1/30 dev gre0
```

---

## 2. On Host B

Mirror the configuration, swapping local and remote:

```bash
# 2.1 Create the GRE tunnel interface 'gre0'
ip tunnel add gre0 mode gre local <B_IP> remote <A_IP> ttl 64

# 2.2 Bring it up
ip link set gre0 up

# 2.3 Assign the peer address
ip addr add 10.255.255.2/30 dev gre0
```

---

## 3. Add Cross‑Host Routes

On **Host A**, route the remote container subnet (`10.10.0.0/24`) via the GRE link:

```bash
ip route add 10.10.0.0/24 via 10.255.255.2 dev gre0
```

On **Host B**, route the other container subnet (`172.0.0.0/24`) back over GRE:

```bash
ip route add 172.0.0.0/24 via 10.255.255.1 dev gre0
```

---
