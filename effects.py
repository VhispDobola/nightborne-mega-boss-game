import pygame
import random
import math

class ScreenShake:
    """Screen shake effect for impacts and explosions"""
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)
        self.intensity = 0
        self.duration = 0
        self.current_time = 0
        
    def shake(self, intensity, duration):
        """Trigger screen shake"""
        self.intensity = intensity
        self.duration = duration
        self.current_time = 0
        
    def update(self, dt):
        """Update screen shake"""
        if self.current_time < self.duration:
            self.current_time += dt
            
            # Calculate shake intensity based on remaining time
            progress = self.current_time / self.duration
            current_intensity = self.intensity * (1 - progress)
            
            # Random offset
            self.offset.x = random.uniform(-current_intensity, current_intensity)
            self.offset.y = random.uniform(-current_intensity, current_intensity)
        else:
            self.offset = pygame.Vector2(0, 0)
            
    def apply_offset(self, surface):
        """Apply shake offset to surface - this method is deprecated, use get_offset() instead"""
        # This method is inefficient, better to use get_offset() in drawing
        return surface
    
    def get_offset(self):
        """Get current shake offset for drawing"""
        return self.offset

class Particle:
    """Single particle for effects"""
    def __init__(self, pos, vel, color, size, lifetime):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.age = 0
        self.initial_size = size
        
    def update(self, dt):
        """Update particle"""
        self.pos += self.vel * dt
        self.age += dt
        
        # Apply gravity to some particles
        if self.vel.y > 0:
            self.vel.y += 200 * dt  # Gravity effect
            
        # Fade out
        alpha = 1.0 - (self.age / self.lifetime)
        self.size = self.initial_size * alpha
        
        return self.age < self.lifetime
        
    def draw(self, screen, shake_offset=pygame.Vector2(0, 0)):
        """Draw particle"""
        if self.size > 0:
            alpha = 1.0 - (self.age / self.lifetime)
            color = (*self.color, int(255 * alpha))
            
            # Create surface with alpha
            particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (int(self.size), int(self.size)), int(self.size))
            screen.blit(particle_surface, (self.pos.x - self.size + int(shake_offset.x), self.pos.y - self.size + int(shake_offset.y)))

class ParticleSystem:
    """Manages particle effects"""
    def __init__(self):
        self.particles = []
        
    def create_explosion(self, pos, color=(255, 100, 0), particle_count=20):
        """Create explosion effect"""
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 300)
            vel = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(2, 6)
            lifetime = random.uniform(0.3, 0.8)
            
            particle = Particle(pos, vel, color, size, lifetime)
            self.particles.append(particle)
    
    def create_particle(self, pos, color, lifetime):
        """Create a single particle with default parameters"""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(20, 100)
        vel = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
        size = random.uniform(2, 4)
        
        particle = Particle(pos, vel, color, size, lifetime)
        self.particles.append(particle)
            
    def create_impact(self, pos, color=(255, 255, 0), particle_count=10):
        """Create impact effect"""
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 150)
            vel = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(1, 3)
            lifetime = random.uniform(0.2, 0.5)
            
            particle = Particle(pos, vel, color, size, lifetime)
            self.particles.append(particle)
            
    def create_death_effect(self, pos, enemy_color, particle_count=15):
        """Create enemy death effect"""
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 200)
            vel = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(2, 5)
            lifetime = random.uniform(0.4, 0.7)
            
            # Use enemy color with some variation
            color_variation = random.randint(-30, 30)
            color = tuple(max(0, min(255, c + color_variation)) for c in enemy_color)
            
            particle = Particle(pos, vel, color, size, lifetime)
            self.particles.append(particle)
            
    def create_xp_pickup_effect(self, pos):
        """Create XP pickup visual effect"""
        for i in range(8):
            angle = (math.pi * 2 * i) / 8
            speed = pygame.Vector2(math.cos(angle) * 100, math.sin(angle) * 100)
            color = (255, 215, 0)
            size = 3
            lifetime = 0.5
            self.particles.append(Particle(pos, speed, color, size, lifetime))
    
    def create_heal_effect(self, pos):
        """Create healing visual effect"""
        for i in range(12):
            angle = (math.pi * 2 * i) / 12
            speed = pygame.Vector2(math.cos(angle) * 50, math.sin(angle) * 50)
            color = (0, 255, 0)
            size = 4
            lifetime = 1.0
            self.particles.append(Particle(pos, speed, color, size, lifetime))
    
    def create_laser_beam(self, start_pos, end_pos, color=(255, 0, 100), width=3):
        """Create laser beam effect"""
        # Calculate laser direction
        direction = (end_pos - start_pos).normalize()
        distance = (end_pos - start_pos).length()
        
        # Create particles along the laser path
        steps = int(distance / 10)
        for i in range(steps):
            t = i / steps
            pos = start_pos + direction * (distance * t)
            # Add some random offset for visual effect
            offset = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
            particle_pos = pos + offset
            speed = pygame.Vector2(random.uniform(-20, 20), random.uniform(-20, 20))
            size = 2
            lifetime = 0.3
            self.particles.append(Particle(particle_pos, speed, color, size, lifetime))
    
    def create_summon_effect(self, pos):
        """Create summoning visual effect"""
        for i in range(16):
            angle = (math.pi * 2 * i) / 16
            # Particles move inward
            speed = pygame.Vector2(-math.cos(angle) * 80, -math.sin(angle) * 80)
            color = (150, 0, 150)
            size = 5
            lifetime = 1.5
            self.particles.append(Particle(pos + speed * -0.5, speed, color, size, lifetime))
    
    def create_dash_trail(self, old_pos, new_pos):
        """Create dash trail effect"""
        # Create particles along the dash path
        steps = 10
        for i in range(steps):
            t = i / steps
            pos = old_pos + (new_pos - old_pos) * t
            # Add some random spread
            offset = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            particle_pos = pos + offset
            speed = pygame.Vector2(random.uniform(-50, 50), random.uniform(-50, 50))
            color = (255, 0, 255)
            size = 6
            lifetime = 0.8
            self.particles.append(Particle(particle_pos, speed, color, size, lifetime))
            
    def update(self, dt):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update(dt)]
        
    def draw(self, screen, shake_offset=pygame.Vector2(0, 0)):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen, shake_offset)

