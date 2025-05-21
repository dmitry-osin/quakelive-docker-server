#!/bin/bash

echo "=== QuakeLive Docker Server - Network Diagnostics ==="
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "Note: Some checks require root privileges. Run with sudo for complete diagnostics."
   echo
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)
echo "External IP: $SERVER_IP"
echo

# Check Docker status
echo "=== Docker Status ==="
systemctl is-active docker
echo

# Check running containers
echo "=== Running Containers ==="
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
echo

# Check open ports
echo "=== Open Ports (279xx range) ==="
netstat -tulnp 2>/dev/null | grep ":279" || echo "No ports in 279xx range found"
echo

# Check iptables rules (if running as root)
if [[ $EUID -eq 0 ]]; then
    echo "=== IPTables Rules (INPUT chain) ==="
    iptables -L INPUT -n --line-numbers | grep -E "(279|ACCEPT|DROP)"
    echo
    
    echo "=== IPTables Rules (FORWARD chain) ==="
    iptables -L FORWARD -n --line-numbers | grep -E "(docker|ACCEPT|DROP)" | head -10
    echo
fi

# Check Docker networks
echo "=== Docker Networks ==="
docker network ls
echo

# Check specific network details
if docker network ls | grep -q quakelive; then
    echo "=== QuakeLive Network Details ==="
    docker network inspect quakelive | jq '.[0].Containers // "No containers connected"'
    echo
fi

# Test internal connectivity
echo "=== Internal Connectivity Test ==="
if docker ps -q --filter "name=redis" > /dev/null; then
    echo "Redis container found"
    # Test if any game server can reach Redis
    GAME_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(ffa|duel|ca|tdm)" | head -1)
    if [ ! -z "$GAME_CONTAINER" ]; then
        echo "Testing Redis connectivity from $GAME_CONTAINER..."
        docker exec $GAME_CONTAINER ping -c 1 redis 2>/dev/null && echo "✓ Redis reachable" || echo "✗ Redis not reachable"
    fi
else
    echo "No Redis container found"
fi
echo

# Test external connectivity
echo "=== External Connectivity Test ==="
echo "Testing if ports are reachable from outside..."

# Find active game servers
ACTIVE_PORTS=$(docker ps --format "{{.Ports}}" | grep -o "27[0-9][0-9][0-9]" | sort -u)

if [ ! -z "$ACTIVE_PORTS" ]; then
    for port in $ACTIVE_PORTS; do
        echo -n "Port $port: "
        timeout 3 nc -z $SERVER_IP $port 2>/dev/null && echo "✓ Open" || echo "✗ Closed/Filtered"
    done
else
    echo "No active game server ports found"
fi
echo

# QLStats.net specific tests
echo "=== QLStats.net Compatibility Check ==="
echo "Checking server query response..."

for port in $ACTIVE_PORTS; do
    echo -n "Testing query response on $port: "
    # Simulate a basic Quake Live query
    timeout 3 bash -c "echo -e '\xff\xff\xff\xffgetstatus' | nc -u $SERVER_IP $port" 2>/dev/null | grep -q "statusResponse" && echo "✓ Responding" || echo "✗ No response"
done
echo

echo "=== Summary ==="
echo "1. External IP: $SERVER_IP"
echo "2. Active ports: $ACTIVE_PORTS"
echo "3. For QLStats.net to track your servers, ensure:"
echo "   - Ports 27960-27999 are open (UDP/TCP)"
echo "   - No firewall blocking external access"
echo "   - Cloud provider security groups allow these ports"
echo "   - Server responds to status queries"
echo
echo "=== Next Steps ==="
echo "If external access fails:"
echo "1. Run: sudo ./scripts/configure-qlstats-access.sh"
echo "2. Check cloud provider firewall rules"
echo "3. Restart Docker containers"
echo "4. Test with external tool: qstat -q2s $SERVER_IP:27960"
