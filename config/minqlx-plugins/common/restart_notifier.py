import minqlx
import os
from datetime import datetime, timedelta

class restart_notifier(minqlx.Plugin):
    def __init__(self):
        # Get cron expression from environment variable
        self.cron_expression = os.getenv('SERVER_RESTART_CRON', '0 6 * * *')
        
        # Parse cron expression to get restart time
        self.restart_hour, self.restart_minute = self.parse_cron_expression(self.cron_expression)
        
        # Register player connect event handler
        self.add_hook("player_loaded", self.handle_player_loaded)
        
        # Register command for manual restart info
        self.add_command("restart", self.cmd_restart_info)
        
        minqlx.console_print(f"Restart notifier initialized. Restart time: {self.restart_hour:02d}:{self.restart_minute:02d}")

    def parse_cron_expression(self, cron_expr):
        """Parse cron expression to extract hour and minute"""
        try:
            parts = cron_expr.split()
            if len(parts) >= 2:
                minute = int(parts[0])
                hour = int(parts[1])
                return hour, minute
            else:
                minqlx.console_print("Invalid cron expression, using default 06:00")
                return 6, 0
        except (ValueError, IndexError):
            minqlx.console_print("Error parsing cron expression, using default 06:00")
            return 6, 0

    def get_next_restart_time(self):
        """Calculate next restart time based on current time"""
        now = datetime.now()
        restart_today = now.replace(hour=self.restart_hour, minute=self.restart_minute, second=0, microsecond=0)
        
        if now < restart_today:
            return restart_today
        else:
            return restart_today + timedelta(days=1)

    def get_time_until_restart(self):
        """Get time remaining until next restart"""
        next_restart = self.get_next_restart_time()
        now = datetime.now()
        time_diff = next_restart - now
        
        return time_diff

    def format_time_remaining(self, time_diff):
        """Format time difference into human readable string"""
        total_seconds = int(time_diff.total_seconds())
        
        if total_seconds <= 0:
            return "менее минуты / less than a minute"
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}ч {minutes}м / {hours}h {minutes}m"
        else:
            return f"{minutes}м / {minutes}m"

    def handle_player_loaded(self, player):
        """Show restart info when player connects"""
        try:
            time_diff = self.get_time_until_restart()
            time_remaining = self.format_time_remaining(time_diff)
            restart_time = f"{self.restart_hour:02d}:{self.restart_minute:02d}"
            
            info_msg = (
                f"^7Время перезагрузки: ^5{restart_time} (ежедневно)\n"
                f"^7Restart time: ^5{restart_time} (daily)\n"
                f"^7Use ^5!restart ^7to view this info again"
            )
            
            # Small delay to ensure message is seen
            @minqlx.delay(60)
            def delayed_message():
                player.tell(info_msg)
            delayed_message()
            
        except Exception as e:
            minqlx.console_print(f"Error showing restart info to player: {e}")

    def cmd_restart_info(self, player, msg, channel):
        """Command handler for restart information"""
        try:
            time_diff = self.get_time_until_restart()
            time_remaining = self.format_time_remaining(time_diff)
            
            restart_time = f"{self.restart_hour:02d}:{self.restart_minute:02d}"
            
            info_msg = (
                f"^7📅 ИНФОРМАЦИЯ О ПЕРЕЗАГРУЗКЕ / RESTART INFO:\n"
                f"^7Время перезагрузки: ^5{restart_time} (ежедневно)\n"
                f"^7Restart time: ^5{restart_time} (daily)\n"
                f"^7До перезагрузки: ^5{time_remaining}\n"
                f"^7Time until restart: ^5{time_remaining}"
            )
            
            player.tell(info_msg)
            
        except Exception as e:
            player.tell("^1Error getting restart info")
            minqlx.console_print(f"Error in restart info command: {e}")
