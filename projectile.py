import pygame
import math
from enum import Enum

class ProjectileType(Enum):
    BASIC = "basic"
    PIERCING = "piercing"
    EXPLOSIVE = "explosive"
    RAPID = "rapid"
    SPREAD = "spread"
    BOUNCING = "bouncing"
    HOMING = "homing"
    LASER = "laser"
    HYBRID = "hybrid"

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, damage, speed, projectile_type=ProjectileType.BASIC, piercing=False, level=1):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.direction = direction.normalize() if direction.length() > 0 else pygame.Vector2(1, 0)
        self.damage = damage
        self.base_damage = damage
        self.speed = speed
        self.projectile_type = projectile_type
        self.piercing = piercing or projectile_type == ProjectileType.PIERCING
        self.level = level  # Enhancement level
        self.hybrid_types = []  # For hybrid projectiles
        
        # Visual setup based on type and level
        self.size = 8 + (level - 1) * 2
        self.color = self.get_projectile_color()
        self.create_visual()
        
        # Physics
        self.vel = self.direction * self.speed
        self.rect = self.image.get_rect(center=self.pos)
        
        # Lifetime
        self.lifetime = self.get_lifetime()
        self.age = 0
        
        # Special properties
        self.bounces = 0
        self.max_bounces = 2 + (level - 1) if projectile_type == ProjectileType.BOUNCING else 0
        self.explosion_radius = 50 + (level - 1) * 15 if projectile_type == ProjectileType.EXPLOSIVE else 0
        self.homing_strength = 0.1 + (level - 1) * 0.05 if projectile_type == ProjectileType.HOMING else 0
        self.has_exploded = False

    def get_projectile_color(self):
        """Get color based on projectile type and level"""
        base_colors = {
            ProjectileType.BASIC: (255, 255, 0),
            ProjectileType.PIERCING: (255, 100, 255),
            ProjectileType.EXPLOSIVE: (255, 150, 0),
            ProjectileType.RAPID: (100, 200, 255),
            ProjectileType.SPREAD: (0, 255, 100),
            ProjectileType.BOUNCING: (255, 255, 100),
            ProjectileType.HOMING: (255, 0, 100),
            ProjectileType.LASER: (255, 0, 0),
            ProjectileType.HYBRID: (255, 255, 255)  # White for hybrids
        }
        
        if self.projectile_type == ProjectileType.HYBRID and self.hybrid_types:
            # Mix colors from hybrid types
            color_map = {
                ProjectileType.BASIC: (255, 255, 0),
                ProjectileType.PIERCING: (255, 100, 255),
                ProjectileType.EXPLOSIVE: (255, 150, 0),
                ProjectileType.RAPID: (100, 200, 255),
                ProjectileType.SPREAD: (0, 255, 100),
                ProjectileType.BOUNCING: (255, 255, 100),
                ProjectileType.HOMING: (255, 0, 100),
                ProjectileType.LASER: (255, 0, 0)
            }
            
            colors = [color_map.get(pt, (255, 255, 255)) for pt in self.hybrid_types]
            if len(colors) >= 2:
                # Average the colors
                color = tuple(sum(c[i] for c in colors) // len(colors) for i in range(3))
            else:
                color = colors[0] if colors else (255, 255, 255)
        else:
            color = base_colors.get(self.projectile_type, (255, 255, 0))
        
        # Brighten color based on level
        if self.level > 1:
            color = tuple(min(255, c + (self.level - 1) * 20) for c in color)
        
        return color
    
    def get_lifetime(self):
        """Get lifetime based on projectile type"""
        lifetimes = {
            ProjectileType.BASIC: 2.0,
            ProjectileType.PIERCING: 3.0,
            ProjectileType.EXPLOSIVE: 1.5,
            ProjectileType.RAPID: 1.0,
            ProjectileType.SPREAD: 1.5,
            ProjectileType.BOUNCING: 4.0,
            ProjectileType.HOMING: 3.0,
            ProjectileType.LASER: 0.5
        }
        return lifetimes.get(self.projectile_type, 2.0)
    
    def create_visual(self):
        """Create visual based on projectile type and level"""
        if self.projectile_type == ProjectileType.BASIC:
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
            
        elif self.projectile_type == ProjectileType.PIERCING:
            self.image = pygame.Surface((self.size * 2 + 4, self.size * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size + 2, self.size + 2), self.size + 2)
            
        elif self.projectile_type == ProjectileType.EXPLOSIVE:
            self.image = pygame.Surface((self.size * 2 + 4, self.size * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size + 2, self.size + 2), self.size + 2)
            
        elif self.projectile_type == ProjectileType.RAPID:
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
            
        elif self.projectile_type == ProjectileType.SPREAD:
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
            
        elif self.projectile_type == ProjectileType.BOUNCING:
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
            
        elif self.projectile_type == ProjectileType.HOMING:
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
            
        elif self.projectile_type == ProjectileType.LASER:
            # Create omnidirectional laser effect
            laser_length = max(20, self.size * 4)
            laser_width = max(4, self.size)
            # Create larger surface for omnidirectional effect
            surface_size = laser_length * 2 + 20
            self.image = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
            center = surface_size // 2
            
            # Draw laser lines in all directions (8 directions)
            for angle in range(0, 360, 45):
                end_x = center + int(laser_length * math.cos(math.radians(angle)))
                end_y = center + int(laser_length * math.sin(math.radians(angle)))
                pygame.draw.line(self.image, self.color, (center, center), (end_x, end_y), laser_width)
            
            # Add center glow
            pygame.draw.circle(self.image, self.color, (center, center), laser_width + 2)
            
        elif self.projectile_type == ProjectileType.HYBRID:
            # Create hybrid visual combining multiple effects
            actual_size = max(16, self.size * 2)
            self.image = pygame.Surface((actual_size + 8, actual_size + 8), pygame.SRCALPHA)
            center = (actual_size + 8) // 2
            
            # Draw base circle
            pygame.draw.circle(self.image, self.color, (center, center), actual_size // 2)
            
            # Add effects based on hybrid types
            if self.hybrid_types:
                # Add inner glow for explosive component
                if ProjectileType.EXPLOSIVE in self.hybrid_types:
                    glow_color = tuple(min(255, c + 50) for c in self.color)
                    pygame.draw.circle(self.image, glow_color, (center, center), actual_size // 3)
                
                # Add piercing effect
                if ProjectileType.PIERCING in self.hybrid_types:
                    pygame.draw.circle(self.image, (255, 255, 255), (center, center), actual_size // 2, 2)
                
                # Add spread effect (multiple small dots)
                if ProjectileType.SPREAD in self.hybrid_types:
                    for angle in range(0, 360, 60):
                        dot_x = center + int(actual_size // 2 * math.cos(math.radians(angle)))
                        dot_y = center + int(actual_size // 2 * math.sin(math.radians(angle)))
                        pygame.draw.circle(self.image, (255, 255, 255), (dot_x, dot_y), 2)
            
        else:  # Default
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size // 2, self.size // 2), self.size // 2)
    
    def update(self, dt, enemies=None):
        """Update projectile position and lifetime"""
        # Special behaviors based on type
        if self.projectile_type == ProjectileType.HOMING and enemies:
            # Home towards nearest enemy
            nearest_enemy = None
            min_distance = float('inf')
            
            for enemy in enemies:
                distance = (enemy.pos - self.pos).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_enemy = enemy
            
            if nearest_enemy and min_distance < 400:  # Home within 400 pixels
                direction_to_enemy = (nearest_enemy.pos - self.pos).normalize()
                # Stronger homing for better tracking
                self.vel = self.vel.lerp(direction_to_enemy * self.speed, self.homing_strength * dt * 60)
                self.direction = self.vel.normalize()
        
        elif self.projectile_type == ProjectileType.BOUNCING:
            # Check for screen edge collisions
            screen_rect = pygame.display.get_surface().get_rect()
            
            if self.rect.left <= 0 or self.rect.right >= screen_rect.width:
                self.vel.x *= -1
                self.direction.x *= -1
                self.bounces += 1
                
            if self.rect.top <= 0 or self.rect.bottom >= screen_rect.height:
                self.vel.y *= -1
                self.direction.y *= -1
                self.bounces += 1
        
        elif self.projectile_type == ProjectileType.HYBRID and self.hybrid_types:
            # Combine behaviors from hybrid types
            if ProjectileType.HOMING in self.hybrid_types and enemies:
                # Homing behavior
                nearest_enemy = None
                min_distance = float('inf')
                
                for enemy in enemies:
                    distance = (enemy.pos - self.pos).length()
                    if distance < min_distance:
                        min_distance = distance
                        nearest_enemy = enemy
                
                if nearest_enemy and min_distance < 350:
                    direction_to_enemy = (nearest_enemy.pos - self.pos).normalize()
                    homing_strength = 0.08  # Better homing for hybrids
                    self.vel = self.vel.lerp(direction_to_enemy * self.speed, homing_strength * dt * 60)
                    self.direction = self.vel.normalize()
            
            if ProjectileType.BOUNCING in self.hybrid_types:
                # Bouncing behavior
                screen_rect = pygame.display.get_surface().get_rect()
                
                if self.rect.left <= 0 or self.rect.right >= screen_rect.width:
                    self.vel.x *= -1
                    self.direction.x *= -1
                    
                if self.rect.top <= 0 or self.rect.bottom >= screen_rect.height:
                    self.vel.y *= -1
                    self.direction.y *= -1
        
        # Update position
        self.pos += self.vel * dt
        self.rect.center = self.pos
        
        # Update age
        self.age += dt
        
        # Destroy if too old or off-screen (with larger margin)
        screen_rect = pygame.display.get_surface().get_rect()
        # Expand screen bounds to give projectiles more room
        expanded_rect = screen_rect.inflate(200, 200)
        
        if self.age >= self.lifetime:
            self.kill()
        elif not expanded_rect.collidepoint(self.rect.center):
            self.kill()
        
        # Destroy if exceeded bounces (only for bouncing projectiles)
        if self.projectile_type == ProjectileType.BOUNCING and self.bounces >= self.max_bounces:
            self.kill()
    
    def on_hit(self, enemy):
        """Handle projectile hitting enemy"""
        # Handle explosive behavior
        is_explosive = False
        damage = self.damage
        
        if self.projectile_type == ProjectileType.EXPLOSIVE and not self.has_exploded:
            self.has_exploded = True
            damage = self.damage * (1.5 + self.level * 0.2)
            is_explosive = True
        
        elif self.projectile_type == ProjectileType.HYBRID and self.hybrid_types:
            if ProjectileType.EXPLOSIVE in self.hybrid_types and not self.has_exploded:
                self.has_exploded = True
                damage = self.damage * (1.3 + self.level * 0.15)  # Slightly weaker explosion for hybrids
                is_explosive = True
        
        return damage, is_explosive  # (damage, is_explosive)
    
    def get_explosion_data(self):
        """Get explosion data for area damage"""
        if self.projectile_type == ProjectileType.EXPLOSIVE:
            return {
                'pos': self.pos,
                'radius': self.explosion_radius,
                'damage': self.damage * 0.5,  # Area damage is reduced
                'level': self.level
            }
        elif self.projectile_type == ProjectileType.HYBRID and self.hybrid_types:
            if ProjectileType.EXPLOSIVE in self.hybrid_types:
                return {
                    'pos': self.pos,
                    'radius': 40 + (self.level - 1) * 10,  # Smaller radius for hybrids
                    'damage': self.damage * 0.4,  # Even more reduced area damage
                    'level': self.level
                }
        return None

class Weapon:
    """Weapon system for managing different projectile types"""
    def __init__(self, weapon_type=ProjectileType.BASIC):
        self.weapon_type = weapon_type
        self.base_damage = 10
        self.base_speed = 650
        self.fire_rate = 1.0
        self.projectile_count = 1
        self.spread_angle = 15  # degrees
        self.hybrid_types = []  # For hybrid weapons
        
        # Set stats based on weapon type
        if weapon_type == ProjectileType.BASIC:
            self.base_damage = 10
            self.fire_rate = 1.0
            self.projectile_count = 1
            
        elif weapon_type == ProjectileType.PIERCING:
            self.base_damage = 7
            self.fire_rate = 0.8
            self.projectile_count = 1
            
        elif weapon_type == ProjectileType.EXPLOSIVE:
            self.base_damage = 15
            self.fire_rate = 0.6
            self.projectile_count = 1
            
        elif weapon_type == ProjectileType.RAPID:
            self.base_damage = 7
            self.fire_rate = 4.5
            self.projectile_count = 1
            
        elif weapon_type == ProjectileType.SPREAD:
            self.base_damage = 8
            self.fire_rate = 1.2
            self.projectile_count = 3
            self.spread_angle = 30
            
        elif weapon_type == ProjectileType.BOUNCING:
            self.base_damage = 12
            self.fire_rate = 0.7
            self.projectile_count = 1
            
        elif weapon_type == ProjectileType.HOMING:
            self.base_damage = 8
            self.fire_rate = 1.5
            self.projectile_count = 1
            
        elif weapon_type == ProjectileType.LASER:
            self.base_damage = 20
            self.fire_rate = 4.0
            self.projectile_count = 1
    
    def create_hybrid(self, other_weapon):
        """Create a hybrid weapon combining this weapon with another"""
        hybrid = Weapon(ProjectileType.BASIC)  # Start with basic
        hybrid.hybrid_types = [self.weapon_type, other_weapon.weapon_type]
        
        # Combine damage
        hybrid.base_damage = (self.base_damage + other_weapon.base_damage) * 0.8
        
        # Average speed
        hybrid.base_speed = (self.base_speed + other_weapon.base_speed) / 2
        
        # Use better fire rate
        hybrid.fire_rate = max(self.fire_rate, other_weapon.fire_rate)
        
        # Combine projectile counts
        hybrid.projectile_count = max(self.projectile_count, other_weapon.projectile_count)
        
        # Use larger spread angle
        hybrid.spread_angle = max(self.spread_angle, other_weapon.spread_angle)
        
        return hybrid
    
    def create_projectiles(self, pos, target_pos, damage_multiplier=1.0, speed_multiplier=1.0, piercing=False):
        """Create projectiles based on weapon settings"""
        projectiles = []
        
        # Calculate direction to target
        direction = pygame.Vector2(target_pos) - pygame.Vector2(pos)
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.Vector2(1, 0)  # Default forward
        
        # Create multiple projectiles if needed
        if self.projectile_count == 1:
            # Single projectile
            projectile_type = self.weapon_type
            if self.hybrid_types:
                projectile_type = ProjectileType.HYBRID  # Custom hybrid type
            
            projectile = Projectile(
                pos, direction, 
                self.base_damage * damage_multiplier,
                self.base_speed * speed_multiplier,
                projectile_type, piercing, level=1
            )
            
            # Set hybrid properties if applicable
            if self.hybrid_types:
                projectile.hybrid_types = self.hybrid_types
            
            projectiles.append(projectile)
        else:
            # Multiple projectiles in spread
            angle_step = self.spread_angle / (self.projectile_count - 1) if self.projectile_count > 1 else 0
            start_angle = -self.spread_angle / 2
            
            for i in range(self.projectile_count):
                angle = start_angle + (i * angle_step)
                spread_direction = direction.rotate(angle)
                
                projectile_type = self.weapon_type
                if self.hybrid_types:
                    projectile_type = ProjectileType.HYBRID
                
                projectile = Projectile(
                    pos, spread_direction,
                    self.base_damage * damage_multiplier,
                    self.base_speed * speed_multiplier,
                    projectile_type, piercing, level=1
                )
                
                # Set hybrid properties if applicable
                if self.hybrid_types:
                    projectile.hybrid_types = self.hybrid_types
                
                projectiles.append(projectile)
        
        return projectiles
