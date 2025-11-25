import pygame
import math
from enum import Enum

class StatusEffectType(Enum):
    BURNING = "burning"
    FROZEN = "frozen"
    STUNNED = "stunned"
    POISONED = "poisoned"
    SLOWED = "slowed"
    WEAKENED = "weakened"

class StatusEffect:
    """Individual status effect on an entity"""
    def __init__(self, effect_type, duration, intensity=1.0):
        self.effect_type = effect_type
        self.duration = duration
        self.intensity = intensity
        self.age = 0
        self.tick_timer = 0
        self.tick_interval = 0.5  # Apply effect every 0.5 seconds
        
    def update(self, dt):
        """Update status effect"""
        self.age += dt
        self.tick_timer += dt
        return self.age < self.duration
    
    def should_tick(self):
        """Check if effect should apply damage/changes this frame"""
        if self.tick_timer >= self.tick_interval:
            self.tick_timer = 0
            return True
        return False
    
    def get_remaining_percentage(self):
        """Get remaining duration as percentage"""
        return max(0, 1.0 - (self.age / self.duration))

class EnemyHealthBar:
    """Health bar for enemies"""
    def __init__(self, enemy):
        self.enemy = enemy
        self.width = 40
        self.height = 4
        self.offset_y = -25
        self.show_duration = 2.0  # Show health bar for 2 seconds after taking damage
        self.show_timer = 0
        self.visible = False
        
    def take_damage(self):
        """Call when enemy takes damage to show health bar"""
        self.visible = True
        self.show_timer = 0
    
    def update(self, dt):
        """Update health bar visibility"""
        if self.visible:
            self.show_timer += dt
            if self.show_timer >= self.show_duration:
                self.visible = False
    
    def draw(self, screen, camera_offset=(0, 0)):
        """Draw health bar above enemy"""
        if not self.visible or self.enemy.hp >= self.enemy.max_hp:
            return
        
        # Calculate position
        x = self.enemy.rect.centerx - self.width // 2 + camera_offset[0]
        y = self.enemy.rect.top + self.offset_y + camera_offset[1]
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (x, y, self.width, self.height))
        
        # Health fill
        health_percentage = self.enemy.hp / self.enemy.max_hp
        fill_width = int(self.width * health_percentage)
        
        # Color based on health percentage
        if health_percentage > 0.6:
            color = (0, 200, 0)  # Green
        elif health_percentage > 0.3:
            color = (255, 200, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
        
        pygame.draw.rect(screen, color, (x, y, fill_width, self.height))
        
        # Border
        pygame.draw.rect(screen, (100, 100, 100), (x, y, self.width, self.height), 1)

class EnhancedDamageNumber:
    """Enhanced damage number with more visual effects"""
    def __init__(self, pos, damage, color=(255, 255, 0), critical=False, damage_type="normal"):
        self.pos = pygame.Vector2(pos)
        self.damage = damage
        self.color = color
        self.critical = critical
        self.damage_type = damage_type
        self.lifetime = 1.5 if not critical else 2.0
        self.age = 0
        
        # Movement
        self.vel = pygame.Vector2(0, -80)  # Float upward
        if critical:
            self.vel.x = random.uniform(-30, 30)  # Critical hits wobble
        
        # Visual properties
        self.scale = 1.5 if critical else 1.0
        self.alpha = 255
        self.rotation = 0
        self.rotation_speed = 2.0 if critical else 0
        
    def update(self, dt):
        """Update damage number"""
        self.age += dt
        
        # Movement
        self.vel.y += 100 * dt  # Gravity
        self.pos += self.vel * dt
        
        # Rotation for critical hits
        if self.critical:
            self.rotation += self.rotation_speed
        
        # Fade out
        if self.age > self.lifetime * 0.7:
            fade_progress = (self.age - self.lifetime * 0.7) / (self.lifetime * 0.3)
            self.alpha = int(255 * (1 - fade_progress))
        
        return self.age < self.lifetime
    
    def draw(self, screen, camera_offset=(0, 0)):
        """Draw damage number"""
        if self.alpha <= 0:
            return
        
        # Create text surface
        font_size = 32 if self.critical else 24
        font = pygame.font.Font(None, font_size)
        
        # Add damage type prefix
        text = str(int(self.damage))
        if self.damage_type == "critical":
            text = "CRIT! " + text
        elif self.damage_type == "area":
            text = "AREA " + text
        elif self.damage_type == "poison":
            text = "☠ " + text
        elif self.damage_type == "burn":
            text = "🔥 " + text
        
        text_surface = font.render(text, True, self.color)
        text_surface.set_alpha(self.alpha)
        
        # Apply rotation for critical hits
        if self.critical:
            text_surface = pygame.transform.rotate(text_surface, self.rotation)
        
        # Draw shadow
        shadow_surface = font.render(text, True, (0, 0, 0))
        shadow_surface.set_alpha(self.alpha // 2)
        screen.blit(shadow_surface, 
                   (self.pos.x - text_surface.get_width()//2 + 2 + camera_offset[0], 
                    self.pos.y - text_surface.get_height()//2 + 2 + camera_offset[1]))
        
        # Draw main text
        screen.blit(text_surface, 
                   (self.pos.x - text_surface.get_width()//2 + camera_offset[0], 
                    self.pos.y - text_surface.get_height()//2 + camera_offset[1]))

class VisualFeedbackManager:
    """Manages all visual feedback systems"""
    def __init__(self, game):
        self.game = game
        self.damage_numbers = []
        self.enemy_health_bars = {}  # {enemy: EnemyHealthBar}
        self.status_effects = {}  # {entity: [StatusEffect]}
        
    def add_damage_number(self, pos, damage, color=(255, 255, 0), critical=False, damage_type="normal"):
        """Add a new damage number"""
        self.damage_numbers.append(EnhancedDamageNumber(pos, damage, color, critical, damage_type))
    
    def add_critical_damage(self, pos, damage):
        """Add critical damage number"""
        self.add_damage_number(pos, damage, (255, 100, 0), True, "critical")
    
    def add_area_damage(self, pos, damage):
        """Add area damage number"""
        self.add_damage_number(pos, damage, (255, 150, 0), False, "area")
    
    def add_status_damage(self, pos, damage, status_type):
        """Add status effect damage number"""
        colors = {
            "poison": (150, 255, 150),
            "burn": (255, 150, 0),
            "frost": (150, 200, 255)
        }
        color = colors.get(status_type, (255, 255, 255))
        self.add_damage_number(pos, damage, color, False, status_type)
    
    def register_enemy(self, enemy):
        """Register enemy for health bar tracking"""
        if enemy not in self.enemy_health_bars:
            self.enemy_health_bars[enemy] = EnemyHealthBar(enemy)
    
    def unregister_enemy(self, enemy):
        """Unregister enemy"""
        if enemy in self.enemy_health_bars:
            del self.enemy_health_bars[enemy]
    
    def on_enemy_damaged(self, enemy, damage, critical=False):
        """Handle enemy taking damage"""
        # Show health bar
        if enemy in self.enemy_health_bars:
            self.enemy_health_bars[enemy].take_damage()
        
        # Add damage number
        color = (255, 100, 0) if critical else (255, 255, 0)
        pos = enemy.rect.center
        self.add_damage_number(pos, damage, color, critical)
    
    def add_status_effect(self, entity, effect_type, duration, intensity=1.0):
        """Add status effect to entity"""
        if entity not in self.status_effects:
            self.status_effects[entity] = []
        
        # Remove existing effect of same type
        self.status_effects[entity] = [e for e in self.status_effects[entity] if e.effect_type != effect_type]
        
        # Add new effect
        self.status_effects[entity].append(StatusEffect(effect_type, duration, intensity))
    
    def update(self, dt):
        """Update all visual feedback systems"""
        # Update damage numbers
        self.damage_numbers = [dn for dn in self.damage_numbers if dn.update(dt)]
        
        # Update health bars
        for health_bar in self.enemy_health_bars.values():
            health_bar.update(dt)
        
        # Update status effects
        entities_to_remove = []
        for entity, effects in self.status_effects.items():
            effects_to_remove = []
            for effect in effects:
                if not effect.update(dt):
                    effects_to_remove.append(effect)
                else:
                    # Apply status effect damage
                    if effect.should_tick():
                        self.apply_status_effect_damage(entity, effect)
            
            # Remove expired effects
            for effect in effects_to_remove:
                effects.remove(effect)
            
            # Remove entity if no effects left
            if not effects:
                entities_to_remove.append(entity)
        
        for entity in entities_to_remove:
            del self.status_effects[entity]
    
    def apply_status_effect_damage(self, entity, effect):
        """Apply damage from status effect"""
        damage = 0
        
        if effect.effect_type == StatusEffectType.BURNING:
            damage = int(5 * effect.intensity)
            self.add_status_damage(entity.rect.center if hasattr(entity, 'rect') else entity.pos, damage, "burn")
            if hasattr(entity, 'hp'):
                entity.hp -= damage
        
        elif effect.effect_type == StatusEffectType.POISONED:
            damage = int(3 * effect.intensity)
            self.add_status_damage(entity.rect.center if hasattr(entity, 'rect') else entity.pos, damage, "poison")
            if hasattr(entity, 'hp'):
                entity.hp -= damage
    
    def draw(self, screen, camera_offset=(0, 0)):
        """Draw all visual feedback"""
        # Draw damage numbers
        for damage_number in self.damage_numbers:
            damage_number.draw(screen, camera_offset)
        
        # Draw enemy health bars
        for health_bar in self.enemy_health_bars.values():
            health_bar.draw(screen, camera_offset)
        
        # Draw status effect indicators
        for entity, effects in self.status_effects.items():
            if hasattr(entity, 'rect'):
                self.draw_status_effects(screen, entity, effects, camera_offset)
    
    def draw_status_effects(self, screen, entity, effects, camera_offset):
        """Draw status effect indicators above entity"""
        if not effects:
            return
        
        # Position above entity
        x = entity.rect.centerx + camera_offset[0]
        y = entity.rect.top - 35 + camera_offset[1]
        
        # Draw effect icons
        icon_size = 12
        spacing = 15
        
        for i, effect in enumerate(effects):
            icon_x = x - (len(effects) * spacing) // 2 + i * spacing
            
            # Color based on effect type
            colors = {
                StatusEffectType.BURNING: (255, 100, 0),
                StatusEffectType.FROZEN: (100, 200, 255),
                StatusEffectType.STUNNED: (255, 255, 100),
                StatusEffectType.POISONED: (150, 255, 150),
                StatusEffectType.SLOWED: (200, 150, 255),
                StatusEffectType.WEAKENED: (255, 150, 150)
            }
            
            color = colors.get(effect.effect_type, (255, 255, 255))
            
            # Draw icon background
            pygame.draw.circle(screen, color, (icon_x, y), icon_size)
            
            # Draw timer ring
            if effect.duration > 0:
                remaining = effect.get_remaining_percentage()
                ring_width = 2
                pygame.draw.circle(screen, (255, 255, 255), (icon_x, y), icon_size + 2, ring_width)
                
                # Draw remaining arc (simplified - just draw a smaller circle)
                if remaining > 0:
                    inner_color = (*color, int(255 * remaining))
                    pygame.draw.circle(screen, color, (icon_x, y), int(icon_size * remaining))
