# QuakeLive Docker Server

QuakeLive server deployment system using Docker containers with automatic scaling and configuration management.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.x
- Bash shell (for Linux/macOS) or WSL (for Windows)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/dmitry-osin/quakelive-docker-server.git
cd quakelive-docker-server
```

### 2. Configure Environment Variables

Edit the server configuration file:

```bash
nano _util/_environment/server.env
```

Fill in the required values:

```bash
SERVER_RCON_PASSWORD=your_rcon_password
SERVER_STATS_PASSWORD=your_stats_password
SERVER_NAME_POSTFIX=your_server_name
SERVER_OWNER=your_name
SERVER_PASSWORD=server_password_if_needed
SERVER_BRAND_NAME=your_brand_name
SERVER_BRAND_TOP_FIELD=your_brand_top_field
SERVER_CONNECT_MESSAGE=welcome_message
SERVER_BALANCE_API=elo
SERVER_G_PASSWORD=game_password
SERVER_RESTART_CRON=0 6 * * *
```

### 3. Export Environment Variables

Navigate to the environment directory and export variables:

```bash
cd _util/_environment
sudo ./export-env.sh
source /etc/environment
```

### 4. Generate Server Compose Files

Navigate to the compose generator directory:

```bash
cd ../_compose-generator
```

Generate the required server types by running the appropriate script:

#### Available Server Types:
- **VA (Vampire)**: `./generate_va.sh`
- **CA (Clan Arena)**: `./generate_ca.sh`
- **Duel**: `./generate_duel.sh`
- **Premium Duel**: `./generate_premium_duel.sh`
- **Private Duel**: `./generate_private_duel.sh`
- **TDM (Team Deathmatch)**: `./generate_tdm.sh`
- **FFA (Free For All)**: `./generate_ffa.sh`
- **CTF (Capture The Flag)**: `./generate_ctf.sh`
- **Freeze Tag**: `./generate_freeze.sh`

Example for generating VA servers:
```bash
./generate_va.sh
```

### 5. Customize Templates (Optional)

Before generating compose files, you can customize server templates located in:
```
_util/_compose-generator/template/
```

Available templates:
- `va-template.yml` - Vampire servers
- `ca-template.yml` - Clan Arena servers
- `duel-template.yml` - Duel servers
- `premium-duel-template.yml` - Premium Duel servers
- `private-duel-template.yml` - Private Duel servers
- `tdm-template.yml` - Team Deathmatch servers
- `ffa-template.yml` - Free For All servers
- `ctf-template.yml` - Capture The Flag servers
- `freeze-template.yml` - Freeze Tag servers

### 6. Enable Required Services

Edit the bootstrap compose file:

```bash
nano _bootstrap/_bootstrap-compose.yml
```

Uncomment the server types you want to run:

```yaml
include:
  - ./compose/autoheal-compose.yml
  - ./compose/redis-compose.yml
  - ./compose/ofelia-compose.yml
  - ./compose/va-compose.yml        # Uncomment for VA servers
  - ./compose/ca-compose.yml        # Uncomment for CA servers
  - ./compose/duel-compose.yml      # Uncomment for Duel servers
  - ./compose/tdm-compose.yml       # Uncomment for TDM servers
  - ./compose/ffa-compose.yml       # Uncomment for FFA servers
  - ./compose/ctf-compose.yml       # Uncomment for CTF servers
  - ./compose/freeze-compose.yml    # Uncomment for Freeze servers
```

### 7. Start the Servers

Navigate to the bootstrap directory and start the services:

```bash
cd ../../_bootstrap
docker compose -f _bootstrap-compose.yml up -d
```

## Server Management

### View Running Services
```bash
docker compose -f _bootstrap-compose.yml ps
```

### View Logs
```bash
docker compose -f _bootstrap-compose.yml logs -f [service_name]
```

### Stop Services
```bash
docker compose -f _bootstrap-compose.yml down
```

### Restart Services
```bash
docker compose -f _bootstrap-compose.yml restart
```

## Configuration

### Server Configuration

Main server configuration is located in:
- `config/server.cfg` - Main server configuration
- `config/autoexec/` - Game mode specific autoexec files
- `config/factories/` - Factory configurations for each game mode
- `config/mappools/` - Map pools for each game mode
- `config/workshop/` - Workshop item configurations

### Access Control

Edit `config/access.txt` to configure admin access and permissions.

### Plugins

MinQLX plugins are located in `config/minqlx-plugins/common/` and include:
- `announce.py` - Server announcements
- `balance.py` - Team balancing
- `branding.py` - Server branding
- `commands.py` - Custom commands
- `essentials.py` - Essential server features
- And more...

## Utility Scripts

### Container Management
- `_remove-all-containers.sh` - Remove all containers
- `_stop-all-containers.sh` - Stop all containers
- `_remove-all-volumes.sh` - Remove all container volumes

### Podman Support
- `build-podman.sh` - Build using Podman
- `publish-podman.sh` - Publish using Podman

## Scheduled Tasks

The system includes Ofelia scheduler for automated tasks:
- Server restarts (configurable via `SERVER_RESTART_CRON`)
- Maintenance tasks
- Automated backups

## Monitoring

Autoheal service automatically monitors and restarts unhealthy containers.

## Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure scripts are executable
   ```bash
   chmod +x _util/_environment/export-env.sh
   chmod +x _util/_compose-generator/*.sh
   ```

2. **Environment Variables Not Set**: Ensure you sourced the environment
   ```bash
   source /etc/environment
   ```

3. **Port Conflicts**: Check that required ports are available
   ```bash
   netstat -tlnp
   ```

### Logs

Check service logs for debugging:
```bash
docker compose -f _bootstrap-compose.yml logs -f [service_name]
```

## Support

For issues and questions, please check the project repository or create an issue on GitHub.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Architecture

The system consists of:
- **Redis**: Session and data storage
- **Ofelia**: Cron job scheduler
- **Autoheal**: Container health monitoring
- **QuakeLive Servers**: Game servers for different modes
- **MinQLX**: Server-side modifications and plugins

Each server type runs in its own container with dedicated configuration and port ranges.
