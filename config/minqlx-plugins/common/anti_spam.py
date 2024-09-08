import minqlx
import time

class anti_spam(minqlx.Plugin):
    def __init__(self):
        self.messages = {}

        self.set_cvar_once("qlx_antiSpamWarningThreshold", "15")
        self.set_cvar_once("qlx_antiSpamKickThreshold", "20")

        self.add_hook("chat", self.handle_chat)
        self.add_hook("player_connect", self.handle_player_connect)
        self.add_hook("player_disconnect", self.handle_player_disconnect)

    def handle_player_connect(self, player):
        self.messages[player.steam_id] = []

    def handle_player_disconnect(self, player, reason):
        if player.steam_id in self.messages:
            del self.messages[player.steam_id]

    def handle_chat(self, player, msg, channel):
        if self.is_privileged(player):
            return

        now = time.time()
        if player.steam_id not in self.messages:
            self.messages[player.steam_id] = []

        self.messages[player.steam_id].append(now)
        self.messages[player.steam_id] = [t for t in self.messages[player.steam_id] if now - t <= 10]

        warning_threshold = self.get_cvar("qlx_antiSpamWarningThreshold", int)
        kick_threshold = self.get_cvar("qlx_antiSpamKickThreshold", int)

        if len(self.messages[player.steam_id]) == warning_threshold:
            player.tell("You are sending messages too frequently. Please slow down.")
        elif len(self.messages[player.steam_id]) > kick_threshold:
            player.kick("You have been kicked for spamming.")
            self.record_kick(player)

    def is_privileged(self, player):
        if player.steam_id == minqlx.owner():
            return True
        return player.privileges in [minqlx.PRIV_ADMIN, minqlx.PRIV_MOD]

    def record_kick(self, player):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        self.db.sadd("kicked_players", f"{player.steam_id}:{now}")
