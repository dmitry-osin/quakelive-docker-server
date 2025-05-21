import minqlx

class rules_agreement(minqlx.Plugin):
    def __init__(self):
        
        # Register player connect event handler
        self.add_hook("player_loaded", self.handle_player_loaded)
        
        # Register commands for viewing rules
        self.add_command("rules-ru", self.cmd_rules_ru)
        self.add_command("rules-en", self.cmd_rules_en)

    def cmd_rules_ru(self, player, msg, channel):
        """Command handler for Russian rules"""
        
        rules_msg = (
            "^0Правила сервера:\n"
            "^7Отказ от ответственности: Администрация сервера не несет ответственности за любые технические неполадки, потерю данных или другие проблемы, возникающие во время игры.\n"
            "^7Запрещено использование любых читов, ботов или модификаций, дающих преимущество в игре. Нарушение приведет к перманентному бану.\n"
            "^7Оскорбления, токсичное поведение и любые формы дискриминации строго запрещены. Наказание: временный или перманентный бан.\n"
            "^7Запрещено поднимать политические темы и вести политические дискуссии. Наказание: предупреждение/кик/бан.\n"
            "^7Запрещено обсуждение религиозных тем и ведение религиозных споров. Наказание: предупреждение/кик/бан.\n"
            "^7Оскорбление администрации сервера влечет за собой немедленный бан без предупреждения.\n"
            "^7Запрещено использование нецензурной лексики в чрезмерных количествах.\n"
            "^7Спам и флуд в чате запрещены. Наказание: мут/кик."
        )
        
        player.tell(rules_msg)

    def cmd_rules_en(self, player, msg, channel):
        """Command handler for English rules"""
        
        rules_msg = (
            "^0Server Rules:\n"
            "^7Disclaimer: Server administration is not responsible for any technical issues, data loss, or other problems that may occur during gameplay.\n"
            "^7The use of any cheats, bots, or modifications that provide advantages in the game is prohibited. Violation will result in a permanent ban.\n"
            "^7Insults, toxic behavior, and any forms of discrimination are strictly prohibited. Punishment: temporary or permanent ban.\n"
            "^7Discussing political topics and engaging in political debates is prohibited. Punishment: warning/kick/ban.\n"
            "^7Discussion of religious topics and religious debates is prohibited. Punishment: warning/kick/ban.\n"
            "^7Insulting server administrators results in an immediate ban without warning.\n"
            "^7Excessive use of profanity is prohibited.\n"
            "^7Spam and flood in chat are prohibited. Punishment: mute/kick."
        )
        
        player.tell(rules_msg)



    def handle_player_loaded(self, player):
        """Check player status when they fully connect"""
        
        rules_msg = (
            "^0Check server Rules: ^7!rules-ru ^0or ^7!rules-en"
        )   
            
        # Small delay to ensure message is seen
        @minqlx.delay(10)
        def delayed_message():
            player.tell(rules_msg)
        delayed_message() 

    