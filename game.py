import pygame
import random
import math
from player import Player
from enemy import Enemy, EnemyType
from projectile import Projectile, ProjectileType
from powerups import PowerUpManager
from upgrades import UpgradeManager
from xp import XPOrb, XPManager
from ui import UI
from waves import WaveManager, WaveState
from effects import ScreenShake, ParticleSystem, FloatingTextManager
from stats_screen import StatsScreen
from music import play_music, stop_music
from sounds import init_sounds, play_sound
from music import play_music, toggle_music, init_music
from visual_feedback import VisualFeedbackManager
from enhanced_audio import DynamicAudioManager, AudioEventType, EnemyVoiceType
from asset_loader import asset_loader

class ProgressionManager:
    """Manages progressive unlocking of enemies and abilities based on player level"""
    def __init__(self, game):
        self.game = game
        
        # Enemy unlock thresholds (player level)
        self.enemy_unlocks = {
            1: [EnemyType.BASIC],
            3: [EnemyType.FAST],
            5: [EnemyType.TANK],
            7: [EnemyType.SNIPER],
            10: [EnemyType.SWARMER],
            12: [EnemyType.HEALER],
            15: [EnemyType.BOMBER],
            18: [EnemyType.BOSS],
            25: [EnemyType.MEGA_BOSS]
        }
        
        # Ability unlock thresholds for enemies
        self.ability_unlocks = {
            5: ["basic_shield"],  # Tank gets shield at level 5+
            8: ["fast_dash"],     # Fast gets dash at level 8+
            12: ["boss_summon"],   # Boss gets summon at level 12+
            15: ["tank_stomp"],    # Tank gets stomp at level 15+
            20: ["mega_abilities"], # Mega boss gets all abilities at level 20+
            25: ["elite_enhanced"] # Enhanced abilities for all elites at level 25+
        }
        
        # Weapon unlock thresholds for upgrades
        self.weapon_unlocks = {
            1: [ProjectileType.BASIC],
            3: [ProjectileType.SPREAD],
            5: [ProjectileType.PIERCING],
            7: [ProjectileType.BOUNCING],
            10: [ProjectileType.HOMING],
            12: [ProjectileType.EXPLOSIVE],
            15: [ProjectileType.RAPID],
            18: [ProjectileType.LASER],
            20: [ProjectileType.HYBRID]  # Hybrid weapons unlocked at level 20
        }
        
        # Current unlocked content
        self.unlocked_enemies = [EnemyType.BASIC]
        self.unlocked_abilities = []
        self.unlocked_weapons = [ProjectileType.BASIC]
    
    def update(self):
        """Check for new unlocks based on player level"""
        player_level = self.game.player.level
        
        # Check enemy unlocks
        for level, enemies in self.enemy_unlocks.items():
            if player_level >= level:
                for enemy_type in enemies:
                    if enemy_type not in self.unlocked_enemies:
                        self.unlocked_enemies.append(enemy_type)
                        self.show_unlock_notification(f"New Enemy: {enemy_type.value.title()}")
        
        # Check ability unlocks
        for level, abilities in self.ability_unlocks.items():
            if player_level >= level:
                for ability in abilities:
                    if ability not in self.unlocked_abilities:
                        self.unlocked_abilities.append(ability)
                        self.show_unlock_notification(f"Enemy Ability: {ability.replace('_', ' ').title()}")
        
        # Check weapon unlocks
        for level, weapons in self.weapon_unlocks.items():
            if player_level >= level:
                for weapon_type in weapons:
                    if weapon_type not in self.unlocked_weapons:
                        self.unlocked_weapons.append(weapon_type)
                        self.show_unlock_notification(f"Weapon Type: {weapon_type.value.title()}")
    
    def get_available_enemies(self):
        """Get list of currently unlocked enemy types"""
        return self.unlocked_enemies.copy()
    
    def get_available_weapons(self):
        """Get list of currently unlocked weapon types"""
        return self.unlocked_weapons.copy()
    
    def has_ability(self, ability_name):
        """Check if an ability is unlocked"""
        return ability_name in self.unlocked_abilities
    
    def show_unlock_notification(self, message):
        """Show unlock notification to player"""
        self.game.floating_text.add_announcement(
            (self.game.screen_width // 2, 100), 
            f"UNLOCKED: {message}", 
            (255, 215, 0)
        )
        play_sound('level_up')  # Use level up sound for unlocks
    
    def get_enemy_spawn_weights(self):
        """Get spawn weights based on progression"""
        player_level = self.game.player.level
        weights = {}
        
        for enemy_type in self.unlocked_enemies:
            if enemy_type == EnemyType.BASIC:
                weights[enemy_type] = max(10 - player_level // 5, 2)  # Decrease basic spawns over time
            elif enemy_type in [EnemyType.FAST, EnemyType.SWARMER]:
                weights[enemy_type] = 3 + player_level // 10  # Increase fast enemies
            elif enemy_type in [EnemyType.TANK, EnemyType.BOMBER]:
                weights[enemy_type] = 2 + player_level // 15  # Slowly increase tough enemies
            elif enemy_type == EnemyType.BOSS:
                weights[enemy_type] = 1 if player_level >= 18 else 0  # Only spawn bosses at level 18+
            elif enemy_type == EnemyType.MEGA_BOSS:
                weights[enemy_type] = 1 if player_level >= 25 else 0  # Only spawn mega boss at level 25+
            else:
                weights[enemy_type] = 3  # Default weight
        
        return weights

class Game:
    def __init__(self):
        pygame.init()
        
        # Screen setup - start in fullscreen
        self.screen_width = 1280
        self.screen_height = 720
        self.fullscreen = True
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # Get actual screen dimensions
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        pygame.display.set_caption("Bullet Heaven")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "playing"  # playing, paused, game_over, victory
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game entities
        self.player = Player((self.screen_width // 2, self.screen_height // 2))
        self.player.game = self  # Set game reference for stats tracking
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.xp_orbs = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        
        # Game systems
        self.upgrade_manager = UpgradeManager(self)
        self.ui = UI(self)
        
        # Progression system
        self.progression_manager = ProgressionManager(self)
        
        # Power-up system
        self.power_up_manager = PowerUpManager(self)
        
        # Wave system
        self.wave_manager = WaveManager(self)
        
        # Effects systems
        self.screen_shake = ScreenShake()
        self.particle_system = ParticleSystem()
        self.floating_text = FloatingTextManager()
        self.visual_feedback = VisualFeedbackManager(self)
        
        # Enhanced audio system (disabled for now)
        # self.audio_manager = DynamicAudioManager(self)
        
        # Combo system
        self.combo_count = 0
        self.combo_timer = 0
        self.max_combo = 0
        
        # Timers and stats
        self.game_time = 0
        self.wave_timer = 0
        self.wave_number = 1
        
        # Stats tracking
        self.stats = {
            "time_survived": 0,
            "waves_completed": 0,
            "highest_wave": 1,
            "deaths": 0,
            "enemies_killed": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "total_shots": 0,
            "hits_landed": 0,
            "critical_hits": 0,
            "max_combo": 0,
            "xp_gained": 0,
            "powerups_collected": 0,
            "upgrades_chosen": 0
        }
        self.enemy_spawn_timer = 0
        self.enemy_spawn_rate = 2.0  # seconds between spawns
        self.boss_spawn_timer = 0
        self.boss_spawn_interval = 60  # Spawn boss every 60 seconds
        self.boss_spawned = False
        
        # Win condition (survive 10 minutes)
        self.survival_time = 600  # seconds
        
        # Load assets
        asset_loader.load_images()
        
        # Initialize sound system
        self.sound_enabled = init_sounds()
        self.music_enabled = init_music()
        
        # Initialize music
        if self.music_enabled:
            play_music('background', loop=True)
            # Set initial volume to 30% (if volume control is available)
            # music_manager.set_volume(0.3)
    
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        # Show stats screen when game is over
        if self.game_state == "game_over":
            stats_screen = StatsScreen(self)
            result = stats_screen.show()
            
            if result == "retry":
                # Restart the game
                self.__init__()
                return self.run()
            elif result == "menu":
                # Return to main menu
                return
            elif result == "quit":
                # Quit the game
                pygame.quit()
                exit()
        
        # Don't quit pygame, just return to main menu
        return
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle mouse input for shooting
            if self.game_state == "playing":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.player.is_shooting = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left click release
                        self.player.is_shooting = False
            
            # Handle upgrade selection
            if self.game_state == "paused":
                self.upgrade_manager.handle_event(event)
                if not self.upgrade_manager.waiting_for_choice():
                    self.game_state = "playing"
            
            # Handle restart
            if self.game_state == "game_over":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_f:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Global key events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self, dt):
        if self.game_state != "playing":
            return
        
        self.game_time += dt
        
        # Check win condition
        if self.game_time >= self.survival_time:
            self.game_state = "victory"
            if self.music_enabled:
                play_music('victory', loop=False)  # Play victory music once
            return
        
        # Update player
        self.player.update(dt)
        
        # Manual shooting
        mouse_pos = pygame.mouse.get_pos()
        self.player.manual_shoot(dt, self.projectiles, mouse_pos)
        
        # Update entities
        self.enemies.update(dt, self.player.pos)
        self.projectiles.update(dt, self.enemies)  # Pass enemies for homing projectiles
        self.xp_orbs.update(dt, self.player.pos, self.player.pickup_range)
        self.power_up_manager.update(dt)
        
        # Process enemy special effects
        self.process_enemy_special_effects()
        
        # Update effects
        self.screen_shake.update(dt)
        self.particle_system.update(dt)
        self.floating_text.update(dt)
        self.visual_feedback.update(dt)
        # self.audio_manager.update(dt)
        
        # Update combo system
        self.update_combo(dt)
        
        # Spawn enemies (using wave system)
        self.wave_manager.update(dt)
        
        # Handle collisions
        self.handle_collisions()
        
        # Handle power-up collisions
        self.power_up_manager.handle_collisions(self.player)
        
        # Check game over
        if self.player.hp <= 0:
            self.game_state = "game_over"
            if self.music_enabled:
                play_music('game_over', loop=False)  # Play game over music once
    
    def spawn_enemies(self, dt):
        self.enemy_spawn_timer += dt
        
        # Update progression system
        self.progression_manager.update()
        
        # Adjust spawn rate based on player level
        player_level = self.player.level
        adjusted_spawn_rate = max(0.5, self.enemy_spawn_rate - player_level * 0.1)
        
        if self.enemy_spawn_timer >= adjusted_spawn_rate:
            self.enemy_spawn_timer = 0
            
            # Spawn enemy
            # Choose random edge
            spawn_edge = random.choice(['top', 'bottom', 'left', 'right'])
            margin = 50
            if spawn_edge == 'top':
                spawn_pos = (random.randint(margin, self.screen_width - margin), -margin)
            elif spawn_edge == 'bottom':
                spawn_pos = (random.randint(margin, self.screen_width - margin), self.screen_height + margin)
            elif spawn_edge == 'left':
                spawn_pos = (-margin, random.randint(margin, self.screen_height - margin))
            else:  # right
                spawn_pos = (self.screen_width + margin, random.randint(margin, self.screen_height - margin))
            
            # Get available enemies and weights from progression system
            available_enemies = self.progression_manager.get_available_enemies()
            spawn_weights = self.progression_manager.get_enemy_spawn_weights()
            
            # Choose enemy type based on progression weights
            enemy_types = list(spawn_weights.keys())
            weights = list(spawn_weights.values())
            
            if enemy_types and weights:
                enemy_type = random.choices(enemy_types, weights=weights)[0]
                enemy = Enemy(spawn_pos, enemy_type)
                
                # Apply ability enhancements based on progression
                self.apply_enemy_progression(enemy)
                
                # Register for visual feedback
                self.visual_feedback.register_enemy(enemy)
                
                # Play enemy spawn voice
                # voice_type = self.get_enemy_voice_type(enemy.enemy_type)
                # self.audio_manager.play_enemy_voice(voice_type, "spawn")
                
                self.enemies.add(enemy)
    
    def apply_enemy_progression(self, enemy):
        """Apply progression-based enhancements to enemies"""
        player_level = self.player.level
        
        # Scale enemy stats based on player level
        hp_multiplier = 1.0 + (player_level - 1) * 0.1  # 10% HP increase per level
        damage_multiplier = 1.0 + (player_level - 1) * 0.05  # 5% damage increase per level
        speed_multiplier = 1.0 + (player_level - 1) * 0.02  # 2% speed increase per level
        
        enemy.max_hp = int(enemy.max_hp * hp_multiplier)
        enemy.hp = enemy.max_hp
        enemy.collision_damage = int(enemy.collision_damage * damage_multiplier)
        enemy.speed = int(enemy.speed * speed_multiplier)
        
        # Apply ability unlocks
        if enemy.enemy_type == EnemyType.TANK and self.progression_manager.has_ability("basic_shield"):
            if "shield" not in enemy.abilities:
                enemy.abilities.append("shield")
                enemy.ability_cooldowns["shield"] = 8.0
        
        if enemy.enemy_type == EnemyType.FAST and self.progression_manager.has_ability("fast_dash"):
            if "dash" not in enemy.abilities:
                enemy.abilities.append("dash")
                enemy.ability_cooldowns["dash"] = 4.0
        
        if enemy.enemy_type == EnemyType.BOSS and self.progression_manager.has_ability("boss_summon"):
            if "summon" not in enemy.abilities:
                enemy.abilities.append("summon")
                enemy.ability_cooldowns["summon"] = 12.0
        
        if enemy.enemy_type == EnemyType.TANK and self.progression_manager.has_ability("tank_stomp"):
            if "stomp" not in enemy.abilities:
                enemy.abilities.append("stomp")
                enemy.ability_cooldowns["stomp"] = 6.0
        
        # Enhanced abilities at high level
        if self.progression_manager.has_ability("elite_enhanced"):
            # Boost all elite enemies
            if enemy.enemy_type in [EnemyType.BOSS, EnemyType.TANK, EnemyType.FAST]:
                enemy.max_hp = int(enemy.max_hp * 1.3)
                enemy.hp = enemy.max_hp
                enemy.collision_damage = int(enemy.collision_damage * 1.2)
    
    def spawn_boss(self, dt):
        """Spawn boss enemies periodically"""
        self.boss_spawn_timer += dt
        
        if self.boss_spawn_timer >= self.boss_spawn_interval and not self.boss_spawned:
            self.boss_spawn_timer = 0
            self.boss_spawned = True
            
            # Spawn boss from random edge
            spawn_edge = random.choice(['top', 'bottom', 'left', 'right'])
            margin = 100
            if spawn_edge == 'top':
                spawn_pos = (random.randint(margin, self.screen_width - margin), -margin)
            elif spawn_edge == 'bottom':
                spawn_pos = (random.randint(margin, self.screen_width - margin), self.screen_height + margin)
            elif spawn_edge == 'left':
                spawn_pos = (-margin, random.randint(margin, self.screen_height - margin))
            else:  # right
                spawn_pos = (self.screen_width + margin, random.randint(margin, self.screen_height - margin))
            
            # Choose boss type based on game time
            if self.game_time < 180:
                boss_type = EnemyType.BOSS
                boss_text = "BOSS INCOMING!"
                boss_color = (255, 0, 0)
            else:
                boss_type = EnemyType.MEGA_BOSS
                boss_text = "MEGA BOSS INCOMING!"
                boss_color = (255, 0, 255)
            
            # Create boss
            boss = Enemy(spawn_pos, boss_type)
            self.enemies.add(boss)
            
            # Add boss announcement
            self.floating_text.add_announcement((self.screen_width // 2, self.screen_height // 2), boss_text, boss_color)
            self.screen_shake.shake(10, 1.0)  # Big shake for boss spawn
            # self.audio_manager.play_sound(AudioEventType.BOSS_SPAWN)
            if self.music_enabled:
                play_music('boss')  # Switch to boss music
    
    def process_bomber_explosion(self, bomber):
        """Process bomber enemy explosion"""
        explosion_pos = bomber.pos
        explosion_radius = bomber.explosion_radius
        
        # Create visual explosion effect
        self.particle_system.create_explosion(explosion_pos, (255, 150, 0), 25)
        
        # Find entities in explosion radius
        # Damage enemies
        for enemy in self.enemies:
            if enemy != bomber:  # Don't damage self
                distance = (enemy.pos - explosion_pos).length()
                if distance <= explosion_radius:
                    damage_falloff = 1.0 - (distance / explosion_radius)
                    area_damage = bomber.damage * damage_falloff
                    enemy.hp -= area_damage
                    
                    # Create impact effect
                    self.particle_system.create_impact(enemy.rect.center, (255, 100, 0), 5)
                    
                    # Check if enemy died from bomber explosion
                    if enemy.hp <= 0:
                        self.particle_system.create_death_effect(enemy.rect.center, enemy.color, 10)
                        self.xp_orbs.add(XPOrb(enemy.rect.center, enemy.xp_value))
                        enemy.kill()
        
        # Damage player if in range
        player_distance = (self.player.pos - explosion_pos).length()
        if player_distance <= explosion_radius:
            damage_falloff = 1.0 - (player_distance / explosion_radius)
            player_damage = bomber.collision_damage * damage_falloff
            self.player.take_damage(int(player_damage))
            self.particle_system.create_impact(self.player.rect.center, (200, 50, 50), 8)
        
        # Screen shake for bomber explosion
        self.screen_shake.shake(15, 0.5)
        # self.audio_manager.play_sound(AudioEventType.EXPLOSION)

    def process_explosion_damage(self, explosion_data):
        """Process area damage from explosive projectiles"""
        explosion_pos = explosion_data['pos']
        explosion_radius = explosion_data['radius']
        explosion_damage = explosion_data['damage']
        
        # Create visual explosion effect
        self.particle_system.create_explosion(explosion_pos, (255, 100, 0), 20)
        
        # Find enemies in explosion radius
        for enemy in self.enemies:
            distance = (enemy.pos - explosion_pos).length()
            if distance <= explosion_radius:
                # Calculate damage based on distance (closer = more damage)
                damage_falloff = 1.0 - (distance / explosion_radius)
                area_damage = explosion_damage * damage_falloff
                
                enemy.hp -= area_damage
                
                # Create impact effect for area damage
                self.particle_system.create_impact(enemy.rect.center, (255, 150, 0), 3)
                
                # Add floating damage for area damage
                if area_damage > 1:
                    self.floating_text.add_damage_number(enemy.rect.center, int(area_damage))
                
                # Check if enemy died from area damage
                if enemy.hp <= 0:
                    # Create death effect
                    self.particle_system.create_death_effect(enemy.rect.center, enemy.color, 10)
    def get_random_edge_position(self):
        screen_width, screen_height = 1280, 720
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        
        if edge == 'top':
            return (random.randint(0, screen_width), 0)
        elif edge == 'bottom':
            return (random.randint(0, screen_width), screen_height)
        elif edge == 'left':
            return (0, random.randint(0, screen_height))
        else:  # right
            return (screen_width, random.randint(0, screen_height))
    
    def handle_collisions(self):
        # Projectile -> Enemy collisions
        hits = pygame.sprite.groupcollide(self.enemies, self.projectiles, False, False)
        explosions_to_process = []
        
        for enemy, projectiles in hits.items():
            total_damage = 0
            for projectile in projectiles:
                damage_result = projectile.on_hit(enemy)
                
                if isinstance(damage_result, tuple):
                    damage, is_explosive = damage_result
                    if is_explosive:
                        explosions_to_process.append(projectile.get_explosion_data())
                else:
                    damage = damage_result
                
                total_damage += damage
                
                if not projectile.piercing:
                    projectile.kill()
                
                # Create impact effect
                self.particle_system.create_impact(projectile.rect.center, (255, 255, 0), 5)
                # play_sound('hit')
                
                # Track damage statistics
                self.update_stats("damage_dealt", damage)
                self.update_stats("hit_landed")
            
            enemy.hp -= total_damage
            if enemy.hp <= 0:
                # Create death effect
                self.particle_system.create_death_effect(enemy.rect.center, enemy.color, 15)
                
                # Add floating damage and visual feedback
                self.floating_text.add_damage_number(enemy.rect.center, total_damage)
                self.visual_feedback.on_enemy_damaged(enemy, total_damage)
                
                # Play enemy death voice
                # voice_type = self.get_enemy_voice_type(enemy.enemy_type)
                # self.audio_manager.play_enemy_voice(voice_type, "death")
                
                # Screen shake for big enemies
                if enemy.enemy_type == EnemyType.BOSS:
                    self.screen_shake.shake(15, 0.5)
                elif enemy.enemy_type == EnemyType.TANK:
                    self.screen_shake.shake(5, 0.3)
                elif enemy.enemy_type == EnemyType.FAST:
                    self.screen_shake.shake(2, 0.1)
                else:
                    self.screen_shake.shake(3, 0.2)
                
                # Update combo
                self.increment_combo()
                
                # Special effects for boss defeat
                if enemy.enemy_type == EnemyType.BOSS:
                    self.floating_text.add_announcement(enemy.rect.center, "BOSS DEFEATED!", (0, 255, 0))
                    self.screen_shake.shake(20, 1.0)
                    self.boss_spawned = False  # Allow next boss to spawn
                    # Create big explosion
                    self.particle_system.create_explosion(enemy.rect.center, (255, 0, 0), 30)
                    # self.audio_manager.play_sound(AudioEventType.BOSS_DEFEATED)
                    if self.music_enabled:
                        play_music('normal')  # Return to normal music
                    
                    # Drop XP orb
                    self.xp_orbs.add(XPOrb(enemy.rect.center, enemy.xp_value))
                    
                    # Chance to drop power-up
                    self.power_up_manager.drop_power_up(enemy.rect.center, enemy.enemy_type.value)
                    
                    # Unregister from visual feedback
                    self.visual_feedback.unregister_enemy(enemy)
                    
                    # Track enemy kill
                    self.update_stats("enemy_killed")
                    
                    enemy.kill()
                
                # Handle bomber explosion
                elif enemy.enemy_type == EnemyType.BOMBER and not enemy.has_exploded:
                    enemy.has_exploded = True
                    self.process_bomber_explosion(enemy)
                
                # Handle mega boss defeat
                elif enemy.enemy_type == EnemyType.MEGA_BOSS:
                    self.floating_text.add_announcement(enemy.rect.center, "MEGA BOSS DEFEATED!", (255, 215, 0))
                    self.screen_shake.shake(30, 1.5)
                    # Create massive explosion
                    self.particle_system.create_explosion(enemy.rect.center, (255, 215, 0), 50)
                    # self.audio_manager.play_sound(AudioEventType.BOSS_DEFEATED)
                    if self.music_enabled:
                        play_music('normal')  # Return to normal music
                    
                    # Drop XP orb
                    self.xp_orbs.add(XPOrb(enemy.rect.center, enemy.xp_value))
                    
                    # Chance to drop power-up
                    self.power_up_manager.drop_power_up(enemy.rect.center, enemy.enemy_type.value)
                    
                    # Unregister from visual feedback
                    self.visual_feedback.unregister_enemy(enemy)
                    
                    # Track enemy kill
                    self.update_stats("enemy_killed")
                    
                    enemy.kill()
                else:
                    # Regular enemy death
                    # Drop XP orb
                    self.xp_orbs.add(XPOrb(enemy.rect.center, enemy.xp_value))
                    
                    # Chance to drop power-up
                    self.power_up_manager.drop_power_up(enemy.rect.center, enemy.enemy_type.value)
                    
                    # Unregister from visual feedback
                    self.visual_feedback.unregister_enemy(enemy)
                    
                    # Track enemy kill
                    self.update_stats("enemy_killed")
                    
                    enemy.kill()
        
        # Process area damage from explosions
        for explosion in explosions_to_process:
            if explosion:
                self.process_explosion_damage(explosion)
        
        # Player -> Enemy collisions
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
            damage = enemy.collision_damage
            self.player.take_damage(damage)
            
            # Track damage taken
            self.update_stats("damage_taken", damage)
            
            # Create impact effect
            self.particle_system.create_impact(enemy.rect.center, (200, 50, 50), 8)
            self.screen_shake.shake(8, 0.4)
            
            # Reset combo on player hit
            self.reset_combo()
            
            # Don't kill mega bosses on collision - only regular enemies
            if enemy.enemy_type != EnemyType.MEGA_BOSS:
                enemy.kill()  # Remove enemy after collision
        
        # Player -> XP orb collisions
        xp_hits = pygame.sprite.spritecollide(self.player, self.xp_orbs, False)
        for orb in xp_hits:
            self.player.add_xp(orb.value)
            
            # Track XP gained
            self.update_stats("xp_gained", orb.value)
            
            # Check for level up
            if self.player.check_level_up():
                self.game_state = "paused"
                self.upgrade_manager.trigger_level_up()
                self.floating_text.add_level_up_text(self.player.rect.center)
            
            # Create pickup effect
            self.particle_system.create_xp_pickup_effect(orb.rect.center)
            # self.audio_manager.play_sound(AudioEventType.POWER_UP_PICKUP)
            
            orb.kill()
    
    def process_enemy_special_effects(self):
        """Process special effects from enemies"""
        current_time = pygame.time.get_ticks()
        
        for enemy in self.enemies:
            if hasattr(enemy, 'special_effects'):
                effects_to_remove = []
                
                for effect in enemy.special_effects:
                    effect_type = effect[0]
                    effect_time = effect[1]
                    
                    # Process different effect types
                    if effect_type == "heal":
                        # Heal nearby enemies
                        self.heal_nearby_enemies(enemy, enemy.heal_amount, enemy.heal_range)
                        effects_to_remove.append(effect)
                        
                    elif effect_type == "explosion":
                        # Handle bomber explosion
                        if len(effect) >= 4:
                            pos, radius = effect[2], effect[3]
                            self.handle_explosion(pos, radius, enemy.damage)
                        effects_to_remove.append(effect)
                        
                    elif effect_type == "shoot":
                        # Enemy shoots projectile
                        if len(effect) >= 3:
                            target_pos = effect[2]
                            self.enemy_shoot_projectile(enemy, target_pos)
                        effects_to_remove.append(effect)
                        
                    elif effect_type == "laser_charge":
                        # Visual charging effect
                        self.create_laser_charge_effect(enemy)
                        
                    elif effect_type == "laser_fire":
                        # Fire laser beam
                        if len(effect) >= 3:
                            target_pos = effect[2]
                            self.fire_enemy_laser(enemy, target_pos)
                        effects_to_remove.append(effect)
                        
                    elif effect_type == "mortar_fire":
                        # Fire mortar projectile
                        if len(effect) >= 3:
                            target_pos = effect[2]
                            self.fire_mortar_projectile(enemy, target_pos)
                        effects_to_remove.append(effect)
                        
                    elif effect_type == "summon":
                        # Summon new enemies
                        self.summon_enemy(enemy)
                        effects_to_remove.append(effect)
                        
                    elif effect_type == "stealth":
                        # Enter stealth visual
                        enemy.color = (50, 50, 50)  # Dark color for stealth
                        
                    elif effect_type == "backstab":
                        # Exit stealth with bonus damage
                        enemy.color = (100, 100, 100)  # Normal color
                        enemy.collision_damage *= enemy.backstab_multiplier
                        
                    elif effect_type == "dash_charge":
                        # Visual charging effect for mega boss dash
                        self.create_dash_charge_effect(enemy)
                        
                    elif effect_type == "dash_execute":
                        # Visual effect for dash execution
                        if len(effect) >= 4:
                            old_pos, new_pos = effect[2], effect[3]
                            self.create_dash_effect(old_pos, new_pos)
                        effects_to_remove.append(effect)
                
                # Remove processed effects
                for effect in effects_to_remove:
                    if effect in enemy.special_effects:
                        enemy.special_effects.remove(effect)
    
    def heal_nearby_enemies(self, healer, heal_amount, heal_range):
        """Heal all enemies within range of the healer"""
        for enemy in self.enemies:
            if enemy != healer:
                distance = (enemy.pos - healer.pos).length()
                if distance <= heal_range:
                    # Heal the enemy
                    enemy.hp = min(enemy.hp + heal_amount, enemy.max_hp)
                    # Create visual effect
                    self.particle_system.create_heal_effect(enemy.rect.center)
                    # Show floating text
                    self.floating_text.add_text(enemy.rect.center, f"+{heal_amount}", (0, 255, 0))
    
    def handle_explosion(self, pos, radius, damage):
        """Handle explosion damage and effects"""
        # Create visual explosion
        self.particle_system.create_explosion(pos, (255, 100, 0), 30)
        self.screen_shake.shake(0.5, 10)
        
        # Damage player if in range
        player_distance = (self.player.pos - pos).length()
        if player_distance <= radius:
            self.player.take_damage(damage)
        
        # Damage other enemies
        for enemy in self.enemies:
            if enemy.pos != pos:  # Don't damage the exploding enemy
                distance = (enemy.pos - pos).length()
                if distance <= radius:
                    enemy.take_damage(damage // 2)  # Less damage to other enemies
    
    def enemy_shoot_projectile(self, enemy, target_pos):
        """Enemy shoots a projectile toward player"""
        from projectile import Projectile, ProjectileType
        direction = (target_pos - enemy.pos).normalize()
        projectile = Projectile(enemy.pos, direction, ProjectileType.BASIC, enemy.damage, is_enemy=True)
        self.projectiles.add(projectile)
    
    def create_laser_charge_effect(self, enemy):
        """Create visual charging effect for laser"""
        # Create charging particles around enemy
        for i in range(8):
            angle = (math.pi * 2 * i) / 8
            offset = pygame.Vector2(math.cos(angle) * 30, math.sin(angle) * 30)
            pos = enemy.pos + offset
            self.particle_system.create_particle(pos, (255, 0, 100), 1.0)
    
    def fire_enemy_laser(self, enemy, target_pos):
        """Fire laser beam from enemy to target"""
        # Create laser visual effect
        self.particle_system.create_laser_beam(enemy.pos, target_pos, (255, 0, 100), 3)
        
        # Check if player is hit
        distance = self.point_to_line_distance(self.player.pos, enemy.pos, target_pos)
        if distance < 20:  # Laser width
            self.player.take_damage(enemy.damage)
    
    def point_to_line_distance(self, point, line_start, line_end):
        """Calculate distance from point to line segment"""
        line_vec = line_end - line_start
        point_vec = point - line_start
        line_len = line_vec.length()
        
        if line_len == 0:
            return point_vec.length()
        
        line_unitvec = line_vec / line_len
        proj_length = point_vec.dot(line_unitvec)
        proj_length = max(0.0, min(line_len, proj_length))
        
        proj = line_start + line_unitvec * proj_length
        return (point - proj).length()
    
    def fire_mortar_projectile(self, enemy, target_pos):
        """Fire mortar projectile with arc trajectory"""
        from projectile import Projectile, ProjectileType
        # Create mortar projectile (would need special mortar projectile type)
        projectile = Projectile(enemy.pos, (target_pos - enemy.pos).normalize(), 
                               ProjectileType.BASIC, enemy.damage, is_enemy=True)
        projectile.is_mortar = True
        projectile.target_pos = target_pos
        projectile.explosion_radius = enemy.explosion_radius
        self.projectiles.add(projectile)
    
    def summon_enemy(self, summoner):
        """Summon a new enemy"""
        from enemy import Enemy, EnemyType
        # Choose random summon type
        summon_type = random.choice(summoner.summon_types)
        # Summon near the summoner
        offset = pygame.Vector2(random.randint(-50, 50), random.randint(-50, 50))
        summon_pos = summoner.pos + offset
        new_enemy = Enemy(summon_pos, summon_type)
        self.enemies.add(new_enemy)
        
        # Visual effect
        self.particle_system.create_summon_effect(summon_pos)
    
    def create_dash_charge_effect(self, enemy):
        """Create visual effect for mega boss dash charge"""
        # Create charging particles
        for i in range(12):
            angle = (math.pi * 2 * i) / 12
            offset = pygame.Vector2(math.cos(angle) * 40, math.sin(angle) * 40)
            pos = enemy.pos + offset
            self.particle_system.create_particle(pos, (255, 0, 255), 2.0)
    
    def create_dash_effect(self, old_pos, new_pos):
        """Create visual effect for dash execution"""
        # Create trail effect
        self.particle_system.create_dash_trail(old_pos, new_pos)
        self.screen_shake.shake(0.3, 5)

    def update_combo(self, dt):
        """Update combo system"""
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.reset_combo()
    
    def increment_combo(self):
        """Increment combo count"""
        self.combo_count += 1
        self.combo_timer = 2.0  # 2 seconds to maintain combo
        self.max_combo = max(self.max_combo, self.combo_count)
        
        # Track max combo
        self.stats["max_combo"] = self.max_combo
        
        # Add combo text for milestones
        if self.combo_count in [5, 10, 20, 50, 100]:
            self.floating_text.add_combo_text(self.player.rect.center, self.combo_count)
            # self.audio_manager.play_sound(AudioEventType.COMBO_MILESTONE)
    
    def reset_combo(self):
        """Reset combo count"""
        if self.combo_count > 0:
            self.combo_count = 0
            self.combo_timer = 0
    
    def draw(self):
        self.screen.fill((20, 20, 30))
        
        if self.game_state == "playing":
            # Apply screen shake
            shake_offset = self.screen_shake.get_offset()
            
            # Draw game entities with shake offset
            for enemy in self.enemies:
                self.screen.blit(enemy.image, (enemy.rect.x + int(shake_offset.x), enemy.rect.y + int(shake_offset.y)))
            
            for projectile in self.projectiles:
                self.screen.blit(projectile.image, (projectile.rect.x + int(shake_offset.x), projectile.rect.y + int(shake_offset.y)))
            
            for orb in self.xp_orbs:
                self.screen.blit(orb.image, (orb.rect.x + int(shake_offset.x), orb.rect.y + int(shake_offset.y)))
            
            # Draw power-ups
            self.power_up_manager.draw(self.screen)
            
            self.screen.blit(self.player.image, (self.player.rect.x + int(shake_offset.x), self.player.rect.y + int(shake_offset.y)))
            
            # Draw effects
            self.particle_system.draw(self.screen, shake_offset)
            self.floating_text.draw(self.screen, shake_offset)
            self.visual_feedback.draw(self.screen, shake_offset)
            
            # Draw UI
            self.ui.draw()
            
        elif self.game_state == "paused":
            # Draw game in background
            self.enemies.draw(self.screen)
            self.projectiles.draw(self.screen)
            self.xp_orbs.draw(self.screen)
            self.screen.blit(self.player.image, self.player.rect)
            self.ui.draw()
            
            # Draw upgrade overlay
            self.upgrade_manager.draw_ui()
            
        elif self.game_state == "game_over":
            self.draw_game_over()
            
        elif self.game_state == "victory":
            self.draw_victory()
        
        pygame.display.flip()
    
    def draw_game_over(self):
        # Full screen overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Scale font based on screen size
        game_over_font = pygame.font.Font(None, int(self.screen_width / 20))
        info_font = pygame.font.Font(None, int(self.screen_width / 40))
        
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        survival_text = info_font.render(f"Survived: {int(self.game_time)} seconds", True, (255, 255, 255))
        text_rect = survival_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        self.screen.blit(survival_text, text_rect)
        
        restart_text = info_font.render("Press R to Restart | ESC to Exit", True, (255, 255, 255))
        text_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
        self.screen.blit(restart_text, text_rect)
    
    def draw_victory(self):
        # Full screen overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Scale font based on screen size
        victory_font = pygame.font.Font(None, int(self.screen_width / 20))
        info_font = pygame.font.Font(None, int(self.screen_width / 40))
        
        victory_text = victory_font.render("VICTORY!", True, (0, 255, 0))
        text_rect = victory_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(victory_text, text_rect)
        
        time_text = info_font.render(f"Survived: {int(self.game_time)} seconds", True, (255, 255, 255))
        text_rect = time_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        self.screen.blit(time_text, text_rect)
        
        restart_text = info_font.render("Press R to Play Again | ESC to Exit", True, (255, 255, 255))
        text_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
        self.screen.blit(restart_text, text_rect)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Get actual screen dimensions
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h
        else:
            self.screen_width = 1280
            self.screen_height = 720
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Update player position to center
        if hasattr(self, 'player'):
            self.player.pos = pygame.Vector2(self.screen_width // 2, self.screen_height // 2)
            self.player.rect.center = self.player.pos
    
    def get_enemy_voice_type(self, enemy_type):
        """Get voice type for enemy"""
        voice_mapping = {
            EnemyType.BASIC: EnemyVoiceType.BASIC,
            EnemyType.FAST: EnemyVoiceType.FAST,
            EnemyType.TANK: EnemyVoiceType.TANK,
            EnemyType.BOSS: EnemyVoiceType.BOSS,
            EnemyType.MEGA_BOSS: EnemyVoiceType.MEGA_BOSS,
            # Default to basic for other types
            EnemyType.SNIPER: EnemyVoiceType.BASIC,
            EnemyType.SWARMER: EnemyVoiceType.BASIC,
            EnemyType.HEALER: EnemyVoiceType.BASIC,
            EnemyType.BOMBER: EnemyVoiceType.BASIC
        }
        return voice_mapping.get(enemy_type, EnemyVoiceType.BASIC)
    
    def get_game_stats(self):
        """Get current game statistics"""
        # Calculate accuracy
        accuracy = 0
        if self.stats["total_shots"] > 0:
            accuracy = (self.stats["hits_landed"] / self.stats["total_shots"]) * 100
        
        # Update final stats
        final_stats = self.stats.copy()
        final_stats["accuracy"] = accuracy
        final_stats["level_reached"] = self.player.level
        final_stats["time_survived"] = self.game_time
        
        return final_stats
    
    def update_stats(self, event_type, value=1):
        """Update game statistics"""
        if event_type == "enemy_killed":
            self.stats["enemies_killed"] += value
        elif event_type == "damage_dealt":
            self.stats["damage_dealt"] += value
        elif event_type == "damage_taken":
            self.stats["damage_taken"] += value
        elif event_type == "shot_fired":
            self.stats["total_shots"] += value
        elif event_type == "hit_landed":
            self.stats["hits_landed"] += value
        elif event_type == "critical_hit":
            self.stats["critical_hits"] += value
        elif event_type == "xp_gained":
            self.stats["xp_gained"] += value
        elif event_type == "powerup_collected":
            self.stats["powerups_collected"] += value
        elif event_type == "upgrade_chosen":
            self.stats["upgrades_chosen"] += value
        elif event_type == "wave_completed":
            self.stats["waves_completed"] += value
            self.stats["highest_wave"] = max(self.stats["highest_wave"], self.wave_number)
    
    def restart_game(self):
        self.__init__()
