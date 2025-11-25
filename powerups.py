import pygame
import random
import math
from enum import Enum

class PowerUpType(Enum):
    SPEED_BOOST = "speed_boost"
    DAMAGE_BOOST = "damage_boost"
    RAPID_FIRE = "rapid_fire"
    SHIELD = "shield"
    HEAL = "heal"
    INVINCIBILITY = "invincibility"
    MULTI_SHOT = "multi_shot"
    PIERCING = "piercing"
    EXPLOSIVE_SHOTS = "explosive_shots"

class PowerUp(pygame.sprite.Sprite):
    """Power-up that players can collect for temporary boosts"""
    def __init__(self, pos, power_type):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.power_type = power_type
        self.size = 20
        self.rect = pygame.Rect(0, 0, self.size * 2, self.size * 2)
        self.rect.center = self.pos
        self.lifetime = 15.0  # Power-ups disappear after 15 seconds
        self.age = 0
        self.float_offset = 0
        self.float_speed = 2.0
        
        # Set properties based on type
        self.setup_properties()
        
        # Create visual
        self.create_visual()
    
    def setup_properties(self):
        """Setup power-up properties based on type"""
        properties = {
            PowerUpType.SPEED_BOOST: {
                "color": (0, 200, 255),
                "duration": 10.0,
                "value": 1.5,
                "symbol": "↑"
            },
            PowerUpType.DAMAGE_BOOST: {
                "color": (255, 100, 0),
                "duration": 12.0,
                "value": 2.0,
                "symbol": "⚡"
            },
            PowerUpType.RAPID_FIRE: {
                "color": (255, 255, 0),
                "duration": 8.0,
                "value": 2.0,
                "symbol": "»"
            },
            PowerUpType.SHIELD: {
                "color": (0, 255, 200),
                "duration": 15.0,
                "value": 1.0,
                "symbol": "◊"
            },
            PowerUpType.HEAL: {
                "color": (255, 0, 100),
                "duration": 0,  # Instant effect
                "value": 50,
                "symbol": "+"
            },
            PowerUpType.INVINCIBILITY: {
                "color": (255, 215, 0),
                "duration": 5.0,
                "value": 1.0,
                "symbol": "★"
            },
            PowerUpType.MULTI_SHOT: {
                "color": (200, 0, 255),
                "duration": 10.0,
                "value": 3,
                "symbol": "◈"
            },
            PowerUpType.PIERCING: {
                "color": (255, 255, 255),
                "duration": 12.0,
                "value": 1.0,
                "symbol": "→"
            },
            PowerUpType.EXPLOSIVE_SHOTS: {
                "color": (255, 50, 50),
                "duration": 8.0,
                "value": 1.0,
                "symbol": "💥"
            }
        }
        
        props = properties.get(self.power_type, properties[PowerUpType.SPEED_BOOST])
        self.color = props["color"]
        self.duration = props["duration"]
        self.value = props["value"]
        self.symbol = props["symbol"]
    
    def create_visual(self):
        """Create visual representation of power-up"""
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        center = self.size
        
        # Draw outer circle with glow effect
        for i in range(3):
            glow_size = self.size - i * 2
            glow_alpha = 100 - i * 30
            glow_color = (*self.color, glow_alpha)
            pygame.draw.circle(self.image, glow_color, (center, center), glow_size)
        
        # Draw main circle
        pygame.draw.circle(self.image, self.color, (center, center), self.size - 2)
        
        # Draw inner circle
        pygame.draw.circle(self.image, (255, 255, 255), (center, center), self.size - 6)
        
        # Draw symbol
        font = pygame.font.Font(None, 20)
        text = font.render(self.symbol, True, self.color)
        text_rect = text.get_rect(center=(center, center))
        self.image.blit(text, text_rect)
    
    def update(self, dt):
        """Update power-up animation and lifetime"""
        self.age += dt
        self.float_offset = math.sin(self.age * self.float_speed) * 5
        
        # Update position with floating effect
        self.rect.centery = self.pos.y + self.float_offset
        
        # Remove if too old
        if self.age >= self.lifetime:
            self.kill()
    
    def apply_to_player(self, player):
        """Apply power-up effect to player"""
        if self.power_type == PowerUpType.HEAL:
            # Instant heal
            player.heal(self.value)
            return "instant"
        else:
            # Add to active effects
            player.add_power_up_effect(self.power_type, self.duration, self.value)
            return "temporary"

