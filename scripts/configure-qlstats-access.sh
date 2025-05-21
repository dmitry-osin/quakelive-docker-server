#!/bin/bash

# Configure Docker for QLStats.net external access
echo "Configuring Docker for QLStats.net external access..."

# Enable IP forwarding
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Create/update iptables rules for external access
# Allow connection tracking
sudo iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Allow forwarding for Docker networks
sudo iptables -A FORWARD -i docker0 -o eth0 -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o docker0 -j ACCEPT

# Allow QLStats.net to access game servers (UDP ports 27960-27999)
sudo iptables -A INPUT -p udp --dport 27960:27999 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 27960:27999 -j ACCEPT

# Allow RCON access (TCP ports 28960-28999)
sudo iptables -A INPUT -p tcp --dport 28960:28999 -j ACCEPT

# Save iptables rules
sudo iptables-save | sudo tee /etc/iptables/rules.v4

echo "Docker networking configured for QLStats.net access!"
echo "Make sure your cloud provider/firewall allows incoming connections on ports:"
echo "  - UDP 27960-27999 (Game servers)"
echo "  - TCP 27960-27999 (Game servers)"
echo "  - TCP 28960-28999 (RCON)"
