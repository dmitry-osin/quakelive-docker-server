# External Access Configuration for QLStats.net

This directory contains configurations optimized for external access from services like QLStats.net.

## Key Differences:

1. **Network Mode**: Uses `bridge` mode instead of custom networks for better external accessibility
2. **Port Binding**: Explicit port binding to host interface
3. **Firewall Configuration**: Includes iptables rules for proper routing

## Usage:

1. Run the network configuration script:
   ```bash
   sudo chmod +x scripts/configure-qlstats-access.sh
   sudo ./scripts/configure-qlstats-access.sh
   ```

2. Regenerate compose files with external access templates
3. Restart containers

## Verification:

Test external access with:
```bash
# Test UDP connectivity (replace with your server IP)
nc -u YOUR_SERVER_IP 27960

# Test from external tool
qstat -q2s YOUR_SERVER_IP:27960
```

## Port Ranges:

- **Game Servers**: 27960-27999 (UDP/TCP)
- **RCON Ports**: 28960-28999 (TCP)
- **Redis**: 6379 (internal only)

## Troubleshooting:

1. Check if ports are open: `netstat -tulnp | grep 279`
2. Verify iptables rules: `sudo iptables -L`
3. Check Docker port mapping: `docker ps`
4. Test from external host: `telnet YOUR_IP 27960`