class FloatingText:
    """Floating damage numbers and other text"""
    def __init__(self, pos, text, color=(255, 255, 255), size=20, lifetime=1.0):
        self.pos = pygame.Vector2(pos)
        self.text = text
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.age = 0
        self.vel = pygame.Vector2(0, -50)  # Float upward
        
    def update(self, dt):
        """Update floating text"""
        self.pos += self.vel * dt
        self.age += dt
        return self.age < self.lifetime
        
    def draw(self, screen, font, shake_offset=pygame.Vector2(0, 0)):
        """Draw floating text"""
        alpha = 1.0 - (self.age / self.lifetime)
        color = (*self.color, int(255 * alpha))
        
        text_surface = font.render(self.text, True, self.color)
        text_surface.set_alpha(int(255 * alpha))
        screen.blit(text_surface, (self.pos.x - text_surface.get_width() // 2 + int(shake_offset.x), 
                                   self.pos.y - text_surface.get_height() // 2 + int(shake_offset.y)))

class FloatingTextManager:
    """Manages floating text effects"""
    def __init__(self):
        self.texts = []
        self.font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 28)
        
    def add_damage_number(self, pos, damage, critical=False):
        """Add damage number"""
        color = (255, 100, 100) if critical else (255, 255, 0)
        size = 28 if critical else 20
        text = str(int(damage))
        
        floating_text = FloatingText(pos, text, color, size, 0.8)
        self.texts.append(floating_text)
        
    def add_level_up_text(self, pos):
        """Add level up text"""
        floating_text = FloatingText(pos, "LEVEL UP!", (255, 215, 0), 32, 1.5)
        self.texts.append(floating_text)
        
    def add_combo_text(self, pos, combo_count):
        """Add combo text"""
        color = (255, 200, 0) if combo_count < 5 else (255, 100, 255) if combo_count < 10 else (255, 0, 255)
        text = f"COMBO x{combo_count}!"
        
        floating_text = FloatingText(pos, text, color, 24, 1.0)
        self.texts.append(floating_text)
        
    def add_announcement(self, pos, text, color=(255, 255, 0)):
        """Add announcement text"""
        floating_text = FloatingText(pos, text, color, 36, 2.0)
        self.texts.append(floating_text)
    
    def add_text(self, pos, text, color=(255, 255, 255)):
        """Add generic text"""
        floating_text = FloatingText(pos, text, color, 20, 1.0)
        self.texts.append(floating_text)
        
    def update(self, dt):
        """Update all floating texts"""
        self.texts = [t for t in self.texts if t.update(dt)]
        
    def draw(self, screen, shake_offset=pygame.Vector2(0, 0)):
        """Draw all floating texts"""
        for text in self.texts:
            font = self.big_font if text.size > 24 else self.font
            text.draw(screen, font, shake_offset)
