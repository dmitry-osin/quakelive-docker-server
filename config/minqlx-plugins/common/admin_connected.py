import minqlx

class admin_connected(minqlx.Plugin):
    def __init__(self):
        self.add_hook("player_connect", self.handle_player_connect)

    def handle_player_connect(self, player):
        if player == minqlx.owner():
            self.msg(f"^1{player.name} ^7(owner) has connected to the server!")
        elif player.privileges == minqlx.PRIV_ADMIN:
            self.msg(f"^1{player.name} ^7(administrator) has connected to the server!")
        elif player.privileges == minqlx.PRIV_MOD:
            self.msg(f"^1{player.name} ^7(moderator) has connected to the server!")