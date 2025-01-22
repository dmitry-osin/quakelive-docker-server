import minqlx

class rules_agreement(minqlx.Plugin):
    def __init__(self):
        
        # Register player connect event handler
        self.add_hook("player_loaded", self.handle_player_loaded)
        
        # Register command for viewing rules
        self.add_command("rules", self.cmd_show_rules)

    def cmd_show_rules(self, player, msg, channel):
        """Command handler for viewing rules"""
        
        rules_msg = (
            "^7Правила сервера AktiveHateX / AktiveHateX Server Rules:\n"
            "^5Русская версия: ^7aktvhtx.ru/rules.html\n"
            "^5English version: ^7aktvhtx.ru/rules_en.html\n"
            "\n"
            "^7Оставаясь на сервере, вы соглашаетесь с данными правилами.\n"
            "^7By staying on the server, you agree to these rules."
        )
        
        player.tell(rules_msg)

    def handle_player_loaded(self, player):
        """Check player status when they fully connect"""
        
        rules_msg = (
            "^7Правила сервера AktiveHateX / AktiveHateX Server Rules:\n"
            "^5Русская версия: ^7aktvhtx.ru/rules.html\n"
            "^5English version: ^7aktvhtx.ru/rules_en.html\n"
            "\n"
            "^7Оставаясь на сервере, вы соглашаетесь с данными правилами.\n"
            "^7By staying on the server, you agree to these rules."
        )   
            
        # Small delay to ensure message is seen
        @minqlx.delay(5)
        def delayed_message():
            player.tell(rules_msg)
        delayed_message() 

    