class PowerUpManager:
    """Manages power-up spawning and effects"""
    def __init__(self, game):
        self.game = game
        self.power_ups = pygame.sprite.Group()
        self.spawn_timer = 0
        self.spawn_rate = 20.0  # Spawn power-up every 20 seconds
        self.drop_chance = 0.15  # 15% chance to drop from elite enemies
        
        # Power-up spawn weights
        self.spawn_weights = {
            PowerUpType.SPEED_BOOST: 20,
            PowerUpType.DAMAGE_BOOST: 15,
            PowerUpType.RAPID_FIRE: 15,
            PowerUpType.SHIELD: 10,
            PowerUpType.HEAL: 25,
            PowerUpType.INVINCIBILITY: 5,
            PowerUpType.MULTI_SHOT: 10,
            PowerUpType.PIERCING: 10,
            PowerUpType.EXPLOSIVE_SHOTS: 10
        }
    
    def update(self, dt):
        """Update power-up spawning and effects"""
        self.spawn_timer += dt
        
        # Spawn random power-ups
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0
            self.spawn_random_power_up()
        
        # Update power-ups
        self.power_ups.update(dt)
    
    def spawn_random_power_up(self):
        """Spawn a random power-up at a random location"""
        # Choose power-up type based on weights
        power_types = list(self.spawn_weights.keys())
        weights = list(self.spawn_weights.values())
        power_type = random.choices(power_types, weights=weights)[0]
        
        # Random spawn position (avoiding edges)
        margin = 100
        x = random.randint(margin, self.game.screen_width - margin)
        y = random.randint(margin, self.game.screen_height - margin)
        
        power_up = PowerUp((x, y), power_type)
        self.power_ups.add(power_up)
    
    def drop_power_up(self, pos, enemy_type):
        """Chance to drop power-up from defeated enemy"""
        # Higher chance for elite enemies
        drop_chance = self.drop_chance
        if enemy_type in ["boss", "mega_boss", "tank", "fast"]:
            drop_chance = 0.4  # 40% for elite enemies
        
        if random.random() < drop_chance:
            # Choose power-up type (better power-ups from elite enemies)
            if enemy_type in ["boss", "mega_boss"]:
                # Better power-ups from bosses
                elite_types = [PowerUpType.DAMAGE_BOOST, PowerUpType.RAPID_FIRE, 
                              PowerUpType.INVINCIBILITY, PowerUpType.MULTI_SHOT,
                              PowerUpType.EXPLOSIVE_SHOTS]
                power_type = random.choice(elite_types)
            else:
                # Random power-up for regular enemies
                power_types = list(self.spawn_weights.keys())
                weights = list(self.spawn_weights.values())
                power_type = random.choices(power_types, weights=weights)[0]
            
            power_up = PowerUp(pos, power_type)
            self.power_ups.add(power_up)
            return True
        return False
    
    def handle_collisions(self, player):
        """Handle player collecting power-ups"""
        collected = pygame.sprite.spritecollide(player, self.power_ups, False)
        for power_up in collected:
            effect_type = power_up.apply_to_player(player)
            
            # Track power-up collection
            self.game.update_stats("powerup_collected")
            
            # Show collection text
            if effect_type == "instant":
                self.game.floating_text.add_announcement(
                    power_up.rect.center, 
                    f"+{power_up.value} HP!", 
                    (255, 0, 100)
                )
            else:
                self.game.floating_text.add_announcement(
                    power_up.rect.center, 
                    f"{power_up.power_type.value.replace('_', ' ').title()}!", 
                    power_up.color
                )
            
            # Play sound
            from sounds import play_sound
            play_sound('pickup')
            
            # Remove power-up
            power_up.kill()
    
    def draw(self, screen):
        """Draw all power-ups"""
        self.power_ups.draw(screen)
