1. **Make executable**

   ```bash
   chmod +x create_topology.sh ping_ns.sh
   ```

2. **Run topology creation**

   ```bash
   sudo ./create_topology.sh
   ```

   Expected: output “Topology created…” with namespace and bridge names.

3. **Verify namespaces & bridges**

   ```bash
   ip netns list
   # should list node1, node2, node3, node4, router

   ip link show type bridge
   # should show br1 and br2
   ```

4. **Inspect interfaces**

   ```bash
   sudo ip netns exec node1 ip addr show
   sudo ip netns exec node3 ip addr show
   sudo ip netns exec router ip addr show
   ```

   Verify each has the correct IP address on its veth.

5. **Test connectivity**

   ```bash
   sudo ./ping_ns.sh node1 node2
   sudo ./ping_ns.sh node2 node1
   sudo ./ping_ns.sh node3 router
   sudo ./ping_ns.sh node4 router
   sudo ./ping_ns.sh node3 node4
   ```

   Each should show 4 ICMP replies.

6. **Cleanup**

   ```bash
   # or rely on trap in create_topology.sh
   sudo ip netns del node1 node2 node3 node4 router
   sudo ip link del br1
   sudo ip link del br2
   ```

This verifies all Q1 requirements exactly. Let me know if you encounter any issues!
