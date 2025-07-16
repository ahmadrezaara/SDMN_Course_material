#!/usr/bin/env bash
# Refactored ping_ns.sh

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <src_ns> <dst_ns>" >&2
  exit 1
fi

src=$1; dst=$2

declare -A IP_MAP=(
  [node1]=172.0.0.2
  [node2]=172.0.0.3
  [node3]=10.10.0.2
  [node4]=10.10.0.3
  [router-1]=172.0.0.1
  [router-2]=10.10.0.1
)

# Determine dest IP
if [[ $dst == router ]]; then
  # choose router interface based on src subnet
  case $src in
    node1|node2) target_ip=${IP_MAP[router-1]} ;;
    node3|node4) target_ip=${IP_MAP[router-2]} ;;
    *) echo "Unknown source $src" >&2; exit 1 ;;
  esac
else
  target_ip=${IP_MAP[$dst]}
fi

if [[ -z ${target_ip:-} ]]; then
  echo "No IP mapping for $dst" >&2
  exit 1
fi

echo "Pinging $dst ($target_ip) from $src..."
ip netns exec $src ping -c4 $target_ip
