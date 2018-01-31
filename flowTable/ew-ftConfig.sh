#!/bin/bash
sudo ovs-ofctl add-flow ap1 in_port=1,actions=output:2
sudo ovs-ofctl add-flow ap1 in_port=2,actions=normal

sudo ovs-ofctl add-flow s1 in_port=1,actions=output:3
sudo ovs-ofctl add-flow s1 in_port=2,actions=output:3
sudo ovs-ofctl add-flow s1 in_port=3,actions=normal

sudo ovs-ofctl add-flow s2 in_port=1,actions=output:2
sudo ovs-ofctl add-flow s2 in_port=2,actions=normal

sudo ovs-ofctl add-flow s3 in_port=1,actions=output:2
sudo ovs-ofctl add-flow s3 in_port=2,actions=normal

sudo ovs-ofctl add-flow s4 in_port=1,actions=output:4
sudo ovs-ofctl add-flow s4 in_port=2,actions=output:4
sudo ovs-ofctl add-flow s4 in_port=3,actions=output:4
sudo ovs-ofctl add-flow s4 in_port=4,actions=normal

sudo ovs-ofctl add-flow ap1 priority=100,actions=normal
sudo ovs-ofctl add-flow s1 priority=100,actions=normal
sudo ovs-ofctl add-flow s2 priority=100,actions=normal
sudo ovs-ofctl add-flow s3 priority=100,actions=normal
sudo ovs-ofctl add-flow s4 priority=100,actions=normal