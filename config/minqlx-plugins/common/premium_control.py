import minqlx
import os

class premium_control(minqlx.Plugin):
    def __init__(self):
        
        # Register event handlers
        self.add_hook("team_switch_attempt", self.handle_team_switch)
        self.add_hook("player_loaded", self.handle_player_loaded)
        
        # Set the path to premium.txt
        self.premium_file = os.path.join(os.path.dirname(__file__), "premium.txt")
        self.premium_players = set()
        
        # Load premium players on plugin start
        self.load_premium_players()

    def load_premium_players(self):
        """Load premium players from file"""
        try:
            with open(self.premium_file, "r") as f:
                self.premium_players = {line.strip() for line in f if line.strip()}
            minqlx.console_print(f"^6Premium: Loaded {len(self.premium_players)} premium players")
        except FileNotFoundError:
            # Create empty file if it doesn't exist
            with open(self.premium_file, "w") as f:
                pass
            minqlx.console_print("^6Premium: Created new premium.txt file")

    def is_premium(self, player):
        """Check if player is premium"""
        return str(player.steam_id) in self.premium_players

    def handle_team_switch(self, player, old_team, new_team):
        """Handle team switch attempts"""
        
        # Check if current game type is duel (game_type = 1)
        if self.game.type_short != "duel":
            return

        # Allow spectator switches
        if new_team == "spectator":
            return
            
        # Check if player is premium
        if not self.is_premium(player):
            player.tell("^1Доступ запрещен! ^7Только premium игроки могут присоединиться к игре.\n"
                       "^1Access denied! ^7Only premium players can join the game.")
            player.put("spectator")
            return minqlx.RET_STOP_ALL
            
        return minqlx.RET_NONE

    def handle_player_loaded(self, player):
        """Check player status when they fully connect"""
        
        # Only show warning in duel mode
        if self.game.type_short != "duel":
            return
            
        if not self.is_premium(player):
            # Small delay to ensure message is seen
            @minqlx.delay(2)
            def delayed_message():
                player.tell("^1Внимание! ^7Вы не являетесь premium игроком. Вы можете только наблюдать за игрой.\n"
                           "^1Warning! ^7You are not a premium player. You can only spectate.")
            delayed_message()
        else:
            # Welcome message for premium players
            @minqlx.delay(2)
            def premium_welcome():
                player.tell("^2Добро пожаловать, premium игрок!\n"
                           "^2Welcome, premium player!")
            premium_welcome() 