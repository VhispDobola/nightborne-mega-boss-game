import pygame
import math
from enum import Enum

class EnemyType(Enum):
    BASIC = "basic"
    TANK = "tank"
    FAST = "fast"
    BOSS = "boss"
    SNIPER = "sniper"
    SWARMER = "swarmer"
    HEALER = "healer"
    BOMBER = "bomber"
    MEGA_BOSS = "mega_boss"
    PROJECTILE = "projectile"
    LASER = "laser"
    MORTAR = "mortar"
    SUMMONER = "summoner"
    ASSASSIN = "assassin"

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, enemy_type=EnemyType.BASIC):
        super().__init__()
        self.enemy_type = enemy_type
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        
        # Load custom images if available
        self.load_custom_images()
        
        # Special effects tracking
        self.special_effects = []
        
        # Animation state
        self.current_state = "normal"
        self.animation_timer = 0
        
        # Default ability states (to avoid AttributeError)
        self.dashing = False
        self.phased = False
        self.shield_active = False
        self.shield_duration = 0
        self.rage_threshold = 0.3
        self.abilities = []
        self.ability_cooldowns = {}
        self.summon_types = [EnemyType.BASIC, EnemyType.FAST]  # Default summon types
        
        # Set stats based on enemy type
        if enemy_type == EnemyType.BASIC:
            self.setup_basic()
        elif enemy_type == EnemyType.TANK:
            self.setup_tank()
        elif enemy_type == EnemyType.FAST:
            self.setup_fast()
        elif enemy_type == EnemyType.BOSS:
            self.setup_boss()
        elif enemy_type == EnemyType.SNIPER:
            self.setup_sniper()
        elif enemy_type == EnemyType.SWARMER:
            self.setup_swarmer()
        elif enemy_type == EnemyType.HEALER:
            self.setup_healer()
        elif enemy_type == EnemyType.BOMBER:
            self.setup_bomber()
        elif enemy_type == EnemyType.PROJECTILE:
            self.setup_projectile()
        elif enemy_type == EnemyType.LASER:
            self.setup_laser()
        elif enemy_type == EnemyType.MORTAR:
            self.setup_mortar()
        elif enemy_type == EnemyType.SUMMONER:
            self.setup_summoner()
        elif enemy_type == EnemyType.ASSASSIN:
            self.setup_assassin()
        elif enemy_type == EnemyType.MEGA_BOSS:
            self.setup_mega_boss()
        
        # Create visual based on type
        self.create_visual()
        self.rect = self.image.get_rect(center=self.pos)
        
    def setup_basic(self):
        """Basic chaser enemy - balanced stats"""
        self.max_hp = 25  # Slightly easier early game
        self.hp = self.max_hp
        self.speed = 100  # Slightly slower for better balance
        self.size = 30
        self.color = (200, 60, 60)
        self.collision_damage = 8  # Reduced damage
        self.xp_value = 15
        
    def setup_tank(self):
        """Tank enemy - slow but high HP"""
        self.max_hp = 80  # Reduced for better balance
        self.hp = self.max_hp
        self.speed = 70  # Slightly faster to be more threatening
        self.size = 45
        self.color = (150, 50, 150)
        self.collision_damage = 15  # Reduced damage
        self.xp_value = 25
        
        # Tank abilities
        self.abilities = ["shield", "stomp"]
        self.ability_cooldowns = {"shield": 6.0, "stomp": 4.0}
        self.shield_active = False
        self.shield_duration = 2.0
        
    def setup_fast(self):
        """Fast melee enemy - low HP but high speed"""
        self.max_hp = 20
        self.hp = self.max_hp
        self.speed = 200
        self.size = 20
        self.color = (255, 150, 50)
        self.collision_damage = 15
        self.xp_value = 20
        
        # Fast abilities
        self.abilities = ["dash", "phase"]
        self.ability_cooldowns = {"dash": 3.0, "phase": 5.0}
        self.dashing = False
        self.phased = False
        
    def setup_boss(self):
        """Boss enemy - very high HP and damage"""
        self.max_hp = 500
        self.hp = self.max_hp
        self.speed = 40
        self.size = 80
        self.color = (255, 0, 0)
        self.collision_damage = 50
        self.xp_value = 100
        
        # Boss abilities
        self.abilities = ["rage", "summon", "shockwave"]
        self.ability_cooldowns = {"rage": 5.0, "summon": 8.0, "shockwave": 10.0}
        self.rage_threshold = 0.3  # Activate rage at 30% HP
        
    def create_visual(self):
        """Create visual representation based on enemy type"""
        if self.enemy_type == EnemyType.BASIC:
            # Triangle for basic enemy
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            points = [
                (self.size//2, 0),
                (self.size, self.size),
                (0, self.size)
            ]
            pygame.draw.polygon(self.image, self.color, points)
            
        elif self.enemy_type == EnemyType.TANK:
            # Square for tank enemy
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(self.image, self.color, (0, 0, self.size, self.size))
            pygame.draw.rect(self.image, (100, 30, 100), (0, 0, self.size, self.size), 3)
            
        elif self.enemy_type == EnemyType.FAST:
            # Diamond for fast enemy
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            points = [
                (self.size//2, 0),
                (self.size, self.size//2),
                (self.size//2, self.size),
                (0, self.size//2)
            ]
            pygame.draw.polygon(self.image, self.color, points)
            
        elif self.enemy_type == EnemyType.BOSS:
            # Large hexagon for boss
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            center = self.size // 2
            radius = self.size // 2 - 5
            points = []
            for i in range(6):
                angle = i * 60  # 60 degrees for hexagon
                x = center + radius * math.cos(math.radians(angle))
                y = center + radius * math.sin(math.radians(angle))
                points.append((x, y))
            pygame.draw.polygon(self.image, self.color, points)
            pygame.draw.polygon(self.image, (200, 0, 0), points, 4)
            # Add a center dot
            pygame.draw.circle(self.image, (255, 100, 100), (center, center), 8)
            
        elif self.enemy_type == EnemyType.SNIPER:
            # Crosshair for sniper
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            center = self.size // 2
            pygame.draw.circle(self.image, self.color, (center, center), self.size // 2, 2)
            pygame.draw.line(self.image, self.color, (center, 5), (center, self.size - 5), 2)
            pygame.draw.line(self.image, self.color, (5, center), (self.size - 5, center), 2)
            
        elif self.enemy_type == EnemyType.SWARMER:
            # Small circle for swarmer
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size // 2, self.size // 2), self.size // 2)
            
        elif self.enemy_type == EnemyType.HEALER:
            # Plus sign for healer
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            center = self.size // 2
            pygame.draw.circle(self.image, self.color, (center, center), self.size // 2, 2)
            pygame.draw.rect(self.image, self.color, (center - 2, 5, 4, self.size - 10))
            pygame.draw.rect(self.image, self.color, (5, center - 2, self.size - 10, 4))
            
        elif self.enemy_type == EnemyType.BOMBER:
            # Fuse bomb for bomber
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size // 2, self.size // 2), self.size // 2)
            # Add fuse
            fuse_end = (self.size // 2 + 8, 5)
            pygame.draw.line(self.image, (100, 50, 0), (self.size // 2, 5), fuse_end, 2)
            pygame.draw.circle(self.image, (255, 200, 0), fuse_end, 3)
            
        elif self.enemy_type == EnemyType.MEGA_BOSS:
            # Try to load custom mega boss image, fallback to generated shape
            from asset_loader import asset_loader
            
            custom_image = asset_loader.get_image("mega_boss")
            if custom_image:
                # Scale the custom image to fit the enemy size
                self.image = pygame.transform.scale(custom_image, (self.size, self.size))
            else:
                # Fallback to star shape for mega boss
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                center = self.size // 2
                outer_radius = self.size // 2 - 5
                inner_radius = outer_radius // 2
                points = []
                for i in range(10):  # 5 points star
                    angle = i * 36 - 90  # Start from top
                    if i % 2 == 0:
                        radius = outer_radius
                    else:
                        radius = inner_radius
                    x = center + radius * math.cos(math.radians(angle))
                    y = center + radius * math.sin(math.radians(angle))
                    points.append((x, y))
                pygame.draw.polygon(self.image, self.color, points)
                pygame.draw.polygon(self.image, (200, 0, 200), points, 3)
                # Add center
                pygame.draw.circle(self.image, (255, 150, 255), (center, center), 8)
        
        # Add missing enemy types with fallback visuals
        else:
            # Default circle for any missing enemy type
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size // 2, self.size // 2), self.size // 2)
            pygame.draw.circle(self.image, (255, 255, 255), (self.size // 2, self.size // 2), self.size // 2, 2)
    
    def load_custom_images(self):
        """Load custom images for this enemy type"""
        from asset_loader import asset_loader
        
        # Store different state images
        self.custom_images = {}
        self.custom_animations = {}
        
        if self.enemy_type == EnemyType.MEGA_BOSS:
            # Try to load different mega boss states
            for state in ["normal", "dash", "attack", "hurt", "death"]:
                image_name = f"mega_boss_{state}"
                custom_image = asset_loader.get_image(image_name)
                if custom_image:
                    self.custom_images[state] = custom_image
                    print(f"Loaded mega boss {state} image")
                
                # Check for animation
                if image_name in asset_loader.animations:
                    self.custom_animations[state] = asset_loader.animations[image_name]
                    print(f"Loaded mega boss {state} animation")
    
    def update_animation(self, dt):
        """Update animation state based on current actions"""
        if self.enemy_type == EnemyType.MEGA_BOSS and hasattr(self, 'custom_images'):
            # Determine current state based on actions
            if hasattr(self, 'is_charging_dash') and self.is_charging_dash:
                self.current_state = "dash"
            elif hasattr(self, 'dashing') and self.dashing:
                self.current_state = "dash"
            elif self.hp / self.max_hp < 0.3:
                self.current_state = "hurt"
            else:
                self.current_state = "normal"
            
            # Update image if we have a custom image for this state
            if self.current_state in self.custom_images:
                custom_image = self.custom_images[self.current_state]
                self.image = pygame.transform.scale(custom_image, (self.size, self.size))
    
    def draw(self, screen):
        """Draw the enemy"""
        screen.blit(self.image, self.rect)
    
    def update(self, dt, player_pos):
        """Move towards player and handle abilities"""
        direction = (player_pos - self.pos)
        if direction.length() > 0:
            direction = direction.normalize()
        
        # Update animation
        self.update_animation(dt)
        
        # Update abilities
        self.update_abilities(dt, player_pos)
        
        # Base movement with ability modifiers
        speed_modifier = 1.0
        if self.dashing:
            speed_modifier = 2.0
        if self.shield_active:
            speed_modifier = 0.5
        
        movement = direction * self.speed * speed_modifier * dt
        
        # Add some behavior variation based on enemy type
        if self.enemy_type == EnemyType.FAST:
            # Fast enemies have slight zigzag movement
            zigzag = math.sin(pygame.time.get_ticks() * 0.005) * 30
            perpendicular = pygame.Vector2(-direction.y, direction.x)
            movement += perpendicular * zigzag * dt
        
        self.pos += movement
        self.rect.center = self.pos
    
    def take_damage(self, damage):
        """Apply damage to enemy"""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            return True  # Enemy died
        return False  # Enemy still alive
    
    def setup_sniper(self):
        """Sniper enemy - stays at distance, high damage projectiles"""
        self.max_hp = 25
        self.hp = self.max_hp
        self.speed = 60
        self.damage = 15
        self.size = 20
        self.color = (150, 0, 150)
        self.xp_value = 15
        self.collision_damage = 10
        self.attack_range = 400
        self.attack_cooldown = 2.0
        self.attack_timer = 0
    
    def setup_swarmer(self):
        """Swarmer enemy - small, fast, weak, spawns in groups"""
        self.max_hp = 10
        self.hp = self.max_hp
        self.speed = 200
        self.damage = 5
        self.size = 12
        self.color = (255, 255, 0)
        self.xp_value = 5
        self.collision_damage = 5
    
    def setup_healer(self):
        """Healer enemy - heals other enemies"""
        self.max_hp = 40
        self.hp = self.max_hp
        self.speed = 80
        self.damage = 8
        self.size = 25
        self.color = (0, 255, 0)
        self.xp_value = 20
        self.collision_damage = 8
        self.heal_range = 150
        self.heal_amount = 5
        self.heal_cooldown = 3.0
        self.heal_timer = 0
    
    def setup_bomber(self):
        """Bomber enemy - explodes on death or contact"""
        self.max_hp = 35
        self.hp = self.max_hp
        self.speed = 100
        self.damage = 25
        self.size = 22
        self.color = (255, 100, 0)
        self.xp_value = 18
        self.collision_damage = 20
        self.explosion_radius = 80
        self.has_exploded = False
    
    def setup_mega_boss(self):
        """Mega Boss - ultimate boss with multiple phases"""
        self.max_hp = 1500
        self.hp = self.max_hp
        self.speed = 50
        self.damage = 30
        self.size = 60
        self.color = (255, 0, 255)
        self.xp_value = 200
        self.collision_damage = 25
        self.phase = 1
        self.special_attack_cooldown = 5.0
        self.special_attack_timer = 0
        
        # Mega boss abilities - combines all elite abilities
        self.abilities = ["rage", "summon", "shockwave", "shield", "phase_dash", "multi_attack"]
        self.ability_cooldowns = {
            "rage": 8.0, 
            "summon": 10.0, 
            "shockwave": 12.0,
            "shield": 15.0,
            "phase_dash": 6.0,
            "multi_attack": 4.0
        }
        self.rage_threshold = 0.4  # Activate rage at 40% HP
        self.phase_thresholds = [0.7, 0.4, 0.2]  # Phase changes at these HP percentages
        
        # Dash ability for mega boss
        self.dash_cooldown = 0
        self.dash_target_pos = None
        self.dash_charge_time = 0
        self.dash_charge_duration = 0.8  # 0.8 second pause before dash
        self.is_charging_dash = False
    
    def setup_projectile(self):
        """Projectile enemy - shoots at player from distance"""
        self.max_hp = 30
        self.hp = self.max_hp
        self.speed = 60  # Slow movement
        self.damage = 15
        self.size = 18
        self.color = (255, 255, 100)
        self.xp_value = 25
        self.collision_damage = 10
        self.shoot_cooldown = 2.0
        self.shoot_timer = 0
        self.shoot_range = 400
        self.keep_distance = True
    
    def setup_laser(self):
        """Laser enemy - charges and fires laser beams"""
        self.max_hp = 40
        self.hp = self.max_hp
        self.speed = 40
        self.damage = 35
        self.size = 20
        self.color = (255, 0, 100)
        self.xp_value = 35
        self.collision_damage = 15
        self.laser_cooldown = 4.0
        self.laser_timer = 0
        self.laser_charge_time = 1.5
        self.is_charging_laser = False
        self.laser_charge_timer = 0
        self.laser_range = 600
    
    def setup_mortar(self):
        """Mortar enemy - lobs explosive projectiles"""
        self.max_hp = 45
        self.hp = self.max_hp
        self.speed = 30
        self.damage = 40
        self.size = 24
        self.color = (200, 100, 50)
        self.xp_value = 40
        self.collision_damage = 20
        self.mortar_cooldown = 3.5
        self.mortar_timer = 0
        self.mortar_range = 500
        self.projectile_speed = 200
        self.explosion_radius = 60
    
    def setup_summoner(self):
        """Summoner enemy - spawns other enemies"""
        self.max_hp = 60
        self.hp = self.max_hp
        self.speed = 50
        self.damage = 10
        self.size = 28
        self.color = (150, 0, 150)
        self.xp_value = 50
        self.collision_damage = 15
        self.summon_cooldown = 8.0
        self.summon_timer = 0
        self.max_summons = 3
        self.current_summons = 0
        self.summon_types = [EnemyType.SWARMER, EnemyType.BASIC]
    
    def setup_assassin(self):
        """Assassin enemy - stealth and high burst damage"""
        self.max_hp = 35
        self.hp = self.max_hp
        self.speed = 180
        self.damage = 50
        self.size = 16
        self.color = (100, 100, 100)
        self.xp_value = 45
        self.collision_damage = 40
        self.stealth_cooldown = 10.0
        self.stealth_timer = 0
        self.is_stealthed = False
        self.stealth_duration = 3.0
        self.stealth_alpha = 0.3
        self.backstab_multiplier = 2.0
    
    def update_abilities(self, dt, player_pos):
        """Update ability cooldowns and trigger abilities"""
        # Update cooldowns
        for ability in self.ability_cooldowns:
            if self.ability_cooldowns[ability] > 0:
                self.ability_cooldowns[ability] -= dt
        
        # Check for ability triggers
        if self.enemy_type == EnemyType.BOSS:
            self.handle_boss_abilities(dt, player_pos)
        elif self.enemy_type == EnemyType.TANK:
            self.handle_tank_abilities(dt, player_pos)
        elif self.enemy_type == EnemyType.FAST:
            self.handle_fast_abilities(dt, player_pos)
        elif self.enemy_type == EnemyType.HEALER:
            self.handle_healer_abilities(dt, player_pos)
        elif self.enemy_type == EnemyType.BOMBER:
            self.handle_bomber_abilities(dt, player_pos)
        elif self.enemy_type == EnemyType.PROJECTILE:
            self.handle_projectile_abilities(dt, player_pos)
        elif self.enemy_type == EnemyType.LASER:
            self.handle_laser_abilities(dt, player_pos)
        elif self.enemy_type == EnemyType.MORTAR:
            self.handle_mortar_abilities(dt, player_pos)
        elif self.enemy_type == EnemyType.SUMMONER:
            self.handle_summoner_abilities(dt, player_pos)
        elif self.enemy_type == EnemyType.ASSASSIN:
            self.handle_assassin_abilities(dt, player_pos)
        elif self.enemy_type == EnemyType.MEGA_BOSS:
            self.handle_mega_boss_abilities(dt, player_pos)
    
    def handle_tank_abilities(self, dt, player_pos):
        """Handle tank special abilities"""
        # Shield ability - temporary invulnerability
        if "shield" in self.abilities and self.ability_cooldowns["shield"] <= 0:
            if self.hp / self.max_hp < 0.5:  # Activate shield at 50% HP
                self.activate_shield()
                self.ability_cooldowns["shield"] = 10.0
        
        # Stomp ability - area damage when close
        if "stomp" in self.abilities and self.ability_cooldowns["stomp"] <= 0:
            distance_to_player = (player_pos - self.pos).length()
            if distance_to_player < 100:
                self.activate_stomp()
                self.ability_cooldowns["stomp"] = 6.0
    
    def handle_fast_abilities(self, dt, player_pos):
        """Handle fast enemy special abilities"""
        # Dash ability - burst of speed
        if "dash" in self.abilities and self.ability_cooldowns["dash"] <= 0:
            distance_to_player = (player_pos - self.pos).length()
            if 150 < distance_to_player < 300:  # Dash at medium range
                self.activate_dash()
                self.ability_cooldowns["dash"] = 4.0
        
        # Phase ability - temporary invulnerability and speed boost
        if "phase" in self.abilities and self.ability_cooldowns["phase"] <= 0:
            if self.hp / self.max_hp < 0.3:  # Phase at low HP
                self.activate_phase()
                self.ability_cooldowns["phase"] = 8.0
    
    def handle_boss_abilities(self, dt, player_pos):
        """Handle boss special abilities"""
        hp_percentage = self.hp / self.max_hp
        
        # Rage ability - activate at low HP
        if hp_percentage < self.rage_threshold and "rage" in self.abilities and self.ability_cooldowns["rage"] <= 0:
            self.activate_rage()
            self.ability_cooldowns["rage"] = 10.0
        
        # Summon ability - spawn smaller enemies
        if "summon" in self.abilities and self.ability_cooldowns["summon"] <= 0:
            distance_to_player = (player_pos - self.pos).length()
            if distance_to_player < 300:  # Only summon when close to player
                self.activate_summon()
                self.ability_cooldowns["summon"] = 12.0
        
        # Shockwave ability - area damage
        if "shockwave" in self.abilities and self.ability_cooldowns["shockwave"] <= 0:
            distance_to_player = (player_pos - self.pos).length()
            if distance_to_player < 200:  # Only shockwave when close
                self.activate_shockwave()
                self.ability_cooldowns["shockwave"] = 15.0
    
    def handle_mega_boss_abilities(self, dt, player_pos):
        """Handle mega boss special abilities - combines all elite abilities"""
        hp_percentage = self.hp / self.max_hp
        
        # Phase management
        for i, threshold in enumerate(self.phase_thresholds):
            if hp_percentage < threshold and self.phase == i + 1:
                self.phase = i + 2
                self.activate_phase_change()
        
        # Rage ability - activate at low HP
        if hp_percentage < self.rage_threshold and "rage" in self.abilities and self.ability_cooldowns["rage"] <= 0:
            self.activate_rage()
            self.ability_cooldowns["rage"] = 10.0
        
        # Summon ability - spawn smaller enemies
        if "summon" in self.abilities and self.ability_cooldowns["summon"] <= 0:
            distance_to_player = (player_pos - self.pos).length()
            if distance_to_player < 400:  # Larger summon range for mega boss
                self.activate_summon()
                self.ability_cooldowns["summon"] = 15.0
        
        # Shockwave ability - area damage
        if "shockwave" in self.abilities and self.ability_cooldowns["shockwave"] <= 0:
            distance_to_player = (player_pos - self.pos).length()
            if distance_to_player < 300:  # Larger shockwave range
                self.activate_shockwave()
                self.ability_cooldowns["shockwave"] = 18.0
        
        # Shield ability - temporary invulnerability
        if "shield" in self.abilities and self.ability_cooldowns["shield"] <= 0:
            if hp_percentage < 0.6:  # Earlier shield activation
                self.activate_shield()
                self.ability_cooldowns["shield"] = 20.0
        
        # Phase dash ability - teleport and attack
        if "phase_dash" in self.abilities and self.ability_cooldowns["phase_dash"] <= 0:
            distance_to_player = (player_pos - self.pos).length()
            if 200 < distance_to_player < 500:  # Dash at longer range
                self.activate_phase_dash(player_pos)
                self.ability_cooldowns["phase_dash"] = 8.0
        
        # Multi attack ability - rapid attacks
        if "multi_attack" in self.abilities and self.ability_cooldowns["multi_attack"] <= 0:
            distance_to_player = (player_pos - self.pos).length()
            if distance_to_player < 250:  # Close range multi attack
                self.activate_multi_attack()
                self.ability_cooldowns["multi_attack"] = 6.0
        
        # Dash ability - charge and dash to player's previous position
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
        
        # Start dash charge
        if self.dash_cooldown <= 0 and not self.is_charging_dash:
            distance_to_player = (player_pos - self.pos).length()
            if 200 < distance_to_player < 500:  # Start dash at medium range
                self.is_charging_dash = True
                self.dash_charge_time = 0
                self.dash_target_pos = player_pos.copy()  # Store player's current position
                self.special_effects.append(("dash_charge", pygame.time.get_ticks()))
        
        # Update dash charge
        if self.is_charging_dash:
            self.dash_charge_time += dt
            if self.dash_charge_time >= self.dash_charge_duration:
                # Execute dash to stored position
                self.execute_dash()
                self.is_charging_dash = False
                self.dash_cooldown = 8.0  # Reset cooldown
    
    def activate_rage(self):
        """Boss rage - increase speed and damage"""
        self.speed *= 2
        self.collision_damage *= 1.5
        self.color = (255, 50, 50)  # Darker red to indicate rage
        self.create_visual()  # Update visual
    
    def activate_summon(self):
        """Boss summon - spawn smaller enemies"""
        # This would need access to the enemy group - for now just visual effect
        self.special_effects.append(("summon", pygame.time.get_ticks()))
    
    def activate_shockwave(self):
        """Boss shockwave - area damage"""
        self.special_effects.append(("shockwave", pygame.time.get_ticks()))
    
    def activate_shield(self):
        """Tank shield - temporary damage reduction"""
        self.shield_active = True
        self.color = (100, 150, 255)  # Blue shield color
        self.create_visual()
        # Shield will be deactivated after duration in update
    
    def activate_stomp(self):
        """Tank stomp - area damage"""
        self.special_effects.append(("stomp", pygame.time.get_ticks()))
    
    def activate_dash(self):
        """Fast dash - burst of speed"""
        self.dashing = True
        # Dash will be deactivated after short duration
    
    def activate_phase(self):
        """Fast phase - temporary invulnerability"""
        self.phased = True
        self.color = (200, 200, 255)  # Ethereal blue color
        self.create_visual()
        # Phase will be deactivated after duration
    
    def activate_phase_change(self):
        """Mega boss phase change - dramatic transformation"""
        self.speed *= 1.3
        self.collision_damage *= 1.2
        # Change color based on phase
        phase_colors = [(255, 0, 255), (255, 100, 0), (255, 255, 0)]
        if self.phase <= len(phase_colors):
            self.color = phase_colors[self.phase - 1]
        self.create_visual()
        self.special_effects.append(("phase_change", pygame.time.get_ticks()))
    
    def activate_phase_dash(self, player_pos):
        """Mega boss phase dash - teleport towards player"""
        # Store old position for effect
        old_pos = self.pos.copy()
        
        # Teleport closer to player
        direction = (player_pos - self.pos).normalize()
        new_pos = player_pos - direction * 150  # Stop 150 pixels from player
        self.pos = new_pos
        self.rect.center = self.pos
        
        # Create visual effect
        self.special_effects.append(("phase_dash", pygame.time.get_ticks(), old_pos))
        
        # Brief speed boost
        self.dashing = True
        self.speed *= 2
    
    def activate_multi_attack(self):
        """Mega boss multi attack - rapid consecutive attacks"""
        self.special_effects.append(("multi_attack", pygame.time.get_ticks()))
        # Temporarily increase collision damage
        self.collision_damage *= 2
    
    def execute_dash(self):
        """Execute mega boss dash to stored position"""
        if self.dash_target_pos:
            # Store old position for visual effect
            old_pos = self.pos.copy()
            
            # Dash to the stored position (where player was 0.8 seconds ago)
            self.pos = self.dash_target_pos
            self.rect.center = self.pos
            
            # Create visual effect
            self.special_effects.append(("dash_execute", pygame.time.get_ticks(), old_pos, self.pos))
            
            # Clear target
            self.dash_target_pos = None
    
    def handle_healer_abilities(self, dt, player_pos):
        """Handle healer special abilities"""
        # Update heal timer
        if self.heal_timer > 0:
            self.heal_timer -= dt
        
        # Heal nearby enemies
        if self.heal_timer <= 0:
            # This would need access to other enemies - for now add visual effect
            self.special_effects.append(("heal", pygame.time.get_ticks()))
            self.heal_timer = self.heal_cooldown
    
    def handle_bomber_abilities(self, dt, player_pos):
        """Handle bomber special abilities"""
        # Explode when close to player or on death
        distance_to_player = (player_pos - self.pos).length()
        if distance_to_player < 50 and not self.has_exploded:
            self.explode()
    
    def handle_projectile_abilities(self, dt, player_pos):
        """Handle projectile enemy special abilities"""
        # Update shoot timer
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        
        # Shoot at player from distance
        distance_to_player = (player_pos - self.pos).length()
        if self.shoot_timer <= 0 and distance_to_player < self.shoot_range:
            self.shoot_timer = self.shoot_cooldown
            self.special_effects.append(("shoot", pygame.time.get_ticks(), player_pos))
    
    def handle_laser_abilities(self, dt, player_pos):
        """Handle laser enemy special abilities"""
        # Update laser timer
        if self.laser_timer > 0:
            self.laser_timer -= dt
        
        # Charge and fire laser
        distance_to_player = (player_pos - self.pos).length()
        if self.laser_timer <= 0 and distance_to_player < self.laser_range:
            if not self.is_charging_laser:
                # Start charging
                self.is_charging_laser = True
                self.laser_charge_timer = self.laser_charge_time
                self.special_effects.append(("laser_charge", pygame.time.get_ticks()))
            else:
                # Fire laser
                self.is_charging_laser = False
                self.laser_timer = self.laser_cooldown
                self.special_effects.append(("laser_fire", pygame.time.get_ticks(), player_pos))
        
        # Update charge timer
        if self.is_charging_laser and self.laser_charge_timer > 0:
            self.laser_charge_timer -= dt
            if self.laser_charge_timer <= 0:
                self.is_charging_laser = False
                self.laser_timer = self.laser_cooldown
                self.special_effects.append(("laser_fire", pygame.time.get_ticks(), player_pos))
    
    def handle_mortar_abilities(self, dt, player_pos):
        """Handle mortar enemy special abilities"""
        # Update mortar timer
        if self.mortar_timer > 0:
            self.mortar_timer -= dt
        
        # Lob explosive projectiles
        distance_to_player = (player_pos - self.pos).length()
        if self.mortar_timer <= 0 and distance_to_player < self.mortar_range:
            self.mortar_timer = self.mortar_cooldown
            self.special_effects.append(("mortar_fire", pygame.time.get_ticks(), player_pos))
    
    def handle_summoner_abilities(self, dt, player_pos):
        """Handle summoner special abilities"""
        # Update summon timer
        if self.summon_timer > 0:
            self.summon_timer -= dt
        
        # Summon enemies
        if self.summon_timer <= 0 and self.current_summons < self.max_summons:
            distance_to_player = (player_pos - self.pos).length()
            if distance_to_player < 300:
                self.summon_timer = self.summon_cooldown
                self.current_summons += 1
                self.special_effects.append(("summon", pygame.time.get_ticks()))
    
    def handle_assassin_abilities(self, dt, player_pos):
        """Handle assassin special abilities"""
        # Update stealth timer
        if self.stealth_timer > 0:
            self.stealth_timer -= dt
        
        # Enter stealth
        if self.stealth_timer <= 0 and not self.is_stealthed:
            distance_to_player = (player_pos - self.pos).length()
            if 200 < distance_to_player < 400:  # Stealth at medium range
                self.is_stealthed = True
                self.stealth_timer = self.stealth_duration
                self.special_effects.append(("stealth", pygame.time.get_ticks()))
        
        # Exit stealth when close to player
        if self.is_stealthed:
            distance_to_player = (player_pos - self.pos).length()
            if distance_to_player < 100:
                self.is_stealthed = False
                self.stealth_timer = self.stealth_cooldown
                self.special_effects.append(("backstab", pygame.time.get_ticks()))
    
    def explode(self):
        """Handle bomber explosion"""
        if not self.has_exploded:
            self.has_exploded = True
            self.special_effects.append(("explosion", pygame.time.get_ticks(), self.pos, self.explosion_radius))
    
    def draw_health_bar(self, screen):
        """Draw health bar above enemy"""
        if self.hp < self.max_hp:
            bar_width = max(30, self.size * 2)
            bar_height = 4
            bar_x = self.rect.centerx - bar_width // 2
            bar_y = self.rect.top - 10
            
            # Background
            pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Health
            health_width = int(bar_width * (self.hp / self.max_hp))
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, health_width, bar_height))
            
            # Draw shield indicator if active
            if hasattr(self, 'shield_active') and self.shield_active:
                pygame.draw.circle(screen, (100, 150, 255), (self.rect.centerx, bar_y + bar_height // 2), 8, 2)
