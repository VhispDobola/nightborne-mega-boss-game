import pygame
import random
import math

class XPOrb(pygame.sprite.Sprite):
    def __init__(self, pos, value=15):
        super().__init__()
        self.value = value
        self.pos = pygame.Vector2(pos)
        
        # Visual setup - size based on value
        self.size = min(8 + value // 10, 16)
        self.create_visual()
        self.rect = self.image.get_rect(center=self.pos)
        
        # Movement
        self.vel = pygame.Vector2(random.uniform(-50, 50), random.uniform(-50, 50))
        self.lifetime = 10.0  # seconds before disappearing
        self.age = 0
        
        # Pickup behavior
        self.pickup_speed = 300  # Speed when moving toward player
        self.being_picked_up = False
        
    def create_visual(self):
        """Create visual representation based on XP value"""
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Color based on value
        if self.value >= 30:
            color = (255, 215, 0)  # Gold for high value
        elif self.value >= 20:
            color = (160, 255, 160)  # Green for medium value
        else:
            color = (100, 200, 255)  # Blue for low value
        
        # Draw orb with glow effect
        pygame.draw.circle(self.image, color, (self.size, self.size), self.size)
        
        # Add inner glow
        glow_color = tuple(min(255, c + 50) for c in color)
        pygame.draw.circle(self.image, glow_color, (self.size, self.size), self.size // 2)
        
        # Add sparkle effect for high-value orbs
        if self.value >= 30:
            sparkle_pos = [
                (self.size - 2, self.size - 2),
                (self.size + 2, self.size - 2),
                (self.size, self.size + 2)
            ]
            for pos in sparkle_pos:
                pygame.draw.circle(self.image, (255, 255, 255), pos, 1)
    
    def update(self, dt, player_pos, pickup_range):
        """Update XP orb movement and behavior"""
        self.age += dt
        
        # Remove if too old
        if self.age >= self.lifetime:
            self.kill()
            return
        
        # Calculate distance to player
        to_player = player_pos - self.pos
        distance = to_player.length()
        
        # Check if within pickup range
        if distance <= pickup_range:
            self.being_picked_up = True
        
        # Movement behavior
        if self.being_picked_up and distance > 0:
            # Move directly toward player when in pickup range
            direction = to_player.normalize()
            self.pos += direction * self.pickup_speed * dt
        else:
            # Random drift when not being picked up
            self.pos += self.vel * dt
            
            # Apply some friction to slow down drift
            self.vel *= 0.98
            
            # Add slight random movement
            if random.random() < 0.1:
                self.vel += pygame.Vector2(random.uniform(-20, 20), random.uniform(-20, 20))
        
        # Update rect position
        self.rect.center = self.pos
        
        # Pulse effect
        pulse = math.sin(self.age * 5) * 0.2 + 1.0
        current_size = int(self.size * pulse)
        if current_size != self.size:
            self.size = current_size
            self.create_visual()
            self.rect = self.image.get_rect(center=self.pos)
    
    def draw(self, screen):
        """Draw the XP orb"""
        screen.blit(self.image, self.rect)
        
        # Draw pickup range indicator when close to player
        if self.being_picked_up:
            # Draw a small attraction indicator
            indicator_size = 2
            pygame.draw.circle(screen, (255, 255, 255, 128), self.rect.center, indicator_size, 1)

class XPManager:
    """Manages XP orb spawning and collection"""
    def __init__(self):
        self.xp_orbs = pygame.sprite.Group()
        self.spawn_chances = {
            'low': 0.7,    # 70% chance for low value (10 XP)
            'medium': 0.25, # 25% chance for medium value (20 XP)
            'high': 0.05   # 5% chance for high value (40 XP)
        }
    
    def spawn_xp_orb(self, pos, enemy_type=None):
        """Spawn an XP orb at given position"""
        # Determine XP value based on enemy type or random chance
        if enemy_type:
            if enemy_type == "basic":
                value = 15
            elif enemy_type == "tank":
                value = 30
            elif enemy_type == "fast":
                value = 20
            else:
                value = 15
        else:
            # Random value based on chances
            rand = random.random()
            if rand < self.spawn_chances['high']:
                value = 40
            elif rand < self.spawn_chances['high'] + self.spawn_chances['medium']:
                value = 20
            else:
                value = 10
        
        orb = XPOrb(pos, value)
        self.xp_orbs.add(orb)
        return orb
    
    def update(self, dt, player_pos, pickup_range):
        """Update all XP orbs"""
        self.xp_orbs.update(dt, player_pos, pickup_range)
    
    def draw(self, screen):
        """Draw all XP orbs"""
        self.xp_orbs.draw(screen)
