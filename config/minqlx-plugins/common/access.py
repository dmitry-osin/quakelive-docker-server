"""
Access control plugin for Quake Live server.
Manages banned players and prevents them from connecting to the server.
"""

import minqlx
import os
import threading

# Path to the bans file relative to the plugin directory
BANS_FILE = "bans.txt"

class access(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        
        # Initialize banned players set
        self.banned_players = set()
        
        # Lock for thread-safe operations
        self.bans_lock = threading.RLock()
        
        # Load bans on plugin initialization
        self.load_bans()
        
        # Add hooks and commands
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_command("reload_bans", self.cmd_reload_bans, 3, usage="Reloads the bans file")
        self.add_command("list_bans", self.cmd_list_bans, 2, usage="Shows list of banned players")
        
        # Log plugin initialization
        minqlx.console_print("Access control plugin initialized. Loaded {} banned players.".format(len(self.banned_players)))

    def load_bans(self):
        """Load banned players from the bans file."""
        with self.bans_lock:
            try:
                # Get the path to the bans file
                plugin_dir = os.path.dirname(os.path.abspath(__file__))
                bans_file_path = os.path.join(plugin_dir, BANS_FILE)
                
                if not os.path.exists(bans_file_path):
                    minqlx.console_print("Bans file not found at: {}".format(bans_file_path))
                    return
                
                # Clear current bans
                self.banned_players.clear()
                
                # Read bans from file
                with open(bans_file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        
                        # Skip empty lines and comments
                        if not line or line.startswith('#') or line.startswith('//'):
                            continue
                        
                        # Remove inline comments
                        if '#' in line:
                            line = line.split('#')[0].strip()
                        if '//' in line:
                            line = line.split('//')[0].strip()
                        
                        # Skip empty lines after comment removal
                        if not line:
                            continue
                        
                        # Validate Steam ID format (64-bit)
                        if line.isdigit() and len(line) == 17:
                            self.banned_players.add(line)
                        else:
                            minqlx.console_print("Invalid Steam ID format at line {}: {}".format(line_num, line))
                
                minqlx.console_print("Successfully loaded {} banned players from bans file.".format(len(self.banned_players)))
                
            except Exception as e:
                minqlx.console_print("Error loading bans file: {}".format(e))

    def handle_player_loaded(self, player):
        """Handle player loaded and check if they are banned."""
        if not player or not player.steam_id:
            return
        
        steam_id = str(player.steam_id)
        
        with self.bans_lock:
            if steam_id in self.banned_players:
                # Send ban message to the player
                player.tell("You are not allowed to join this server.")
                
                # Kick the banned player
                @minqlx.delay(0.1)
                def kick_banned():
                    try:
                        player.kick("Banned player")
                        minqlx.console_print("Kicked banned player: {} ({})".format(player.name, steam_id))
                    except Exception as e:
                        minqlx.console_print("Error kicking banned player {}: {}".format(player.name, e))
                
                kick_banned()

    def cmd_reload_bans(self, player, msg, channel):
        """Command to reload the bans file."""
        try:
            old_count = len(self.banned_players)
            self.load_bans()
            new_count = len(self.banned_players)
            
            channel.reply("^2Bans reloaded successfully.^7 Old count: {}, New count: {}".format(old_count, new_count))
            minqlx.console_print("Bans reloaded by {} ({}). Old count: {}, New count: {}".format(
                player.name, player.steam_id, old_count, new_count))
                
        except Exception as e:
            channel.reply("^1Error reloading bans: {}^7".format(e))
            minqlx.console_print("Error reloading bans: {}".format(e))

    def cmd_list_bans(self, player, msg, channel):
        """Command to list all banned players."""
        with self.bans_lock:
            if not self.banned_players:
                channel.reply("^3No players are currently banned.^7")
                return
            
            # Format the response
            banned_list = ", ".join(sorted(self.banned_players))
            channel.reply("^3Banned players ({}): ^7{}".format(len(self.banned_players), banned_list))
            
            # Log the command usage
            minqlx.console_print("Bans list requested by {} ({})".format(player.name, player.steam_id))
