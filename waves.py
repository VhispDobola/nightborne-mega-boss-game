import pygame
import random
import math
from enum import Enum
from enemy import Enemy, EnemyType

class WaveState(Enum):
    PREPARING = "preparing"
    ACTIVE = "active"
    BREAK = "break"
    COMPLETED = "completed"

class WaveManager:
    """Manages wave system with structured enemy spawning and difficulty scaling"""
    def __init__(self, game):
        self.game = game
        self.current_wave = 1
        self.state = WaveState.PREPARING
        self.wave_timer = 0
        self.enemies_spawned = 0
        self.enemies_to_spawn = 0
        self.break_duration = 10.0  # 10 seconds break between waves
        self.preparation_duration = 5.0  # 5 seconds preparation before wave
        self.wave_announcement_shown = False
        
        # Wave configurations
        self.wave_configs = self.generate_wave_configs()
        
    def generate_wave_configs(self):
        """Generate configurations for all waves"""
        configs = {}
        total_waves = 20  # 20 waves total
        
        for wave_num in range(1, total_waves + 1):
            config = {
                "duration": 30 + wave_num * 5,  # Waves get longer
                "enemy_count": 5 + wave_num * 2,  # More enemies per wave
                "spawn_rate": max(0.5, 2.0 - wave_num * 0.05),  # Faster spawning
                "elite_chance": min(0.5, 0.05 + wave_num * 0.02),  # More elite enemies
                "boss_wave": wave_num % 5 == 0,  # Every 5th wave is boss wave
                "mega_boss_wave": wave_num % 10 == 0,  # Every 10th wave is mega boss wave
                "enemy_types": self.get_available_enemies_for_wave(wave_num),
                "difficulty_multiplier": 1.0 + (wave_num - 1) * 0.05  # 5% harder per wave (easier progression)
            }
            configs[wave_num] = config
            
        return configs
    
    def get_available_enemies_for_wave(self, wave_num):
        """Get available enemy types based on wave number"""
        enemy_progression = {
            1: ["basic"],
            2: ["basic", "fast"],
            3: ["basic", "fast", "tank"],
            4: ["basic", "fast", "tank", "sniper"],
            5: ["basic", "fast", "tank", "sniper", "swarmer"],
            6: ["basic", "fast", "tank", "sniper", "swarmer", "healer"],
            7: ["basic", "fast", "tank", "sniper", "swarmer", "healer", "bomber"],
            8: ["basic", "fast", "tank", "sniper", "swarmer", "healer", "bomber", "projectile"],
            9: ["basic", "fast", "tank", "sniper", "swarmer", "healer", "bomber", "projectile", "laser"],
            10: ["basic", "fast", "tank", "sniper", "swarmer", "healer", "bomber", "projectile", "laser", "boss"],
            12: ["basic", "fast", "tank", "sniper", "swarmer", "healer", "bomber", "projectile", "laser", "boss", "mortar"],
            14: ["basic", "fast", "tank", "sniper", "swarmer", "healer", "bomber", "projectile", "laser", "boss", "mortar", "summoner"],
            16: ["basic", "fast", "tank", "sniper", "swarmer", "healer", "bomber", "projectile", "laser", "boss", "mortar", "summoner", "assassin"],
            20: ["basic", "fast", "tank", "sniper", "swarmer", "healer", "bomber", "projectile", "laser", "boss", "mortar", "summoner", "assassin", "mega_boss"]
        }
        
        # Find the highest wave number that's <= current wave
        available_types = ["basic"]
        for threshold, types in enemy_progression.items():
            if wave_num >= threshold:
                available_types = types
        
        return available_types
    
    def update(self, dt):
        """Update wave system"""
        self.wave_timer += dt
        
        if self.state == WaveState.PREPARING:
            self.update_preparation(dt)
        elif self.state == WaveState.ACTIVE:
            self.update_active_wave(dt)
        elif self.state == WaveState.BREAK:
            self.update_break(dt)
    
    def update_preparation(self, dt):
        """Update preparation phase"""
        if not self.wave_announcement_shown:
            self.show_wave_announcement()
            self.wave_announcement_shown = True
        
        if self.wave_timer >= self.preparation_duration:
            self.start_wave()
    
    def update_active_wave(self, dt):
        """Update active wave"""
        config = self.wave_configs[self.current_wave]
        
        # Spawn enemies
        if self.enemies_spawned < self.enemies_to_spawn:
            spawn_timer = dt
            while spawn_timer > 0 and self.enemies_spawned < self.enemies_to_spawn:
                if self.spawn_enemy():
                    self.enemies_spawned += 1
                spawn_timer -= config["spawn_rate"]
        
        # Check if wave is complete
        if len(self.game.enemies) == 0 and self.enemies_spawned >= self.enemies_to_spawn:
            self.complete_wave()
    
    def update_break(self, dt):
        """Update break period"""
        if self.wave_timer >= self.break_duration:
            self.next_wave()
    
    def spawn_enemy(self):
        """Spawn an enemy for the current wave"""
        config = self.wave_configs[self.current_wave]
        
        # Choose enemy type
        enemy_type = random.choice(config["enemy_types"])
        
        # Check if this should be an elite enemy
        is_elite = random.random() < config["elite_chance"]
        
        # Boss waves
        if config["boss_wave"] and self.enemies_spawned == 0:
            enemy_type = "boss"
        elif config["mega_boss_wave"] and self.enemies_spawned == 0:
            enemy_type = "mega_boss"
        
        # Convert string to EnemyType
        from enemy import EnemyType
        enemy_type_map = {
            "basic": EnemyType.BASIC,
            "fast": EnemyType.FAST,
            "tank": EnemyType.TANK,
            "sniper": EnemyType.SNIPER,
            "swarmer": EnemyType.SWARMER,
            "healer": EnemyType.HEALER,
            "bomber": EnemyType.BOMBER,
            "projectile": EnemyType.PROJECTILE,
            "laser": EnemyType.LASER,
            "mortar": EnemyType.MORTAR,
            "summoner": EnemyType.SUMMONER,
            "assassin": EnemyType.ASSASSIN,
            "boss": EnemyType.BOSS,
            "mega_boss": EnemyType.MEGA_BOSS
        }
        
        actual_enemy_type = enemy_type_map.get(enemy_type, EnemyType.BASIC)
        
        # Choose spawn position
        spawn_pos = self.get_wave_spawn_position()
        
        # Create enemy
        enemy = Enemy(spawn_pos, actual_enemy_type)
        
        # Apply wave difficulty multiplier
        enemy.max_hp = int(enemy.max_hp * config["difficulty_multiplier"])
        enemy.hp = enemy.max_hp
        enemy.collision_damage = int(enemy.collision_damage * config["difficulty_multiplier"])
        
        # Register for visual feedback
        self.game.visual_feedback.register_enemy(enemy)
        
        # Add to game
        self.game.enemies.add(enemy)
        return True
    
    def get_wave_spawn_position(self):
        """Get spawn position for wave enemies"""
        # Spawn from edges in patterns
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        margin = 50
        screen_width = self.game.screen_width
        screen_height = self.game.screen_height
        
        if edge == 'top':
            x = random.randint(margin, screen_width - margin)
            y = -margin
        elif edge == 'bottom':
            x = random.randint(margin, screen_width - margin)
            y = screen_height + margin
        elif edge == 'left':
            x = -margin
            y = random.randint(margin, screen_height - margin)
        else:  # right
            x = screen_width + margin
            y = random.randint(margin, screen_height - margin)
        
        return (x, y)
    
    def start_wave(self):
        """Start the current wave"""
        self.state = WaveState.ACTIVE
        self.wave_timer = 0
        self.enemies_spawned = 0
        config = self.wave_configs[self.current_wave]
        self.enemies_to_spawn = config["enemy_count"]
        
        # Show wave start message
        self.game.floating_text.add_announcement(
            (self.game.screen_width // 2, 100),
            f"Wave {self.current_wave} START!",
            (255, 255, 0)
        )
        
        # Play sound
        # from enhanced_audio import AudioEventType
        # self.game.audio_manager.play_sound(AudioEventType.WAVE_START)
    
    def complete_wave(self):
        """Complete the current wave"""
        self.state = WaveState.COMPLETED
        
        # Show completion message
        self.game.floating_text.add_announcement(
            (self.game.screen_width // 2, self.game.screen_height // 2),
            f"Wave {self.current_wave} COMPLETE!",
            (0, 255, 0)
        )
        
        # Give bonus XP
        bonus_xp = 50 * self.current_wave
        self.game.player.add_xp(bonus_xp)
        self.game.floating_text.add_announcement(
            self.game.player.rect.center,
            f"+{bonus_xp} Wave Bonus XP!",
            (255, 215, 0)
        )
        
        # Check for level up from wave bonus
        if self.game.player.check_level_up():
            self.game.game_state = "paused"
            self.game.upgrade_manager.trigger_level_up()
            self.game.floating_text.add_level_up_text(self.game.player.rect.center)
            # play_sound('level_up')
        
        # Start break
        self.state = WaveState.BREAK
        self.wave_timer = 0
        
        # Track wave completion
        self.game.update_stats("wave_completed")
        
        # Play sound
        # from enhanced_audio import AudioEventType
        # self.game.audio_manager.play_sound(AudioEventType.WAVE_COMPLETE)
    
    def next_wave(self):
        """Move to next wave"""
        self.current_wave += 1
        
        # Check if game is won (completed all waves)
        if self.current_wave > len(self.wave_configs):
            self.game.game_state = "victory"
            if self.game.music_enabled:
                from music import play_music
                play_music('victory', loop=False)
            return
        
        # Start preparation for next wave
        self.state = WaveState.PREPARING
        self.wave_timer = 0
        self.wave_announcement_shown = False
    
    def show_wave_announcement(self):
        """Show announcement for upcoming wave"""
        config = self.wave_configs[self.current_wave]
        
        # Create announcement text
        if config["boss_wave"]:
            if config["mega_boss_wave"]:
                text = f"Wave {self.current_wave}: MEGA BOSS WAVE!"
                color = (255, 0, 255)
            else:
                text = f"Wave {self.current_wave}: BOSS WAVE!"
                color = (255, 0, 0)
        else:
            text = f"Wave {self.current_wave}: {config['enemy_count']} Enemies"
            color = (255, 255, 0)
        
        self.game.floating_text.add_announcement(
            (self.game.screen_width // 2, self.game.screen_height // 2),
            text,
            color
        )
        
        # Show countdown
        countdown = int(self.preparation_duration - self.wave_timer)
        if countdown > 0:
            self.game.floating_text.add_announcement(
                (self.game.screen_width // 2, self.game.screen_height // 2 + 50),
                f"Starting in {countdown}...",
                (255, 255, 255)
            )
    
    def get_wave_info(self):
        """Get current wave information for UI"""
        if self.state == WaveState.PREPARING:
            countdown = max(0, int(self.preparation_duration - self.wave_timer))
            return f"Wave {self.current_wave} - Starting in {countdown}s"
        elif self.state == WaveState.ACTIVE:
            remaining = self.enemies_to_spawn - self.enemies_spawned
            return f"Wave {self.current_wave} - {remaining} enemies remaining"
        elif self.state == WaveState.BREAK:
            countdown = max(0, int(self.break_duration - self.wave_timer))
            return f"Break - Next wave in {countdown}s"
        else:
            return f"Wave {self.current_wave}"
    
    def is_boss_wave(self):
        """Check if current wave is a boss wave"""
        if self.current_wave in self.wave_configs:
            return self.wave_configs[self.current_wave]["boss_wave"]
        return False
    
    def get_difficulty_multiplier(self):
        """Get current difficulty multiplier"""
        if self.current_wave in self.wave_configs:
            return self.wave_configs[self.current_wave]["difficulty_multiplier"]
        return 1.0
