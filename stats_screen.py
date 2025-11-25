import pygame
import math
import random
from enum import Enum
import numpy as np

class StatsScreen:
    def __init__(self, game):
        self.game = game
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.header_font = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Animation properties
        self.animation_time = 0
        self.stats_revealed = []
        self.particles = []
        self.star_particles = []
        
        # Initialize star background
        self.init_star_background()
        
        # Stats categories
        self.stats_categories = {
            "survival": {
                "title": "SURVIVAL STATS",
                "color": (255, 100, 100),
                "stats": []
            },
            "combat": {
                "title": "COMBAT STATS", 
                "color": (100, 255, 100),
                "stats": []
            },
            "performance": {
                "title": "PERFORMANCE",
                "color": (100, 200, 255),
                "stats": []
            },
            "achievements": {
                "title": "ACHIEVEMENTS",
                "color": (255, 215, 0),
                "stats": []
            }
        }
        
        # Sound effects
        self.sounds = self.create_stats_sounds()
    
    def init_star_background(self):
        """Create animated star background"""
        for _ in range(100):
            x = random.uniform(0, self.screen_width)
            y = random.uniform(0, self.screen_height)
            size = random.uniform(1, 3)
            brightness = random.uniform(0.3, 1.0)
            twinkle_speed = random.uniform(1, 3)
            self.star_particles.append({
                'x': x, 'y': y, 'size': size, 
                'brightness': brightness, 'twinkle_speed': twinkle_speed,
                'phase': random.uniform(0, math.pi * 2)
            })
    
    def create_stats_sounds(self):
        """Create sound effects for stats screen"""
        sounds = {}
        
        # Reveal sound
        sounds['reveal'] = self.generate_reveal_sound()
        
        # Hover sound
        sounds['hover'] = self.generate_hover_sound()
        
        # Click sound
        sounds['click'] = self.generate_click_sound()
        
        return sounds
    
    def generate_reveal_sound(self):
        """Generate stat reveal sound effect"""
        sample_rate = 22050
        duration = 0.3
        samples = int(sample_rate * duration)
        
        waves = []
        for i in range(samples):
            t = float(i) / sample_rate
            # Rising frequency whoosh
            freq = 200 + t * 800
            envelope = math.exp(-t * 3)
            wave = envelope * math.sin(2 * math.pi * freq * t)
            waves.append(int(wave * 16384 / 3))  # 3x quieter
        
        # Create stereo sound
        stereo_waves = []
        for wave in waves:
            stereo_waves.append([wave, wave])
        
        # Convert to numpy array
        stereo_array = np.array(stereo_waves, dtype=np.int16)
        return pygame.sndarray.make_sound(stereo_array)
    
    def generate_hover_sound(self):
        """Generate hover sound effect"""
        sample_rate = 22050
        duration = 0.1
        samples = int(sample_rate * duration)
        
        waves = []
        for i in range(samples):
            t = float(i) / sample_rate
            envelope = math.exp(-t * 10)
            wave = envelope * math.sin(2 * math.pi * 600 * t)
            waves.append(int(wave * 8192 / 3))  # 3x quieter
        
        # Create stereo sound
        stereo_waves = []
        for wave in waves:
            stereo_waves.append([wave, wave])
        
        # Convert to numpy array
        stereo_array = np.array(stereo_waves, dtype=np.int16)
        return pygame.sndarray.make_sound(stereo_array)
    
    def generate_click_sound(self):
        """Generate click sound effect"""
        sample_rate = 22050
        duration = 0.15
        samples = int(sample_rate * duration)
        
        waves = []
        for i in range(samples):
            t = float(i) / sample_rate
            envelope = math.exp(-t * 20)
            wave = envelope * math.sin(2 * math.pi * 400 * t)
            wave += envelope * random.uniform(-0.2, 0.2)
            waves.append(int(wave * 16384 / 3))  # 3x quieter
        
        # Create stereo sound
        stereo_waves = []
        for wave in waves:
            stereo_waves.append([wave, wave])
        
        # Convert to numpy array
        stereo_array = np.array(stereo_waves, dtype=np.int16)
        return pygame.sndarray.make_sound(stereo_array)
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def collect_stats(self):
        """Collect all game statistics"""
        stats = self.game.get_game_stats() if hasattr(self.game, 'get_game_stats') else self.generate_mock_stats()
        
        # Organize stats into categories
        self.stats_categories["survival"]["stats"] = [
            {"label": "Time Survived", "value": self.format_time(stats.get("time_survived", 0)), "icon": "⏱️"},
            {"label": "Waves Completed", "value": str(stats.get("waves_completed", 0)), "icon": "🌊"},
            {"label": "Highest Wave", "value": str(stats.get("highest_wave", 0)), "icon": "🏆"},
            {"label": "Deaths", "value": str(stats.get("deaths", 1)), "icon": "💀"}
        ]
        
        self.stats_categories["combat"]["stats"] = [
            {"label": "Enemies Killed", "value": str(stats.get("enemies_killed", 0)), "icon": "⚔️"},
            {"label": "Damage Dealt", "value": self.format_number(stats.get("damage_dealt", 0)), "icon": "💥"},
            {"label": "Damage Taken", "value": self.format_number(stats.get("damage_taken", 0)), "icon": "🛡️"},
            {"label": "Accuracy", "value": f"{stats.get('accuracy', 0):.1f}%", "icon": "🎯"},
            {"label": "Critical Hits", "value": str(stats.get("critical_hits", 0)), "icon": "⭐"},
            {"label": "Max Combo", "value": str(stats.get("max_combo", 0)), "icon": "🔥"}
        ]
        
        self.stats_categories["performance"]["stats"] = [
            {"label": "Level Reached", "value": str(stats.get("level_reached", 1)), "icon": "⬆️"},
            {"label": "XP Gained", "value": self.format_number(stats.get("xp_gained", 0)), "icon": "✨"},
            {"label": "Power-ups Collected", "value": str(stats.get("powerups_collected", 0)), "icon": "💎"},
            {"label": "Upgrades Chosen", "value": str(stats.get("upgrades_chosen", 0)), "icon": "🔧"}
        ]
        
        # Generate achievements based on performance
        achievements = self.generate_achievements(stats)
        self.stats_categories["achievements"]["stats"] = achievements
    
    def generate_mock_stats(self):
        """Generate mock stats for testing"""
        return {
            "time_survived": 180,  # 3 minutes
            "waves_completed": 5,
            "highest_wave": 6,
            "deaths": 1,
            "enemies_killed": 125,
            "damage_dealt": 15420,
            "damage_taken": 850,
            "accuracy": 67.5,
            "critical_hits": 23,
            "max_combo": 15,
            "level_reached": 8,
            "xp_gained": 2450,
            "powerups_collected": 12,
            "upgrades_chosen": 7
        }
    
    def generate_achievements(self, stats):
        """Generate achievements based on stats"""
        achievements = []
        
        # Survival achievements
        if stats.get("time_survived", 0) >= 120:  # 2+ minutes
            achievements.append({"label": "Survivor", "value": "2+ minutes survived", "icon": "🏅", "earned": True})
        if stats.get("waves_completed", 0) >= 5:
            achievements.append({"label": "Wave Master", "value": "5 waves completed", "icon": "🌊", "earned": True})
        
        # Combat achievements
        if stats.get("enemies_killed", 0) >= 100:
            achievements.append({"label": "Exterminator", "value": "100 enemies killed", "icon": "⚔️", "earned": True})
        if stats.get("accuracy", 0) >= 80:
            achievements.append({"label": "Sharpshooter", "value": "80%+ accuracy", "icon": "🎯", "earned": True})
        if stats.get("max_combo", 0) >= 10:
            achievements.append({"label": "Combo Master", "value": "10+ combo", "icon": "🔥", "earned": True})
        
        # Performance achievements
        if stats.get("level_reached", 1) >= 5:
            achievements.append({"label": "Level Up", "value": "Reached level 5", "icon": "⬆️", "earned": True})
        
        return achievements
    
    def format_time(self, seconds):
        """Format time in seconds to readable format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def format_number(self, number):
        """Format large numbers with commas"""
        if number >= 1000000:
            return f"{number/1000000:.1f}M"
        elif number >= 1000:
            return f"{number/1000:.1f}K"
        else:
            return str(int(number))
    
    def update(self, dt):
        """Update animations"""
        self.animation_time += dt
        
        # Update star particles
        for star in self.star_particles:
            star['phase'] += star['twinkle_speed'] * dt
        
        # Update floating particles
        self.particles = [(x, y, life - dt, vx, vy) for x, y, life, vx, vy in self.particles if life > 0]
        for i, (x, y, life, vx, vy) in enumerate(self.particles):
            self.particles[i] = (x + vx * dt, y + vy * dt, life, vx * 0.98, vy * 0.98 + 30 * dt)
        
        # Reveal stats progressively
        if len(self.stats_revealed) < 4 and self.animation_time > len(self.stats_revealed) * 0.5:
            category_index = len(self.stats_revealed)
            category_names = list(self.stats_categories.keys())
            if category_index < len(category_names):
                self.stats_revealed.append(category_names[category_index])
                self.play_sound('reveal')
                self.add_reveal_particles()
    
    def add_reveal_particles(self):
        """Add particles for stat reveal effect"""
        for _ in range(20):
            x = random.uniform(100, self.screen_width - 100)
            y = random.uniform(200, self.screen_height - 200)
            vx = random.uniform(-100, 100)
            vy = random.uniform(-200, -50)
            life = random.uniform(0.5, 1.0)
            color = random.choice([(255, 215, 0), (255, 255, 255), (100, 200, 255)])
            self.particles.append((x, y, life, vx, vy, color))
    
    def draw_background(self):
        """Draw animated background"""
        # Gradient background
        for y in range(self.screen_height):
            color_value = int(10 + (y / self.screen_height) * 20)
            color = (color_value, color_value, color_value + 5)
            pygame.draw.line(self.screen, color, (0, y), (self.screen_width, y))
        
        # Draw twinkling stars
        for star in self.star_particles:
            brightness = star['brightness'] * (0.5 + 0.5 * math.sin(star['phase']))
            color_value = int(255 * brightness)
            color = (color_value, color_value, color_value)
            pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), int(star['size']))
    
    def draw_particles(self):
        """Draw floating particles"""
        for particle in self.particles:
            if len(particle) == 6:  # (x, y, life, vx, vy, color)
                x, y, life, vx, vy, color = particle
                alpha = life / 1.0
                size = int(3 * alpha)
                if size > 0:
                    pygame.draw.circle(self.screen, color, (int(x), int(y)), size)
            else:  # Old format without color
                x, y, life, vx, vy = particle
                alpha = life / 1.0
                color = (int(255 * alpha), int(215 * alpha), int(100 * alpha))
                size = int(2 * alpha)
                if size > 0:
                    pygame.draw.circle(self.screen, color, (int(x), int(y)), size)
    
    def draw_stats_category(self, category_key, x, y, width, height, animation_progress):
        """Draw a single stats category"""
        category = self.stats_categories[category_key]
        
        # Category background
        bg_alpha = min(1.0, animation_progress)
        bg_color = tuple(int(c * 0.3 * bg_alpha) for c in category["color"])
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=10)
        
        # Category border
        border_color = tuple(int(c * bg_alpha) for c in category["color"])
        pygame.draw.rect(self.screen, border_color, bg_rect, 2, border_radius=10)
        
        # Category title
        if animation_progress > 0.3:
            title_alpha = min(1.0, (animation_progress - 0.3) / 0.3)
            title_color = tuple(int(c * title_alpha) for c in category["color"])
            title_text = self.header_font.render(category["title"], True, title_color)
            title_rect = title_text.get_rect(center=(x + width // 2, y + 30))
            self.screen.blit(title_text, title_rect)
        
        # Draw stats
        if animation_progress > 0.6:
            stats_alpha = min(1.0, (animation_progress - 0.6) / 0.4)
            stats_y = y + 70
            
            for stat in category["stats"]:
                # Stat icon (using colored circle as placeholder)
                icon_color = tuple(int(200 * stats_alpha) for _ in range(3))
                pygame.draw.circle(self.screen, icon_color, (x + 20, stats_y + 10), 8)
                
                # Stat label
                label_color = tuple(int(255 * stats_alpha) for _ in range(3))
                label_text = self.font.render(stat["label"], True, label_color)
                self.screen.blit(label_text, (x + 40, stats_y))
                
                # Stat value
                value_text = self.font.render(stat["value"], True, label_color)
                value_rect = value_text.get_rect(right=x + width - 20, centery=stats_y + 10)
                self.screen.blit(value_text, value_rect)
                
                stats_y += 35
    
    def draw(self):
        """Draw the stats screen"""
        self.draw_background()
        self.draw_particles()
        
        # Main title
        title_offset = int(abs(math.sin(self.animation_time * 2) * 5))
        title_text = self.title_font.render("GAME OVER", True, (255, 50, 50))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 80 + title_offset))
        
        # Title glow
        glow_size = int(5 + abs(math.sin(self.animation_time * 3) * 2))
        for i in range(glow_size):
            glow_alpha = 1 - (i / glow_size)
            glow_color = (255, 50, 50, int(100 * glow_alpha))
            glow_rect = title_rect.inflate(i * 6, i * 6)
            glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            glow_surface.fill(glow_color)
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.small_font.render("Press SPACE to continue | ESC for main menu", True, (150, 150, 150))
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, 130))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw stats categories
        category_width = 280
        category_height = 350
        category_spacing = 20
        total_width = 4 * category_width + 3 * category_spacing
        start_x = (self.screen_width - total_width) // 2
        start_y = 180
        
        for i, category_key in enumerate(self.stats_revealed):
            x = start_x + i * (category_width + category_spacing)
            y = start_y
            animation_progress = min(1.0, (self.animation_time - i * 0.5) / 0.5)
            self.draw_stats_category(category_key, x, y, category_width, category_height, animation_progress)
        
        # Action buttons
        if self.animation_time > 3:
            button_alpha = min(1.0, (self.animation_time - 3) / 0.5)
            
            # Retry button
            retry_rect = pygame.Rect(self.screen_width // 2 - 220, self.screen_height - 80, 200, 50)
            retry_color = (50, 150, 50, int(200 * button_alpha))
            pygame.draw.rect(self.screen, retry_color[:3], retry_rect, border_radius=8)
            retry_text = self.font.render("RETRY", True, (255, 255, 255))
            retry_text_rect = retry_text.get_rect(center=retry_rect.center)
            self.screen.blit(retry_text, retry_text_rect)
            
            # Main menu button
            menu_rect = pygame.Rect(self.screen_width // 2 + 20, self.screen_height - 80, 200, 50)
            menu_color = (50, 50, 150, int(200 * button_alpha))
            pygame.draw.rect(self.screen, menu_color[:3], menu_rect, border_radius=8)
            menu_text = self.font.render("MAIN MENU", True, (255, 255, 255))
            menu_text_rect = menu_text.get_rect(center=menu_rect.center)
            self.screen.blit(menu_text, menu_text_rect)
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "retry"
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
            
            if event.type == pygame.MOUSEBUTTONDOWN and self.animation_time > 3:
                mouse_x, mouse_y = event.pos
                
                # Check retry button
                retry_rect = pygame.Rect(self.screen_width // 2 - 220, self.screen_height - 80, 200, 50)
                if retry_rect.collidepoint(mouse_x, mouse_y):
                    self.play_sound('click')
                    return "retry"
                
                # Check main menu button
                menu_rect = pygame.Rect(self.screen_width // 2 + 20, self.screen_height - 80, 200, 50)
                if menu_rect.collidepoint(mouse_x, mouse_y):
                    self.play_sound('click')
                    return "menu"
        
        return None
    
    def show(self):
        """Show the stats screen"""
        # Reset animations
        self.animation_time = 0
        self.stats_revealed = []
        self.particles = []
        
        # Collect stats
        self.collect_stats()
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60) / 1000.0
            
            # Handle events
            result = self.handle_events()
            if result == "quit":
                return "quit"
            elif result == "retry":
                return "retry"
            elif result == "menu":
                return "menu"
            
            # Update
            self.update(dt)
            
            # Draw
            self.draw()
            pygame.display.flip()
        
        return "menu"
