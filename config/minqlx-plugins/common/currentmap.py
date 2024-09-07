import minqlx

class currentmap(minqlx.Plugin):

    def __init__(self):
        self.mappool_index = 0

        #COMMANDS
        self.add_command("nextmap", self.cmd_nextmap)
        self.add_command("currentmap", self.cmd_current_map)

        #HOOKS
        self.add_hook("game_start", self.handle_game_start)
        self.add_hook("game_end", self.handle_game_end)

    #CMD/TRIGGER FUNCTIONS
    def cmd_nextmap(self, player, msg, channel):
        if self.game.state == "warmup":
            self.msg("^1Next map is not set until match starts!")
        else:
            self.msg("^1Next map: ^2{}".format(self.get_cvar("nextmap").replace("map ", "")))

    def cmd_current_map(self, player, msg, channel):
        self.msg("^1Current map: ^2{}".format("{} {}".format(self.get_cvar("mapname"), self.get_cvar("g_factory"))))

    #HOOK FUNCTIONS
    def handle_game_start(self, *args, **kwargs):
        @minqlx.delay(2)
        def delayed_thing():
            self.set_cvar("nextmap", "map_restart") #0 is map name, 1[0] is factory (ffa,etc)
        delayed_thing()

    def handle_game_end(self, *args, **kwargs):
        self.msg("^1Next map: ^2{}".format("{} {}".format(self.get_cvar("mapname"), self.get_cvar("g_factory"))))
