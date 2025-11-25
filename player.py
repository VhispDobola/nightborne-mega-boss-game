import pygame
import math
from projectile import Projectile, ProjectileType, Weapon
from sounds import play_sound
from powerups import PowerUpType

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        # Visual setup
        self.original_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.original_image, (0, 200, 255), [(20,0),(40,40),(0,40)])
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        
        # Core stats
        self.max_hp = 100
        self.hp = self.max_hp
        self.speed = 280
        self.damage = 10
        self.fire_rate = 1.0  # shots per second
        self.projectile_speed = 650
        self.pickup_range = 80
        
        # Weapon system
        self.weapon_level = 1
        self.weapon = Weapon(ProjectileType.BASIC)
        self.piercing = False
        
        # Shooting system
        self.shoot_timer = 0
        self.is_shooting = False
        
        # XP and leveling
        self.xp = 0
        self.level = 1
        self.xp_to_next_level = 50
        
        # Power-up system
        self.power_up_effects = {}  # {power_type: [duration, value]}
        self.base_speed = self.speed
        self.base_damage = self.damage
        self.base_fire_rate = self.fire_rate
        self.shield_active = False
        self.invincible = False
        
    def update(self, dt):
        # Movement
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(
            (keys[pygame.K_d] - keys[pygame.K_a]),
            (keys[pygame.K_s] - keys[pygame.K_w])
        )
        if move.length() > 0:
            move = move.normalize()
        
        self.pos += move * self.speed * dt
        self.rect.center = self.pos
        
        # Keep player on screen
        screen_rect = pygame.display.get_surface().get_rect()
        self.pos.x = max(screen_rect.left + 20, min(screen_rect.right - 20, self.pos.x))
        self.pos.y = max(screen_rect.top + 20, min(screen_rect.bottom - 20, self.pos.y))
        self.rect.center = self.pos
        
        # Update power-up effects
        self.update_power_ups(dt)
        
        # Face movement direction (or mouse if manual aim)
        if move.length() > 0:
            angle = math.degrees(math.atan2(-move.y, move.x))
        else:
            mouse_pos = pygame.mouse.get_pos()
            dx, dy = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
            angle = math.degrees(math.atan2(-dy, dx))
        
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Update shoot timer
        # Note: Timer is handled in manual_shoot method now
    
    def manual_shoot(self, dt, projectile_group, mouse_pos):
        """Manual shooting with mouse hold and fire rate control"""
        fire_threshold = 1.0 / self.weapon.fire_rate
        if self.is_shooting:
            self.shoot_timer += dt
            
            if self.shoot_timer >= fire_threshold:
                self.shoot_timer = 0
                self.shoot_toward_mouse(projectile_group, mouse_pos)
                play_sound('shoot')
        else:
            # Reset timer when not shooting
            self.shoot_timer = 0
    
    def shoot_toward_mouse(self, projectile_group, mouse_pos):
        """Shoot projectiles toward mouse position using weapon system"""
        # Use weapon to create projectiles
        projectiles = self.weapon.create_projectiles(
            self.rect.center, mouse_pos, 
            damage_multiplier=1.0 + (self.weapon_level - 1) * 0.3,
            speed_multiplier=1.0,
            piercing=self.piercing
        )
        
        # Set enhancement level on projectiles and add to group
        for projectile in projectiles:
            projectile.level = self.weapon_level
            projectile_group.add(projectile)
            
            # Track shot statistics (if game reference is available)
            if hasattr(self, 'game') and self.game:
                self.game.update_stats("shot_fired")
    
    def shoot(self, projectile_group):
        """Shoot projectiles at nearest enemy"""
        # Get direction to shoot (forward by default)
        direction = pygame.Vector2(1, 0)  # Default forward
        
        # Create projectiles
        if self.projectile_count == 1:
            # Single projectile
            projectile = Projectile(self.rect.center, direction, self.damage, 
                                  self.projectile_speed, self.weapon_type, self.piercing)
            projectile_group.add(projectile)
        else:
            # Multiple projectiles in spread
            spread_angle = 30  # Total spread angle in degrees
            angle_step = spread_angle / (self.projectile_count - 1) if self.projectile_count > 1 else 0
            start_angle = -spread_angle / 2
            
            for i in range(self.projectile_count):
                angle = start_angle + (i * angle_step)
                spread_direction = direction.rotate(angle)
                projectile = Projectile(self.rect.center, spread_direction, self.damage,
                                      self.projectile_speed, self.weapon_type, self.piercing)
                projectile_group.add(projectile)
    
    def add_xp(self, amount):
        """Add XP and check for level up"""
        self.xp += amount
    
    def check_level_up(self):
        """Check if player leveled up and handle level up"""
        if self.xp >= self.xp_to_next_level:
            self.level_up()
            return True
        return False
    
    def level_up(self):
        """Handle level up"""
        self.level += 1
        self.xp = 0
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)  # Increase XP requirement
        
        # Restore some health on level up
        heal_amount = int(self.max_hp * 0.3)
        self.hp = min(self.hp + heal_amount, self.max_hp)
    
    def take_damage(self, amount):
        """Take damage, considering power-up effects"""
        if self.invincible:
            return  # No damage when invincible
        
        if self.shield_active:
            amount = int(amount * 0.5)  # Shield reduces damage by 50%
        
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
    
    def add_power_up_effect(self, power_type, duration, value):
        """Add a power-up effect to the player"""
        self.power_up_effects[power_type] = [duration, value]
        self.apply_power_up_effects()
    
    def update_power_ups(self, dt):
        """Update all active power-up effects"""
        effects_to_remove = []
        
        for power_type, [duration, value] in self.power_up_effects.items():
            new_duration = duration - dt
            if new_duration <= 0:
                effects_to_remove.append(power_type)
            else:
                self.power_up_effects[power_type] = [new_duration, value]
        
        # Remove expired effects
        for power_type in effects_to_remove:
            del self.power_up_effects[power_type]
        
        # Reapply effects
        self.apply_power_up_effects()
    
    def apply_power_up_effects(self):
        """Apply all active power-up effects to player stats"""
        # Reset to base stats
        self.speed = self.base_speed
        self.damage = self.base_damage
        self.fire_rate = self.base_fire_rate
        self.shield_active = False
        self.invincible = False
        
        # Apply active effects
        for power_type, [duration, value] in self.power_up_effects.items():
            if power_type == PowerUpType.SPEED_BOOST:
                self.speed = int(self.base_speed * value)
            elif power_type == PowerUpType.DAMAGE_BOOST:
                self.damage = int(self.base_damage * value)
            elif power_type == PowerUpType.RAPID_FIRE:
                self.fire_rate = self.base_fire_rate * value
            elif power_type == PowerUpType.SHIELD:
                self.shield_active = True
            elif power_type == PowerUpType.INVINCIBILITY:
                self.invincible = True
            elif power_type == PowerUpType.MULTI_SHOT:
                # This is handled in shooting logic
                pass
            elif power_type == PowerUpType.PIERCING:
                self.piercing = True
            elif power_type == PowerUpType.EXPLOSIVE_SHOTS:
                # This is handled in projectile creation
                pass
    
    def heal(self, amount):
        """Heal the player"""
        self.hp = min(self.hp + amount, self.max_hp)
    
    def get_power_up_multiplier(self, power_type):
        """Get the multiplier for a specific power-up type"""
        if power_type in self.power_up_effects:
            return self.power_up_effects[power_type][1]
        return 1.0
