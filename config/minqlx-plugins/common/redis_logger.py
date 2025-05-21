import minqlx
import redis
import time
from datetime import datetime

class redis_logger(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        
        # Redis configuration from server.cfg
        self.redis_host = self.get_cvar("qlx_redisAddress", str) or "localhost"
        self.redis_port = 6379  # Default Redis port
        self.redis_db = self.get_cvar("qlx_redisDatabase", int) or 0
        self.redis_password = self.get_cvar("qlx_redisPassword", str) or None
        
        # Initialize Redis connection
        self.redis_client = None
        self.connect_redis()
        
        # Register hooks for player events
        self.add_hook("player_loaded", self.handle_player_connect)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        
        # Register hooks for chat events
        self.add_hook("chat", self.handle_chat_message)
        
        # Register commands
        self.add_command("redis-status", self.cmd_redis_status, permission=5)
        self.add_command("chat-logs", self.cmd_chat_logs, permission=5)
        self.add_command("user-info", self.cmd_user_info, permission=5)
        self.add_command("user-events", self.cmd_user_events, permission=5)
        self.add_command("user-chat", self.cmd_user_chat, permission=5)
        
        # Log plugin initialization
        self.log_event("plugin_started", "Redis logger plugin started")

    def connect_redis(self):
        """Establish connection to Redis"""
        try:
            # Check if Unix socket is enabled
            use_unix_socket = self.get_cvar("qlx_redisUnixSocket", bool) or False
            
            if use_unix_socket:
                # Connect via Unix socket
                self.redis_client = redis.Redis(
                    unix_socket_path=self.redis_host,
                    db=self.redis_db,
                    password=self.redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                self.logger.info(f"Successfully connected to Redis via Unix socket: {self.redis_host}")
            else:
                # Connect via TCP
                self.redis_client = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=self.redis_db,
                    password=self.redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                self.logger.info(f"Successfully connected to Redis at {self.redis_host}:{self.redis_port}")
            
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def log_event(self, event_type, data):
        """Log event to Redis"""
        if not self.redis_client:
            return
            
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timestamp = int(time.time())
            
            # Create log entry
            log_entry = {
                "event_type": event_type,
                "data": data,
                "datetime": current_time,
                "timestamp": timestamp
            }
            
            # Store in Redis with timestamp as key
            key = f"server_events:{timestamp}"
            self.redis_client.hmset(key, log_entry)
            
            # Set expiration for 365 days (optional)
            self.redis_client.expire(key, 365 * 24 * 60 * 60)
            
            # Also add to a list for easy retrieval
            self.redis_client.lpush("server_events", key)
            self.redis_client.ltrim("server_events", 0, 99999)  # Keep last 100000 events
            
        except Exception as e:
            self.logger.error(f"Failed to log event to Redis: {e}")

    def log_user_event(self, player_name, steam_id, ip, event_type, event_data):
        """Log user-specific event to Redis"""
        if not self.redis_client:
            return
            
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timestamp = int(time.time())
            
            # Create user event entry
            user_event = {
                "event_type": event_type,
                "data": event_data,
                "datetime": current_time,
                "timestamp": timestamp
            }
            
            # User key format: user:{steam_id}
            user_key = f"user:{steam_id}"
            
            # Store user info if not exists
            user_info = {
                "name": player_name,
                "steam_id": steam_id,
                "ip": ip,
                "first_seen": current_time,
                "last_seen": current_time
            }
            
            # Check if user exists
            if not self.redis_client.exists(user_key):
                self.redis_client.hmset(user_key, user_info)
            else:
                # Update last_seen
                self.redis_client.hset(user_key, "last_seen", current_time)
                self.redis_client.hset(user_key, "ip", ip)  # Update IP in case it changed
            
            # Add event to user's events list
            event_key = f"{user_key}:events"
            self.redis_client.lpush(event_key, str(user_event))
            self.redis_client.ltrim(event_key, 0, 99999)  # Keep last 100000 events per user
            
            # Set expiration for user data (365 days)
            self.redis_client.expire(user_key, 365 * 24 * 60 * 60)
            self.redis_client.expire(event_key, 365 * 24 * 60 * 60)
            
            # Also log to general events for backward compatibility
            self.log_event(event_type, event_data)
            
        except Exception as e:
            self.logger.error(f"Failed to log user event to Redis: {e}")

    def handle_player_connect(self, player):
        """Handle player connection event"""
        try:
            # Get player information
            name = player.name
            steam_id = player.steam_id
            ip = player.ip
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format: connect:name:steam_id:ip:time
            connect_data = f"connect:{current_time}:{name}:{steam_id}:{ip}"
            
            # Log to user-specific storage
            self.log_user_event(name, steam_id, ip, "player_connect", connect_data)
            
        except Exception as e:
            self.logger.error(f"Error handling player connect: {e}")

    def handle_player_disconnect(self, player, reason):
        """Handle player disconnection event"""
        try:
            # Get player information
            name = player.name
            steam_id = player.steam_id
            ip = player.ip
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format: disconnect:name:steam_id:ip:reason:time
            disconnect_data = f"disconnect:{current_time}:{name}:{steam_id}:{ip}:{reason}"
            
            # Log to user-specific storage
            self.log_user_event(name, steam_id, ip, "player_disconnect", disconnect_data)
            
        except Exception as e:
            self.logger.error(f"Error handling player disconnect: {e}")

    def handle_chat_message(self, player, msg, channel):
        """Handle chat message event"""
        try:
            # Get player information
            name = player.name
            steam_id = player.steam_id
            ip = player.ip
            message = msg.strip()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Determine channel type
            if channel == "chat":
                channel_type = "all"
            elif channel == "team":
                channel_type = "team"
            else:
                channel_type = "other"
            
            # Format: chat:datetime:name:steam_id:ip:channel:message
            chat_data = f"chat:{current_time}:{name}:{steam_id}:{ip}:{channel_type}:{message}"
            
            # Log to user-specific storage
            self.log_user_event(name, steam_id, ip, "chat_message", chat_data)
            
        except Exception as e:
            self.logger.error(f"Error handling chat message: {e}")

    def cmd_redis_status(self, player, msg, channel):
        """Command to check Redis connection status"""
        if self.redis_client:
            try:
                # Test Redis connection
                self.redis_client.ping()
                player.tell("^2Redis connection: ^7OK")
                
                # Get some stats
                info = self.redis_client.info()
                player.tell(f"^2Redis version: ^7{info.get('redis_version', 'Unknown')}")
                player.tell(f"^2Connected clients: ^7{info.get('connected_clients', 'Unknown')}")
                
                # Count events
                event_count = self.redis_client.llen("server_events")
                player.tell(f"^2Total events logged: ^7{event_count}")
                
            except Exception as e:
                player.tell(f"^1Redis connection error: ^7{e}")
        else:
            player.tell("^1Redis connection: ^7Not connected")

    def cmd_chat_logs(self, player, msg, channel):
        """Command to view recent chat logs"""
        if not self.redis_client:
            player.tell("^1Redis connection: ^7Not connected")
            return
            
        try:
            # Get recent chat events
            recent_events = self.redis_client.lrange("server_events", 0, 49)  # Last 50 events
            
            chat_messages = []
            for event_key in recent_events:
                event_data = self.redis_client.hgetall(event_key)
                if event_data.get("event_type") == "chat_message":
                    chat_messages.append(event_data.get("data", ""))
            
            if not chat_messages:
                player.tell("^3No recent chat messages found")
                return
            
            # Show last 10 chat messages
            player.tell("^2Recent chat messages:")
            for i, chat_data in enumerate(chat_messages[-10:], 1):
                # Parse chat data: chat:datetime:name:steam_id:ip:channel:message
                parts = chat_data.split(":")
                if len(parts) >= 7:
                    datetime_str = parts[1]
                    name = parts[2]
                    channel_type = parts[5]
                    message = parts[6]
                    
                    # Extract time from datetime
                    try:
                        time_str = datetime_str.split(" ")[1] if " " in datetime_str else datetime_str
                    except:
                        time_str = datetime_str
                    
                    channel_color = "^3" if channel_type == "team" else "^7"
                    player.tell(f"^7[{time_str}] {channel_color}[{channel_type.upper()}] ^7{name}: {message}")
            
        except Exception as e:
            player.tell(f"^1Error retrieving chat logs: ^7{e}")

    def cmd_user_info(self, player, msg, channel):
        """Command to view user information"""
        if not self.redis_client:
            player.tell("^1Redis connection: ^7Not connected")
            return
            
        if len(msg) < 2:
            player.tell("^3Usage: ^7!user-info <steam_id or name>")
            return
            
        try:
            search_term = msg[1]
            
            # Search by steam_id or name
            user_keys = self.redis_client.keys("user:*")
            
            found_user = None
            for user_key in user_keys:
                user_data = self.redis_client.hgetall(user_key)
                if (search_term.lower() in user_data.get("name", "").lower() or 
                    search_term.lower() in user_data.get("steam_id", "").lower()):
                    found_user = user_data
                    break
            
            if not found_user:
                player.tell(f"^3User not found: ^7{search_term}")
                return
            
            # Display user info
            player.tell(f"^2User Information:")
            player.tell(f"^7Name: ^3{found_user.get('name', 'Unknown')}")
            player.tell(f"^7Steam ID: ^3{found_user.get('steam_id', 'Unknown')}")
            player.tell(f"^7IP: ^3{found_user.get('ip', 'Unknown')}")
            player.tell(f"^7First seen: ^3{found_user.get('first_seen', 'Unknown')}")
            player.tell(f"^7Last seen: ^3{found_user.get('last_seen', 'Unknown')}")
            
            # Count events
            event_key = f"user:{found_user.get('steam_id')}:events"
            event_count = self.redis_client.llen(event_key)
            player.tell(f"^7Total events: ^3{event_count}")
            
        except Exception as e:
            player.tell(f"^1Error retrieving user info: ^7{e}")

    def cmd_user_events(self, player, msg, channel):
        """Command to view user events"""
        if not self.redis_client:
            player.tell("^1Redis connection: ^7Not connected")
            return
            
        if len(msg) < 2:
            player.tell("^3Usage: ^7!user-events <steam_id or name> [count]")
            return
            
        try:
            search_term = msg[1]
            count = int(msg[2]) if len(msg) > 2 else 10
            
            # Search by steam_id or name
            user_keys = self.redis_client.keys("user:*")
            
            found_steam_id = None
            for user_key in user_keys:
                user_data = self.redis_client.hgetall(user_key)
                if (search_term.lower() in user_data.get("name", "").lower() or 
                    search_term.lower() in user_data.get("steam_id", "").lower()):
                    found_steam_id = user_data.get("steam_id")
                    break
            
            if not found_steam_id:
                player.tell(f"^3User not found: ^7{search_term}")
                return
            
            # Get user events
            event_key = f"user:{found_steam_id}:events"
            events = self.redis_client.lrange(event_key, 0, count - 1)
            
            if not events:
                player.tell("^3No events found for this user")
                return
            
            player.tell(f"^2Recent events for ^3{search_term}:")
            for i, event_str in enumerate(events, 1):
                try:
                    # Parse event string
                    import ast
                    event = ast.literal_eval(event_str)
                    
                    event_type = event.get("event_type", "unknown")
                    event_data = event.get("data", "")
                    event_time = event.get("datetime", "unknown")
                    
                    # Extract time from datetime
                    time_str = event_time.split(" ")[1] if " " in event_time else event_time
                    
                    player.tell(f"^7[{time_str}] ^3{event_type.upper()}: ^7{event_data}")
                    
                except Exception as e:
                    player.tell(f"^1Error parsing event {i}: ^7{e}")
            
        except Exception as e:
            player.tell(f"^1Error retrieving user events: ^7{e}")

    def cmd_user_chat(self, player, msg, channel):
        """Command to view user chat messages"""
        if not self.redis_client:
            player.tell("^1Redis connection: ^7Not connected")
            return
            
        if len(msg) < 2:
            player.tell("^3Usage: ^7!user-chat <steam_id or name> [count]")
            return
            
        try:
            search_term = msg[1]
            count = int(msg[2]) if len(msg) > 2 else 10
            
            # Search by steam_id or name
            user_keys = self.redis_client.keys("user:*")
            
            found_steam_id = None
            for user_key in user_keys:
                user_data = self.redis_client.hgetall(user_key)
                if (search_term.lower() in user_data.get("name", "").lower() or 
                    search_term.lower() in user_data.get("steam_id", "").lower()):
                    found_steam_id = user_data.get("steam_id")
                    break
            
            if not found_steam_id:
                player.tell(f"^3User not found: ^7{search_term}")
                return
            
            # Get user events
            event_key = f"user:{found_steam_id}:events"
            events = self.redis_client.lrange(event_key, 0, count * 2)  # Get more to filter chat messages
            
            chat_messages = []
            for event_str in events:
                try:
                    import ast
                    event = ast.literal_eval(event_str)
                    
                    if event.get("event_type") == "chat_message":
                        chat_messages.append(event)
                        
                        if len(chat_messages) >= count:
                            break
                            
                except Exception:
                    continue
            
            if not chat_messages:
                player.tell("^3No chat messages found for this user")
                return
            
            player.tell(f"^2Recent chat messages for ^3{search_term}:")
            for i, event in enumerate(chat_messages, 1):
                event_data = event.get("data", "")
                event_time = event.get("datetime", "unknown")
                
                # Parse chat data: chat:datetime:name:steam_id:ip:channel:message
                parts = event_data.split(":")
                if len(parts) >= 7:
                    datetime_str = parts[1]
                    name = parts[2]
                    channel_type = parts[5]
                    message = parts[6]
                    
                    # Extract time from datetime
                    time_str = datetime_str.split(" ")[1] if " " in datetime_str else datetime_str
                    
                    channel_color = "^3" if channel_type == "team" else "^7"
                    player.tell(f"^7[{time_str}] {channel_color}[{channel_type.upper()}] ^7{name}: {message}")
            
        except Exception as e:
            player.tell(f"^1Error retrieving user chat: ^7{e}")

    def unload(self):
        """Cleanup when plugin is unloaded"""
        if self.redis_client:
            self.log_event("plugin_stopped", "Redis logger plugin stopped")
            self.redis_client.close() 