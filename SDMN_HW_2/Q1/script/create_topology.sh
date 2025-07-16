#!/usr/bin/env bash
# Refactored create_topology.sh without automatic teardown

set -euo pipefail

# Require root
if [[ $EUID -ne 0 ]]; then
  echo "Run as root." >&2
  exit 1
fi

# Configuration
declare -A NS_SUBNET=(
  [node1]=172.0.0.0/24
  [node2]=172.0.0.0/24
  [node3]=10.10.0.0/24
  [node4]=10.10.0.0/24
)
declare -A NS_IP=(
  [node1]=172.0.0.2
  [node2]=172.0.0.3
  [node3]=10.10.0.2
  [node4]=10.10.0.3
)
declare -A BR_IFACE=(
  [node1]=br1
  [node2]=br1
  [router-1]=br1
  [node3]=br2
  [node4]=br2
  [router-2]=br2
)

namespaces=(node1 node2 node3 node4 router)
bridges=(br1 br2)

# --- NO cleanup trap here ---

# Create namespaces
for ns in "${namespaces[@]}"; do
  ip netns add $ns
done

# Create bridges
for br in "${bridges[@]}"; do
  ip link add name $br type bridge
  ip link set $br up
done

# Create veths and connect nodes
for node in node1 node2 node3 node4; do
  br=${BR_IFACE[$node]}
  ip link add ${node}-veth type veth peer name ${node}-br
  ip link set ${node}-veth netns $node
  ip link set ${node}-br master $br
done

# Create veths and connect router
ip link add router-veth1 type veth peer name router-br1
ip link set router-veth1 netns router
ip link set router-br1 master br1

ip link add router-veth2 type veth peer name router-br2
ip link set router-veth2 netns router
ip link set router-br2 master br2

# Configure interfaces inside namespaces
for node in node1 node2 node3 node4; do
  ns_ip=${NS_IP[$node]}
  # gateway based on subnet
  if [[ $node == node1 || $node == node2 ]]; then
    gw=172.0.0.1
  else
    gw=10.10.0.1
  fi
  ip netns exec $node ip addr add ${ns_ip}/${NS_SUBNET[$node]##*/} dev ${node}-veth
  ip netns exec $node ip link set ${node}-veth up
  ip netns exec $node ip route add default via $gw
done

# Configure router
ip netns exec router ip addr add 172.0.0.1/24 dev router-veth1
ip netns exec router ip addr add 10.10.0.1/24 dev router-veth2
ip netns exec router ip link set router-veth1 up
ip netns exec router ip link set router-veth2 up
ip netns exec router sysctl -w net.ipv4.ip_forward=1

# Bring up bridge-side veths
for iface in node1-br node2-br router-br1 node3-br node4-br router-br2; do
  ip link set $iface up
done

echo "Topology is up. Namespaces: ${namespaces[*]}, Bridges: ${bridges[*]}"
