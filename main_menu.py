import pygame
import pygame.sndarray
import sys
import math
import random
import numpy as np
from enum import Enum

class MenuState(Enum):
    MAIN = "main"
    SETTINGS = "settings"
    ENEMY_INDEX = "enemy_index"
    ABILITY_INDEX = "ability_index"
    INVENTORY = "inventory"
    SHOP = "shop"

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 150), hover_color=(150, 150, 200), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.hover_animation = 0
        self.particles = []
        
    def update(self, mouse_pos, dt, menu_instance=None):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Hover animation
        if self.is_hovered:
            self.hover_animation = min(1.0, self.hover_animation + dt * 5)
            # Add hover particles
            if not was_hovered:
                self.add_hover_particles()
                # Play hover sound
                if menu_instance:
                    menu_instance.play_menu_sound('hover')
        else:
            self.hover_animation = max(0.0, self.hover_animation - dt * 5)
        
        # Update particles
        self.particles = [(x, y, life - dt, vx, vy) for x, y, life, vx, vy in self.particles if life > 0]
        for i, (x, y, life, vx, vy) in enumerate(self.particles):
            self.particles[i] = (x + vx * dt, y + vy * dt, life, vx * 0.95, vy * 0.95 + 50 * dt)
    
    def add_hover_particles(self):
        import random
        for _ in range(10):
            x = self.rect.centerx + random.uniform(-self.rect.width//2, self.rect.width//2)
            y = self.rect.centery + random.uniform(-self.rect.height//2, self.rect.height//2)
            vx = random.uniform(-50, 50)
            vy = random.uniform(-100, -20)
            life = random.uniform(0.3, 0.8)
            self.particles.append((x, y, life, vx, vy))
    
    def draw(self, screen, font):
        # Draw particles
        for x, y, life, vx, vy in self.particles:
            alpha = life / 0.8
            color = (255, 215, 0, int(255 * alpha))
            size = int(3 * alpha)
            if size > 0:
                pygame.draw.circle(screen, color[:3], (int(x), int(y)), size)
        
        # Animated button background
        current_color = self.color
        if self.is_hovered:
            current_color = tuple(int(self.color[i] + (self.hover_color[i] - self.color[i]) * self.hover_animation) for i in range(3))
        
        # Draw button with rounded corners
        pygame.draw.rect(screen, current_color, self.rect, border_radius=8)
        
        # Draw border with glow effect
        if self.is_hovered:
            glow_alpha = self.hover_animation
            for i in range(3):
                glow_color = (255, 215, 0, int(100 * glow_alpha * (1 - i/3)))
                glow_rect = self.rect.inflate(i * 4, i * 4)
                pygame.draw.rect(screen, glow_color[:3], glow_rect, 2, border_radius=8 + i * 2)
        else:
            pygame.draw.rect(screen, (80, 80, 120), self.rect, 2, border_radius=8)
        
        # Draw text
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, event, menu_instance=None):
        clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered
        if clicked and menu_instance:
            # Play click sound
            if self.text == "Back":
                menu_instance.play_menu_sound('back')
            else:
                menu_instance.play_menu_sound('click')
        return clicked

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.state = MenuState.MAIN
        
        # Screen setup - support fullscreen
        self.screen_width = 1280
        self.screen_height = 720
        self.fullscreen = False
        
        # Check if we should start in fullscreen (from game settings or default)
        if game and hasattr(game, 'fullscreen') and game.fullscreen:
            self.fullscreen = True
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Get actual screen dimensions
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h
        else:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Audio system
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sound_enabled = True
        self.menu_sounds = self.create_menu_sounds()
        
        # Play menu music
        self.play_menu_music()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.header_font = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Background particles
        self.background_particles = []
        self.init_background_particles()
        
        # UI elements
        self.init_ui_elements()
        
        # Settings
        self.settings = {
            'master_volume': 0.8,
            'music_volume': 0.7,
            'sound_volume': 0.8,
            'fullscreen': False,
            'vsync': True,
            'particle_quality': 'high'
        }
        
        # Scrolling for indexes
        self.enemy_scroll_offset = 0
        self.ability_scroll_offset = 0
        self.max_scroll_speed = 500  # pixels per second
        self.scroll_friction = 0.9
        self.enemy_scroll_velocity = 0
        self.ability_scroll_velocity = 0
        
        # Settings interaction
        self.dragging_slider = None
        self.hovered_setting = None
        
        # Animation timers
        self.title_animation = 0
        self.menu_animation = 0
        
    def init_background_particles(self):
        import random
        for _ in range(50):
            x = random.uniform(0, self.screen_width)
            y = random.uniform(0, self.screen_height)
            vx = random.uniform(-20, 20)
            vy = random.uniform(-20, 20)
            size = random.uniform(1, 3)
            brightness = random.uniform(0.3, 1.0)
            self.background_particles.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'size': size, 'brightness': brightness})
    
    def init_ui_elements(self):
        # Main menu buttons
        self.main_buttons = [
            Button(self.screen_width//2 - 150, 210, 300, 60, "Start Game"),
            Button(self.screen_width//2 - 150, 290, 300, 60, "Endless Mode"),
            Button(self.screen_width//2 - 150, 370, 300, 60, "Settings"),
            Button(self.screen_width//2 - 150, 450, 300, 60, "Enemy Index"),
            Button(self.screen_width//2 - 150, 530, 300, 60, "Ability Index"),
            Button(self.screen_width//2 - 150, 610, 300, 60, "Exit")
        ]
        
        # Settings buttons
        self.settings_buttons = [
            Button(100, 600, 200, 50, "Apply"),
            Button(320, 600, 200, 50, "Reset"),
            Button(self.screen_width - 300, 600, 200, 50, "Back")
        ]
        
        # Back button for other menus
        self.back_button = Button(self.screen_width//2 - 100, 600, 200, 50, "Back")
    
    def update_background_particles(self, dt):
        for particle in self.background_particles:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            
            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = self.screen_width
            elif particle['x'] > self.screen_width:
                particle['x'] = 0
            if particle['y'] < 0:
                particle['y'] = self.screen_height
            elif particle['y'] > self.screen_height:
                particle['y'] = 0
    
    def draw_background(self):
        # Gradient background
        for y in range(self.screen_height):
            color_value = int(20 + (y / self.screen_height) * 30)
            color = (color_value, color_value, color_value + 10)
            pygame.draw.line(self.screen, color, (0, y), (self.screen_width, y))
        
        # Draw background particles
        for particle in self.background_particles:
            alpha = particle['brightness']
            color = (int(100 * alpha), int(100 * alpha), int(150 * alpha))
            pygame.draw.circle(self.screen, color, (int(particle['x']), int(particle['y'])), int(particle['size']))
    
    def draw_main_menu(self, dt):
        # Update animations
        self.title_animation += dt
        self.menu_animation += dt
        
        # Draw animated title
        title_offset = int(abs(pygame.math.Vector2(0, 1).rotate(self.title_animation * 50).y) * 5)
        title_text = self.title_font.render("ARENA SURVIVOR", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, 100 + title_offset))
        
        # Title glow effect
        glow_size = int(5 + abs(pygame.math.Vector2(1, 0).rotate(self.title_animation * 30).x) * 2)
        for i in range(glow_size):
            glow_alpha = 1 - (i / glow_size)
            glow_color = (255, 215, 0, int(50 * glow_alpha))
            glow_rect = title_rect.inflate(i * 4, i * 4)
            glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            glow_surface.fill(glow_color)
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.small_font.render("A Top-Down Survival Shooter", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width//2, 150))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Update and draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.main_buttons:
            button.update(mouse_pos, dt, self)
            button.draw(self.screen, self.font)
    
    def draw_settings(self, dt):
        # Title
        title_text = self.header_font.render("SETTINGS", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Settings options with interaction
        settings_data = [
            ("master_volume", "Master Volume", self.settings['master_volume'], 0.0, 1.0),
            ("music_volume", "Music Volume", self.settings['music_volume'], 0.0, 1.0),
            ("sound_volume", "Sound Volume", self.settings['sound_volume'], 0.0, 1.0),
            ("fullscreen", "Fullscreen", self.settings['fullscreen'], None, None),
            ("vsync", "VSync", self.settings['vsync'], None, None),
            ("particle_quality", "Particle Quality", self.settings['particle_quality'], None, None)
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        y_offset = 180
        for setting_key, setting_name, value, min_val, max_val in settings_data:
            # Draw setting name
            text = self.font.render(setting_name, True, (255, 255, 255))
            self.screen.blit(text, (100, y_offset))
            
            # Draw setting value
            if isinstance(value, float):
                # Draw slider track
                slider_rect = pygame.Rect(400, y_offset + 5, 300, 20)
                pygame.draw.rect(self.screen, (60, 60, 80), slider_rect, border_radius=10)
                
                # Slider handle
                handle_x = int(slider_rect.x + (value - min_val) / (max_val - min_val) * slider_rect.width)
                handle_rect = pygame.Rect(handle_x - 10, slider_rect.y - 5, 20, 30)
                
                # Highlight if hovering
                is_hovered = handle_rect.collidepoint(mouse_pos)
                handle_color = (255, 235, 0) if is_hovered else (255, 215, 0)
                pygame.draw.rect(self.screen, handle_color, handle_rect, border_radius=5)
                
                # Value text
                value_text = self.small_font.render(f"{int(value * 100)}%", True, (200, 200, 200))
                self.screen.blit(value_text, (720, y_offset + 5))
                
                # Store slider rect for interaction
                if not hasattr(self, 'slider_rects'):
                    self.slider_rects = {}
                self.slider_rects[setting_key] = slider_rect
                
            else:
                # Draw toggle or text
                if isinstance(value, bool):
                    toggle_rect = pygame.Rect(400, y_offset, 60, 30)
                    color = (0, 255, 0) if value else (255, 0, 0)
                    
                    # Highlight if hovering
                    is_hovered = toggle_rect.collidepoint(mouse_pos)
                    if is_hovered:
                        color = tuple(min(255, c + 50) for c in color)
                    
                    pygame.draw.rect(self.screen, color, toggle_rect, border_radius=15)
                    status_text = "ON" if value else "OFF"
                    status_surface = self.small_font.render(status_text, True, (255, 255, 255))
                    status_rect = status_surface.get_rect(center=toggle_rect.center)
                    self.screen.blit(status_surface, status_rect)
                    
                    # Store toggle rect for interaction
                    if not hasattr(self, 'toggle_rects'):
                        self.toggle_rects = {}
                    self.toggle_rects[setting_key] = toggle_rect
                else:
                    # Dropdown for particle quality
                    dropdown_rect = pygame.Rect(400, y_offset, 150, 30)
                    pygame.draw.rect(self.screen, (60, 60, 80), dropdown_rect, border_radius=5)
                    
                    # Highlight if hovering
                    is_hovered = dropdown_rect.collidepoint(mouse_pos)
                    border_color = (120, 120, 160) if is_hovered else (80, 80, 100)
                    pygame.draw.rect(self.screen, border_color, dropdown_rect, 2, border_radius=5)
                    
                    value_text = self.font.render(str(value), True, (200, 200, 200))
                    value_rect = value_text.get_rect(center=dropdown_rect.center)
                    self.screen.blit(value_text, value_rect)
                    
                    # Store dropdown rect for interaction
                    if not hasattr(self, 'dropdown_rects'):
                        self.dropdown_rects = {}
                    self.dropdown_rects[setting_key] = dropdown_rect
            
            y_offset += 60
        
        # Update and draw buttons
        for button in self.settings_buttons:
            button.update(mouse_pos, dt, self)
            button.draw(self.screen, self.font)
    
    def draw_enemy_index(self, dt):
        # Update scrolling physics
        self.update_scrolling(dt, "enemy")
        
        # Title
        title_text = self.header_font.render("ENEMY INDEX", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        inst_text = self.small_font.render("Use mouse wheel or drag to scroll", True, (150, 150, 150))
        inst_rect = inst_text.get_rect(center=(self.screen_width//2, 110))
        self.screen.blit(inst_text, inst_rect)
        
        # Extended enemy data with detailed descriptions and unique abilities
        enemies = [
            {
                "name": "Basic", 
                "hp": 50, 
                "damage": 10, 
                "speed": 100, 
                "description": "Standard enemy with balanced stats",
                "verbal_desc": "The Basic enemy is your most common foe. It moves at moderate speed and deals average damage. While not particularly threatening alone, they become dangerous in groups. Their simple attack patterns make them good targets for practicing your aim and dodging skills.",
                "unique_ability": "None - Relies on numbers and basic movement patterns"
            },
            {
                "name": "Fast", 
                "hp": 30, 
                "damage": 15, 
                "speed": 200, 
                "description": "Quick but fragile enemy",
                "verbal_desc": "The Fast enemy is a nightmare for beginners. With twice the speed of Basic enemies, they can quickly close distance and overwhelm you with their rapid attacks. Their low health means they die quickly, but you need to hit them first!",
                "unique_ability": "Dash Strike - Can briefly boost speed to close gaps"
            },
            {
                "name": "Tank", 
                "hp": 100, 
                "damage": 20, 
                "speed": 50, 
                "description": "Slow but heavily armored",
                "verbal_desc": "The Tank enemy is a walking fortress. While their slow speed makes them easy to outrun, their high health pool means they can absorb significant punishment. They deal heavy damage and can block your projectiles with their thick armor.",
                "unique_ability": "Armor Plating - Reduces incoming damage by 25%"
            },
            {
                "name": "Sniper", 
                "hp": 40, 
                "damage": 40, 
                "speed": 80, 
                "description": "Long-range attacker with high damage",
                "verbal_desc": "The Sniper enemy prefers to fight from a distance. They maintain optimal range and unleash devastating high-damage attacks. Their accuracy is impressive, but they're vulnerable when you get close. Watch for their laser sight before they shoot!",
                "unique_ability": "Precision Shot - Charges up for extra damage every 3 seconds"
            },
            {
                "name": "Swarm", 
                "hp": 20, 
                "damage": 8, 
                "speed": 150, 
                "description": "Comes in large numbers",
                "verbal_desc": "Swarm enemies are never alone. These small, fast-moving creatures attack in coordinated waves. While individually weak, their strength lies in overwhelming numbers and unpredictable movement patterns. Clear them quickly before they surround you!",
                "unique_ability": "Group Coordination - Gains speed boost when near other Swarm enemies"
            },
            {
                "name": "Healer", 
                "hp": 60, 
                "damage": 5, 
                "speed": 70, 
                "description": "Supports other enemies",
                "verbal_desc": "The Healer enemy is a priority target in any battle. While their direct damage is minimal, they can restore health to nearby enemies, prolonging fights significantly. Eliminate healers first to prevent them from turning the tide of battle.",
                "unique_ability": "Restoration Aura - Heals nearby enemies for 5 HP per second"
            },
            {
                "name": "Bomber", 
                "hp": 80, 
                "damage": 60, 
                "speed": 60, 
                "description": "Explodes on contact",
                "verbal_desc": "The Bomber enemy is a walking time bomb. They move deliberately toward you, and upon death or contact, they explode in a large area of effect. Keep your distance and take them out from range to avoid their devastating blast radius.",
                "unique_ability": "Explosive Death - Deals 60 damage in a 150-pixel radius"
            },
            {
                "name": "Elite", 
                "hp": 150, 
                "damage": 25, 
                "speed": 90, 
                "description": "Enhanced version of basic enemy",
                "verbal_desc": "Elite enemies are veteran warriors who have survived many battles. They combine the balanced approach of Basic enemies with enhanced stats and combat experience. They're smarter, tougher, and more dangerous than their regular counterparts.",
                "unique_ability": "Combat Experience - 20% chance to dodge incoming projectiles"
            },
            {
                "name": "Boss", 
                "hp": 500, 
                "damage": 30, 
                "speed": 80, 
                "description": "Powerful boss enemy",
                "verbal_desc": "The Boss enemy is a formidable opponent that tests all your skills. With high health, significant damage output, and multiple attack patterns, they require strategy and patience to defeat. Boss battles are intense encounters that push you to your limits.",
                "unique_ability": "Multi-Attack - Can shoot in 3 directions simultaneously"
            },
            {
                "name": "Mega Boss", 
                "hp": 1000, 
                "damage": 50, 
                "speed": 60, 
                "description": "Ultimate boss enemy",
                "verbal_desc": "The Mega Boss is the ultimate challenge. This towering behemoth possesses immense health, devastating attacks, and special abilities that can turn the battlefield into chaos. Only the most skilled players can hope to defeat this legendary foe.",
                "unique_ability": "Arena Control - Creates shockwaves and summons minions"
            }
        ]
        
        # Draw enemy cards with scrolling
        card_width = 220
        card_height = 150
        cards_per_row = 5
        x_start = (self.screen_width - (cards_per_row * card_width + (cards_per_row - 1) * 20)) // 2
        y_start = 150 - self.enemy_scroll_offset
        
        # Create clipping region for scrolling area
        clip_rect = pygame.Rect(0, 150, self.screen_width, self.screen_height - 250)
        self.screen.set_clip(clip_rect)
        
        for i, enemy in enumerate(enemies):
            row = i // cards_per_row
            col = i % cards_per_row
            x = x_start + col * (card_width + 20)
            y = y_start + row * (card_height + 20)
            
            # Skip if outside visible area
            if y + card_height < clip_rect.y or y > clip_rect.y + clip_rect.height:
                continue
            
            # Card background
            card_rect = pygame.Rect(x, y, card_width, card_height)
            pygame.draw.rect(self.screen, (60, 60, 80), card_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 100, 120), card_rect, 2, border_radius=10)
            
            # Enemy name
            name_text = self.font.render(enemy["name"], True, (255, 215, 0))
            name_rect = name_text.get_rect(center=(card_rect.centerx, card_rect.y + 20))
            self.screen.blit(name_text, name_rect)
            
            # Enemy stats (compact)
            hp_color = (255, 100, 100) if enemy['hp'] >= 100 else (255, 200, 100) if enemy['hp'] >= 50 else (100, 255, 100)
            stats_text = [
                (f"HP: {enemy['hp']}", hp_color),
                (f"DMG: {enemy['damage']}", (255, 150, 150)),
                (f"SPD: {enemy['speed']}", (150, 150, 255))
            ]
            
            for j, (stat, color) in enumerate(stats_text):
                stat_surface = self.small_font.render(stat, True, color)
                stat_rect = stat_surface.get_rect(center=(card_rect.centerx, card_rect.y + 45 + j * 15))
                self.screen.blit(stat_surface, stat_rect)
            
            # Unique ability (highlighted)
            ability_text = self.small_font.render("Ability:", True, (200, 200, 200))
            ability_rect = ability_text.get_rect(midleft=(card_rect.x + 10, card_rect.y + 95))
            self.screen.blit(ability_text, ability_rect)
            
            ability_lines = self.wrap_text(enemy["unique_ability"], 25)
            for j, line in enumerate(ability_lines[:1]):  # Max 1 line for ability
                ability_surface = self.small_font.render(line, True, (100, 255, 100))
                ability_desc_rect = ability_surface.get_rect(midleft=(card_rect.x + 10, card_rect.y + 110))
                self.screen.blit(ability_surface, ability_desc_rect)
        
        # Reset clipping
        self.screen.set_clip(None)
        
        # Draw scroll indicators if needed
        total_height = len(enemies) // cards_per_row * (card_height + 20) + (card_height + 20)
        if total_height > clip_rect.height:
            self.draw_scroll_indicators(clip_rect, self.enemy_scroll_offset, total_height)
        
        # Check for hover to show detailed description
        mouse_pos = pygame.mouse.get_pos()
        hovered_enemy = None
        
        for i, enemy in enumerate(enemies):
            row = i // cards_per_row
            col = i % cards_per_row
            x = x_start + col * (card_width + 20)
            y = y_start + row * (card_height + 20)
            
            card_rect = pygame.Rect(x, y, card_width, card_height)
            if card_rect.collidepoint(mouse_pos):
                hovered_enemy = enemy
                # Highlight hovered card
                pygame.draw.rect(self.screen, (120, 120, 160), card_rect, 3, border_radius=10)
                break
        
        # Show detailed description panel if hovering
        if hovered_enemy:
            self.draw_enemy_detail_panel(hovered_enemy, mouse_pos)
        
        # Back button
        self.back_button.update(mouse_pos, dt, self)
        self.back_button.draw(self.screen, self.font)
    
    def draw_enemy_detail_panel(self, enemy, mouse_pos):
        """Draw detailed information panel for hovered enemy"""
        panel_width = 400
        panel_height = 250
        panel_x = min(mouse_pos[0] + 20, self.screen_width - panel_width - 20)
        panel_y = min(mouse_pos[1] + 20, self.screen_height - panel_height - 20)
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (40, 40, 60), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 140), panel_rect, 2, border_radius=10)
        
        # Enemy name (larger)
        name_text = self.font.render(enemy["name"], True, (255, 215, 0))
        name_rect = name_text.get_rect(midleft=(panel_x + 15, panel_y + 25))
        self.screen.blit(name_text, name_rect)
        
        # Stats summary
        stats_text = f"HP: {enemy['hp']} | DMG: {enemy['damage']} | SPD: {enemy['speed']}"
        stats_surface = self.small_font.render(stats_text, True, (200, 200, 200))
        stats_rect = stats_surface.get_rect(midleft=(panel_x + 15, panel_y + 50))
        self.screen.blit(stats_surface, stats_rect)
        
        # Verbal description (wrapped)
        desc_title = self.small_font.render("Description:", True, (150, 150, 255))
        desc_title_rect = desc_title.get_rect(midleft=(panel_x + 15, panel_y + 75))
        self.screen.blit(desc_title, desc_title_rect)
        
        desc_lines = self.wrap_text(enemy["verbal_desc"], 35)
        for i, line in enumerate(desc_lines[:4]):  # Max 4 lines
            desc_surface = self.small_font.render(line, True, (220, 220, 220))
            desc_rect = desc_surface.get_rect(midleft=(panel_x + 15, panel_y + 95 + i * 20))
            self.screen.blit(desc_surface, desc_rect)
        
        # Unique ability
        ability_title = self.small_font.render("Unique Ability:", True, (100, 255, 100))
        ability_title_rect = ability_title.get_rect(midleft=(panel_x + 15, panel_y + 180))
        self.screen.blit(ability_title, ability_title_rect)
        
        ability_lines = self.wrap_text(enemy["unique_ability"], 35)
        for i, line in enumerate(ability_lines[:2]):  # Max 2 lines
            ability_surface = self.small_font.render(line, True, (100, 255, 100))
            ability_rect = ability_surface.get_rect(midleft=(panel_x + 15, panel_y + 200 + i * 20))
            self.screen.blit(ability_surface, ability_rect)
    
    def draw_ability_index(self, dt):
        # Update scrolling physics
        self.update_scrolling(dt, "ability")
        
        # Title
        title_text = self.header_font.render("ABILITY INDEX", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        inst_text = self.small_font.render("Use mouse wheel or drag to scroll", True, (150, 150, 150))
        inst_rect = inst_text.get_rect(center=(self.screen_width//2, 110))
        self.screen.blit(inst_text, inst_rect)
        
        # Extended ability data with detailed descriptions
        abilities = [
            {
                "name": "Dash", 
                "cooldown": "5s", 
                "description": "Quick dash to avoid danger and reposition",
                "verbal_desc": "Dash allows you to quickly teleport a short distance in the direction you're moving. This essential defensive ability helps you escape tight situations and reposition for better angles. Master the timing to dodge enemy attacks and projectiles.",
                "unique_feature": "Invincibility frames during dash animation"
            },
            {
                "name": "Shield", 
                "cooldown": "10s", 
                "description": "Temporary protection from all damage",
                "verbal_desc": "Shield projects a protective barrier around you that absorbs incoming damage for a limited time. While active, you can continue attacking and moving normally. Use it when overwhelmed or to survive otherwise fatal attacks.",
                "unique_feature": "Absorbs up to 100 damage before breaking"
            },
            {
                "name": "Heal", 
                "cooldown": "15s", 
                "description": "Restore health over time",
                "verbal_desc": "Heal restores your health gradually over several seconds. This ability can turn the tide of battle by allowing you to recover from damage without needing health pickups. Use it between waves or when you have a moment of safety.",
                "unique_feature": "Restores 50 HP over 5 seconds"
            },
            {
                "name": "Multi-Shot", 
                "cooldown": "8s", 
                "description": "Fire multiple projectiles in a spread pattern",
                "verbal_desc": "Multi-Shot transforms your next attack into a devastating spread of projectiles. Perfect for clearing groups of enemies or covering a wide area. The spread pattern ensures you hit multiple targets simultaneously.",
                "unique_feature": "Fires 5 projectiles in a cone pattern"
            },
            {
                "name": "Rapid Fire", 
                "cooldown": "6s", 
                "description": "Increased fire rate for a short duration",
                "verbal_desc": "Rapid Fire dramatically increases your attack speed for a brief period. This ability excels at overwhelming single targets with a barrage of projectiles. Combine with other damage boosts for maximum effectiveness.",
                "unique_feature": "3x fire rate for 4 seconds"
            },
            {
                "name": "Piercing Shots", 
                "cooldown": "12s", 
                "description": "Projectiles pierce through enemies",
                "verbal_desc": "Piercing Shots allows your projectiles to pass through multiple enemies. This ability is incredibly effective against lines of enemies or large groups. Each projectile maintains its damage through all hits.",
                "unique_feature": "Projectiles pierce up to 5 enemies"
            },
            {
                "name": "Explosive Rounds", 
                "cooldown": "10s", 
                "description": "Projectiles explode on impact",
                "verbal_desc": "Explosive Rounds cause your projectiles to detonate on impact, dealing area damage to nearby enemies. This creates devastating chain reactions and is perfect for clustered groups of foes.",
                "unique_feature": "30-pixel radius explosion on impact"
            },
            {
                "name": "Time Slow", 
                "cooldown": "20s", 
                "description": "Slow down time for all enemies",
                "verbal_desc": "Time Slow creates a temporal field that dramatically reduces enemy movement and attack speed. This powerful ability gives you precious moments to reposition, heal, or unleash devastating attacks on slowed targets.",
                "unique_feature": "Enemies move at 25% speed for 6 seconds"
            },
            {
                "name": "Teleport", 
                "cooldown": "8s", 
                "description": "Instant teleport to mouse position",
                "verbal_desc": "Teleport allows instant relocation to your mouse cursor position. This ultimate mobility tool lets you escape any danger or instantly close distances. Mastering teleportation is key to high-level play.",
                "unique_feature": "500-pixel maximum range"
            },
            {
                "name": "Area Damage", 
                "cooldown": "15s", 
                "description": "Deal damage in an area around you",
                "verbal_desc": "Area Damage unleashes a powerful shockwave that damages all enemies in a large radius around you. This defensive ability clears space and damages nearby threats simultaneously.",
                "unique_feature": "200-pixel radius area damage"
            },
            {
                "name": "Life Steal", 
                "cooldown": "12s", 
                "description": "Heal for a percentage of damage dealt",
                "verbal_desc": "Life Steal converts a portion of your damage into healing for the next several seconds. This offensive sustain ability lets you stay in the fight longer by turning your damage output into survivability.",
                "unique_feature": "25% of damage dealt becomes healing"
            },
            {
                "name": "Invincibility", 
                "cooldown": "30s", 
                "description": "Complete immunity for a short time",
                "verbal_desc": "Invincibility grants complete immunity from all damage for a brief period. This ultimate defensive ability saves you from certain death and allows you to attack without fear of retaliation during its duration.",
                "unique_feature": "Complete damage immunity for 3 seconds"
            }
        ]
        
        # Draw ability cards with scrolling
        y_offset = 150 - self.ability_scroll_offset
        card_height = 80
        
        # Create clipping region for scrolling area
        clip_rect = pygame.Rect(0, 150, self.screen_width, self.screen_height - 250)
        self.screen.set_clip(clip_rect)
        
        for ability in abilities:
            # Skip if outside visible area
            if y_offset + card_height < clip_rect.y or y_offset > clip_rect.y + clip_rect.height:
                y_offset += 90
                continue
            
            # Card background
            card_rect = pygame.Rect(150, y_offset, self.screen_width - 300, card_height)
            pygame.draw.rect(self.screen, (60, 60, 80), card_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 100, 120), card_rect, 2, border_radius=10)
            
            # Ability name
            name_text = self.font.render(ability["name"], True, (255, 215, 0))
            name_rect = name_text.get_rect(midleft=(card_rect.x + 20, card_rect.y + 20))
            self.screen.blit(name_text, name_rect)
            
            # Cooldown and type indicator
            cooldown_color = (255, 100, 100) if int(ability['cooldown'].rstrip('s')) <= 8 else (255, 200, 100) if int(ability['cooldown'].rstrip('s')) <= 15 else (100, 100, 255)
            cooldown_text = self.small_font.render(f"Cooldown: {ability['cooldown']}", True, cooldown_color)
            cooldown_rect = cooldown_text.get_rect(midleft=(card_rect.x + 20, card_rect.y + 40))
            self.screen.blit(cooldown_text, cooldown_rect)
            
            # Unique feature (highlighted)
            feature_text = self.small_font.render("Feature:", True, (200, 200, 200))
            feature_rect = feature_text.get_rect(midleft=(card_rect.x + 20, card_rect.y + 60))
            self.screen.blit(feature_text, feature_rect)
            
            feature_lines = self.wrap_text(ability["unique_feature"], 35)
            for j, line in enumerate(feature_lines[:1]):  # Max 1 line for feature
                feature_surface = self.small_font.render(line, True, (100, 255, 255))
                feature_desc_rect = feature_surface.get_rect(midleft=(card_rect.x + 20, card_rect.y + 75))
                self.screen.blit(feature_surface, feature_desc_rect)
            
            y_offset += 90
        
        # Reset clipping
        self.screen.set_clip(None)
        
        # Draw scroll indicators if needed
        total_height = len(abilities) * 90
        if total_height > clip_rect.height:
            self.draw_scroll_indicators(clip_rect, self.ability_scroll_offset, total_height)
        
        # Check for hover to show detailed description
        mouse_pos = pygame.mouse.get_pos()
        hovered_ability = None
        y_offset = 150 - self.ability_scroll_offset
        
        for ability in abilities:
            # Skip if outside visible area
            if y_offset + card_height < clip_rect.y or y_offset > clip_rect.y + clip_rect.height:
                y_offset += 90
                continue
            
            card_rect = pygame.Rect(150, y_offset, self.screen_width - 300, card_height)
            if card_rect.collidepoint(mouse_pos):
                hovered_ability = ability
                # Highlight hovered card
                pygame.draw.rect(self.screen, (120, 120, 160), card_rect, 3, border_radius=10)
                break
            
            y_offset += 90
        
        # Show detailed description panel if hovering
        if hovered_ability:
            self.draw_ability_detail_panel(hovered_ability, mouse_pos)
        
        # Back button
        self.back_button.update(mouse_pos, dt, self)
        self.back_button.draw(self.screen, self.font)
    
    def draw_ability_detail_panel(self, ability, mouse_pos):
        """Draw detailed information panel for hovered ability"""
        panel_width = 450
        panel_height = 280
        panel_x = min(mouse_pos[0] + 20, self.screen_width - panel_width - 20)
        panel_y = min(mouse_pos[1] + 20, self.screen_height - panel_height - 20)
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (40, 40, 60), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 140), panel_rect, 2, border_radius=10)
        
        # Ability name (larger)
        name_text = self.font.render(ability["name"], True, (255, 215, 0))
        name_rect = name_text.get_rect(midleft=(panel_x + 15, panel_y + 25))
        self.screen.blit(name_text, name_rect)
        
        # Cooldown and type
        cooldown_value = int(ability['cooldown'].rstrip('s'))
        cooldown_color = (100, 255, 100) if cooldown_value <= 8 else (255, 255, 100) if cooldown_value <= 15 else (255, 100, 100)
        type_text = "Quick" if cooldown_value <= 8 else "Medium" if cooldown_value <= 15 else "Long"
        
        stats_text = f"Cooldown: {ability['cooldown']} | Type: {type_text}"
        stats_surface = self.small_font.render(stats_text, True, cooldown_color)
        stats_rect = stats_surface.get_rect(midleft=(panel_x + 15, panel_y + 50))
        self.screen.blit(stats_surface, stats_rect)
        
        # Verbal description (wrapped)
        desc_title = self.small_font.render("Description:", True, (150, 150, 255))
        desc_title_rect = desc_title.get_rect(midleft=(panel_x + 15, panel_y + 75))
        self.screen.blit(desc_title, desc_title_rect)
        
        desc_lines = self.wrap_text(ability["verbal_desc"], 40)
        for i, line in enumerate(desc_lines[:4]):  # Max 4 lines
            desc_surface = self.small_font.render(line, True, (220, 220, 220))
            desc_rect = desc_surface.get_rect(midleft=(panel_x + 15, panel_y + 95 + i * 20))
            self.screen.blit(desc_surface, desc_rect)
        
        # Unique feature
        feature_title = self.small_font.render("Unique Feature:", True, (100, 255, 255))
        feature_title_rect = feature_title.get_rect(midleft=(panel_x + 15, panel_y + 180))
        self.screen.blit(feature_title, feature_title_rect)
        
        feature_lines = self.wrap_text(ability["unique_feature"], 40)
        for i, line in enumerate(feature_lines[:2]):  # Max 2 lines
            feature_surface = self.small_font.render(line, True, (100, 255, 255))
            feature_rect = feature_surface.get_rect(midleft=(panel_x + 15, panel_y + 200 + i * 20))
            self.screen.blit(feature_surface, feature_rect)
        
        # Usage tip
        tip_text = "Hover over abilities to see detailed information"
        tip_surface = self.small_font.render(tip_text, True, (150, 150, 150))
        tip_rect = tip_surface.get_rect(midleft=(panel_x + 15, panel_y + 240))
        self.screen.blit(tip_surface, tip_rect)
    
    def draw_inventory_ui(self, dt):
        # Title
        title_text = self.header_font.render("INVENTORY", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Inventory grid placeholder
        grid_size = 50
        grid_cols = 10
        grid_rows = 6
        grid_start_x = (self.screen_width - grid_cols * grid_size - (grid_cols - 1) * 10) // 2
        grid_start_y = 150
        
        for row in range(grid_rows):
            for col in range(grid_cols):
                x = grid_start_x + col * (grid_size + 10)
                y = grid_start_y + row * (grid_size + 10)
                
                # Draw inventory slot
                slot_rect = pygame.Rect(x, y, grid_size, grid_size)
                pygame.draw.rect(self.screen, (60, 60, 80), slot_rect, border_radius=5)
                pygame.draw.rect(self.screen, (80, 80, 100), slot_rect, 1, border_radius=5)
        
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.update(mouse_pos, dt, self)
        self.back_button.draw(self.screen, self.font)
    
    def draw_shop_ui(self, dt):
        # Title
        title_text = self.header_font.render("SHOP", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(self.screen_width//2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Shop items placeholder
        shop_items = [
            {"name": "Health Potion", "price": 50, "description": "Restore 50 HP"},
            {"name": "Damage Boost", "price": 100, "description": "+10% damage for 5 minutes"},
            {"name": "Speed Boost", "price": 75, "description": "+20% speed for 3 minutes"},
            {"name": "Extra Life", "price": 200, "description": "Gain an extra life"}
        ]
        
        # Draw shop items
        item_height = 80
        y_start = 150
        
        for i, item in enumerate(shop_items):
            y = y_start + i * (item_height + 20)
            
            # Item background
            item_rect = pygame.Rect(200, y, self.screen_width - 400, item_height)
            pygame.draw.rect(self.screen, (60, 60, 80), item_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 100, 120), item_rect, 2, border_radius=10)
            
            # Item name
            name_text = self.font.render(item["name"], True, (255, 215, 0))
            name_rect = name_text.get_rect(midleft=(item_rect.x + 20, item_rect.y + 25))
            self.screen.blit(name_text, name_rect)
            
            # Item price
            price_text = self.font.render(f"${item['price']}", True, (0, 255, 0))
            price_rect = price_text.get_rect(midright=(item_rect.right - 20, item_rect.y + 25))
            self.screen.blit(price_text, price_rect)
            
            # Item description
            desc_surface = self.small_font.render(item["description"], True, (200, 200, 200))
            desc_rect = desc_surface.get_rect(midleft=(item_rect.x + 20, item_rect.y + 55))
            self.screen.blit(desc_surface, desc_rect)
        
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.update(mouse_pos, dt, self)
        self.back_button.draw(self.screen, self.font)
    
    def create_menu_sounds(self):
        """Create menu sound effects"""
        sounds = {}
        
        # Hover sound
        sounds['hover'] = self.generate_menu_sound(800, 0.05, 'hover')
        
        # Click sound
        sounds['click'] = self.generate_menu_sound(600, 0.1, 'click')
        
        # Back sound
        sounds['back'] = self.generate_menu_sound(400, 0.15, 'back')
        
        return sounds
    
    def generate_menu_sound(self, frequency, duration, sound_type):
        """Generate a menu sound effect"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        waves = np.zeros(samples, dtype=np.float32)
        for i in range(samples):
            t = float(i) / sample_rate
            
            if sound_type == 'hover':
                # Soft whoosh sound
                envelope = math.exp(-t * 10)
                freq = frequency * (1 + t * 0.5)
                waves[i] = envelope * math.sin(2 * math.pi * freq * t)
            elif sound_type == 'click':
                # Sharp click sound
                envelope = math.exp(-t * 30)
                waves[i] = envelope * math.sin(2 * math.pi * frequency * t)
                waves[i] += envelope * random.uniform(-0.3, 0.3)
            elif sound_type == 'back':
                # Lower pitch click
                envelope = math.exp(-t * 20)
                freq = frequency * 0.7
                waves[i] = envelope * math.sin(2 * math.pi * freq * t)
            else:
                envelope = math.exp(-t * 5)
                waves[i] = envelope * math.sin(2 * math.pi * frequency * t)
        
        # Create stereo sound with reduced volume (1/3 of original)
        volume_multiplier = 32767 / 3  # 3x quieter
        stereo_waves = np.zeros((samples, 2), dtype=np.int16)
        stereo_waves[:, 0] = waves * volume_multiplier
        stereo_waves[:, 1] = waves * volume_multiplier
        
        return pygame.sndarray.make_sound(stereo_waves)
    
    def play_menu_sound(self, sound_name):
        """Play a menu sound effect"""
        if self.sound_enabled and sound_name in self.menu_sounds:
            self.menu_sounds[sound_name].play()
    
    def play_menu_music(self):
        """Generate and play simple menu music"""
        # Create a simple looping melody
        duration = 8.0
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        # Simple melody notes
        melody_freqs = [220, 247, 262, 294, 330, 294, 262, 247]  # A3, B3, C4, D4, E4, D4, C4, B3
        
        waves = np.zeros(samples, dtype=np.float32)
        for i in range(samples):
            t = float(i) / sample_rate
            
            # Find current note
            note_duration = duration / len(melody_freqs)
            note_index = int(t / note_duration) % len(melody_freqs)
            note_t = (t % note_duration) / note_duration
            
            freq = melody_freqs[note_index]
            
            # Simple envelope
            envelope = 0.2 * math.sin(math.pi * note_t)
            
            # Add some harmony
            waves[i] = envelope * (
                0.6 * math.sin(2 * math.pi * freq * t) +
                0.3 * math.sin(2 * math.pi * freq * 1.5 * t) +
                0.1 * math.sin(2 * math.pi * freq * 2 * t)
            )
        
        # Create stereo sound with reduced volume (1/3 of original)
        volume_multiplier = 32767 / 3  # 3x quieter
        stereo_waves = np.zeros((samples, 2), dtype=np.int16)
        stereo_waves[:, 0] = waves * volume_multiplier
        stereo_waves[:, 1] = waves * volume_multiplier
        
        self.menu_music = pygame.sndarray.make_sound(stereo_waves)
        self.menu_music.play(-1)  # Loop indefinitely
    
    def wrap_text(self, text, max_chars):
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) <= max_chars:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def update_scrolling(self, dt, scroll_type):
        """Update scrolling physics"""
        if scroll_type == "enemy":
            # Apply friction
            self.enemy_scroll_velocity *= self.scroll_friction
            self.enemy_scroll_offset += self.enemy_scroll_velocity * dt
            
            # Clamp offset
            max_offset = max(0, 0)  # Will be calculated based on content
            self.enemy_scroll_offset = max(0, self.enemy_scroll_offset)
            
        elif scroll_type == "ability":
            # Apply friction
            self.ability_scroll_velocity *= self.scroll_friction
            self.ability_scroll_offset += self.ability_scroll_velocity * dt
            
            # Clamp offset
            self.ability_scroll_offset = max(0, self.ability_scroll_offset)
    
    def draw_scroll_indicators(self, clip_rect, scroll_offset, total_height):
        """Draw scroll indicators when content is scrollable"""
        # Draw scroll bar on the right side
        scrollbar_width = 10
        scrollbar_x = self.screen_width - 30
        scrollbar_height = clip_rect.height - 20
        scrollbar_y = clip_rect.y + 10
        
        # Scrollbar background
        scrollbar_bg = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(self.screen, (40, 40, 50), scrollbar_bg, border_radius=5)
        
        # Scrollbar handle
        if total_height > clip_rect.height:
            handle_height = max(20, scrollbar_height * (clip_rect.height / total_height))
            handle_y = scrollbar_y + (scroll_offset / total_height) * scrollbar_height
            
            scrollbar_handle = pygame.Rect(scrollbar_x, handle_y, scrollbar_width, handle_height)
            pygame.draw.rect(self.screen, (100, 100, 120), scrollbar_handle, border_radius=5)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle mouse wheel scrolling
            if event.type == pygame.MOUSEWHEEL:
                if self.state == MenuState.ENEMY_INDEX:
                    self.enemy_scroll_velocity -= event.y * 200
                elif self.state == MenuState.ABILITY_INDEX:
                    self.ability_scroll_velocity -= event.y * 200
            
            # Handle mouse drag scrolling
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.drag_start_pos = pygame.mouse.get_pos()
                    self.dragging_scroll = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_scroll = False
            
            elif event.type == pygame.MOUSEMOTION:
                if hasattr(self, 'dragging_scroll') and self.dragging_scroll:
                    current_pos = pygame.mouse.get_pos()
                    if self.state == MenuState.ENEMY_INDEX:
                        delta_y = self.drag_start_pos[1] - current_pos[1]
                        self.enemy_scroll_velocity = delta_y * 5
                    elif self.state == MenuState.ABILITY_INDEX:
                        delta_y = self.drag_start_pos[1] - current_pos[1]
                        self.ability_scroll_velocity = delta_y * 5
                    self.drag_start_pos = current_pos
            
            # Handle settings interactions
            if self.state == MenuState.SETTINGS:
                mouse_pos = pygame.mouse.get_pos()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check slider interactions
                        if hasattr(self, 'slider_rects'):
                            for setting_key, slider_rect in self.slider_rects.items():
                                if slider_rect.collidepoint(mouse_pos):
                                    self.dragging_slider = setting_key
                                    self.update_slider_value(setting_key, mouse_pos[0])
                        
                        # Check toggle interactions
                        if hasattr(self, 'toggle_rects'):
                            for setting_key, toggle_rect in self.toggle_rects.items():
                                if toggle_rect.collidepoint(mouse_pos):
                                    self.settings[setting_key] = not self.settings[setting_key]
                                    self.play_menu_sound('click')
                        
                        # Check dropdown interactions
                        if hasattr(self, 'dropdown_rects'):
                            for setting_key, dropdown_rect in self.dropdown_rects.items():
                                if dropdown_rect.collidepoint(mouse_pos):
                                    self.cycle_dropdown_value(setting_key)
                                    self.play_menu_sound('click')
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_slider and hasattr(self, 'slider_rects'):
                        slider_rect = self.slider_rects[self.dragging_slider]
                        self.update_slider_value(self.dragging_slider, mouse_pos[0])
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dragging_slider = None
            
            if self.state == MenuState.MAIN:
                for i, button in enumerate(self.main_buttons):
                    if button.is_clicked(event, self):
                        if i == 0:  # Start Game
                            return "start_game"
                        elif i == 1:  # Endless Mode
                            return "endless_mode"
                        elif i == 2:  # Settings
                            self.state = MenuState.SETTINGS
                        elif i == 3:  # Enemy Index
                            self.state = MenuState.ENEMY_INDEX
                        elif i == 4:  # Ability Index
                            self.state = MenuState.ABILITY_INDEX
                        elif i == 5:  # Exit
                            return "exit"
            
            elif self.state == MenuState.SETTINGS:
                for i, button in enumerate(self.settings_buttons):
                    if button.is_clicked(event, self):
                        if i == 0:  # Apply
                            self.apply_settings()
                        elif i == 1:  # Reset
                            self.reset_settings()
                        elif i == 2:  # Back
                            self.state = MenuState.MAIN
            
            elif self.state in [MenuState.ENEMY_INDEX, MenuState.ABILITY_INDEX, MenuState.INVENTORY, MenuState.SHOP]:
                if self.back_button.is_clicked(event, self):
                    self.state = MenuState.MAIN
        
        return True
    
    def update_slider_value(self, setting_key, mouse_x):
        """Update slider value based on mouse position"""
        if setting_key in self.slider_rects:
            slider_rect = self.slider_rects[setting_key]
            # Calculate value from mouse position
            relative_x = mouse_x - slider_rect.x
            relative_x = max(0, min(slider_rect.width, relative_x))
            value = relative_x / slider_rect.width
            
            self.settings[setting_key] = value
    
    def cycle_dropdown_value(self, setting_key):
        """Cycle through dropdown values"""
        if setting_key == "particle_quality":
            qualities = ["low", "medium", "high"]
            current_index = qualities.index(self.settings[setting_key])
            self.settings[setting_key] = qualities[(current_index + 1) % len(qualities)]
    
    def apply_settings(self):
        # Apply fullscreen setting
        if self.settings['fullscreen'] and not self.fullscreen:
            # Switch to fullscreen
            self.fullscreen = True
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Get actual screen dimensions
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h
        elif not self.settings['fullscreen'] and self.fullscreen:
            # Switch to windowed mode
            self.fullscreen = False
            self.screen_width = 1280
            self.screen_height = 720
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Apply volume settings
        pygame.mixer.music.set_volume(self.settings['music_volume'])
        # Set individual sound volumes here
        
        # Apply particle quality
        # This would affect the game's particle system
        
        # Apply vsync
        # This would need to be applied when creating the display
    
    def reset_settings(self):
        self.settings = {
            'master_volume': 0.8,
            'music_volume': 0.7,
            'sound_volume': 0.8,
            'fullscreen': False,
            'vsync': True,
            'particle_quality': 'high'
        }
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60) / 1000.0
            
            # Handle events
            result = self.handle_events()
            if result == "start_game":
                return "start_game"
            elif result == "exit":
                return "exit"
            elif result is False:
                return "exit"
            
            # Update
            self.update_background_particles(dt)
            
            # Draw
            self.draw_background()
            
            if self.state == MenuState.MAIN:
                self.draw_main_menu(dt)
            elif self.state == MenuState.SETTINGS:
                self.draw_settings(dt)
            elif self.state == MenuState.ENEMY_INDEX:
                self.draw_enemy_index(dt)
            elif self.state == MenuState.ABILITY_INDEX:
                self.draw_ability_index(dt)
            elif self.state == MenuState.INVENTORY:
                self.draw_inventory_ui(dt)
            elif self.state == MenuState.SHOP:
                self.draw_shop_ui(dt)
            
            pygame.display.flip()
        
        return "exit"
