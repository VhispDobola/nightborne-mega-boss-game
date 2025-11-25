import pygame

class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.large_font = pygame.font.Font(None, 32)
        
        # UI colors
        self.hp_bar_color = (200, 50, 50)
        self.hp_bg_color = (50, 50, 50)
        self.xp_bar_color = (50, 200, 50)
        self.xp_bg_color = (30, 30, 30)
        self.text_color = (255, 255, 255)
        
        # UI positions (will be updated in draw to match screen size)
        self.hp_bar_pos = (20, 20)
        self.hp_bar_size = (300, 25)
        self.xp_bar_pos = (20, 680)
        self.xp_bar_size = (400, 20)
        
    def draw(self):
        """Draw all UI elements"""
        self.draw_hp_bar()
        self.draw_xp_bar()
        self.draw_stats()
        self.draw_timer()
        self.draw_combo()
        self.draw_wave_info()
        
    def draw_hp_bar(self):
        """Draw HP bar at top-left"""
        # Update position based on screen size
        x, y = 20, 20
        width, height = 300, 25
        
        # Draw background
        pygame.draw.rect(self.game.screen, self.hp_bg_color, (x, y, width, height))
        pygame.draw.rect(self.game.screen, (100, 100, 100), (x, y, width, height), 2)
        
        # Draw HP fill
        player = self.game.player
        hp_percentage = player.hp / player.max_hp
        hp_width = int(width * hp_percentage)
        
        # Change color based on HP percentage
        if hp_percentage > 0.6:
            color = (50, 200, 50)
        elif hp_percentage > 0.3:
            color = (200, 200, 50)
        else:
            color = (200, 50, 50)
            
        pygame.draw.rect(self.game.screen, color, (x, y, hp_width, height))
        
        # Draw HP text
        hp_text = f"HP: {int(player.hp)}/{int(player.max_hp)}"
        text_surface = self.font.render(hp_text, True, self.text_color)
        self.game.screen.blit(text_surface, (x + 5, y + 3))
        
    def draw_xp_bar(self):
        """Draw XP bar at bottom"""
        # Update position based on screen size
        x, y = 20, self.game.screen_height - 50
        width, height = 400, 20
        
        # Draw background
        pygame.draw.rect(self.game.screen, self.xp_bg_color, (x, y, width, height))
        pygame.draw.rect(self.game.screen, (80, 80, 80), (x, y, width, height), 2)
        
        # Draw XP fill
        player = self.game.player
        xp_percentage = player.xp / player.xp_to_next_level
        xp_width = int(width * xp_percentage)
        
        pygame.draw.rect(self.game.screen, self.xp_bar_color, (x, y, xp_width, height))
        
        # Draw XP text
        xp_text = f"Level {player.level} - XP: {int(player.xp)}/{int(player.xp_to_next_level)}"
        text_surface = self.font.render(xp_text, True, self.text_color)
        self.game.screen.blit(text_surface, (x + 5, y + 2))
        
    def draw_stats(self):
        """Draw player stats in top-right"""
        player = self.game.player
        x = self.game.screen_width - 250
        y = 20
        line_height = 25
        
        stats = [
            f"Damage: {player.damage}",
            f"Fire Rate: {player.weapon.fire_rate:.1f}/s",
            f"Speed: {player.speed}",
            f"Projectiles: {player.weapon.projectile_count}",
            f"Pickup: {player.pickup_range}",
            f"Weapon: {player.weapon.weapon_type.value.title()}",
            f"Weapon Level: {getattr(player, 'weapon_level', 1)}"
        ]
        
        # Draw semi-transparent background
        bg_rect = pygame.Rect(x - 10, y - 10, 240, len(stats) * line_height + 20)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        self.game.screen.blit(bg_surface, bg_rect)
        
        # Draw border
        pygame.draw.rect(self.game.screen, (100, 100, 100), bg_rect, 2)
        
        # Draw stats text
        for i, stat in enumerate(stats):
            text_surface = self.small_font.render(stat, True, self.text_color)
            self.game.screen.blit(text_surface, (x, y + i * line_height))
            
    def draw_timer(self):
        """Draw game timer and survival info"""
        # Draw time survived
        time_survived = int(self.game.game_time)
        minutes = time_survived // 60
        seconds = time_survived % 60
        time_text = f"Time: {minutes:02d}:{seconds:02d}"
        
        # Draw target time
        target_time = int(self.game.survival_time)
        target_minutes = target_time // 60
        target_seconds = target_time % 60
        target_text = f"Target: {target_minutes:02d}:{target_seconds:02d}"
        
        # Position at top-center
        x = 640
        y = 20
        
        # Draw time text
        time_surface = self.large_font.render(time_text, True, self.text_color)
        time_rect = time_surface.get_rect(center=(x, y))
        self.game.screen.blit(time_surface, time_rect)
        
        # Draw target text
        target_surface = self.small_font.render(target_text, True, (150, 150, 150))
        target_rect = target_surface.get_rect(center=(x, y + 30))
        self.game.screen.blit(target_surface, target_rect)
        
        # Draw progress bar towards victory
        progress = min(time_survived / target_time, 1.0)
        bar_width = 200
        bar_height = 8
        bar_x = x - bar_width // 2
        bar_y = y + 45
        
        # Background
        pygame.draw.rect(self.game.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        # Progress
        pygame.draw.rect(self.game.screen, (100, 150, 200), (bar_x, bar_y, int(bar_width * progress), bar_height))
        # Border
        pygame.draw.rect(self.game.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)
        
    def draw_combo(self):
        """Draw combo counter"""
        if self.game.combo_count > 1:
            # Combo text
            combo_text = f"COMBO x{self.game.combo_count}"
            
            # Color based on combo level
            if self.game.combo_count < 5:
                color = (255, 255, 0)
            elif self.game.combo_count < 10:
                color = (255, 200, 0)
            elif self.game.combo_count < 20:
                color = (255, 100, 255)
            else:
                color = (255, 0, 255)
            
            # Draw combo text
            font = pygame.font.Font(None, 32)
            text_surface = font.render(combo_text, True, color)
            text_rect = text_surface.get_rect(center=(640, 100))
            
            # Draw background
            bg_rect = text_rect.inflate(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 150))
            self.game.screen.blit(bg_surface, bg_rect)
            
            # Draw text
            self.game.screen.blit(text_surface, text_rect)
            
            # Draw combo timer bar
            if self.game.combo_timer > 0:
                bar_width = 100
                bar_height = 4
                bar_x = 640 - bar_width // 2
                bar_y = text_rect.bottom + 5
                
                # Background
                pygame.draw.rect(self.game.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                
                # Timer fill
                timer_percentage = self.game.combo_timer / 2.0  # 2 seconds max
                fill_width = int(bar_width * timer_percentage)
                pygame.draw.rect(self.game.screen, color, (bar_x, bar_y, fill_width, bar_height))
    
    def draw_wave_info(self):
        """Draw wave information"""
        wave_info = self.game.wave_manager.get_wave_info()
        
        # Position at top center
        x = self.game.screen_width // 2
        y = 60
        
        # Draw wave info
        font = pygame.font.Font(None, 28)
        text_surface = font.render(wave_info, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x, y))
        
        # Draw background
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        self.game.screen.blit(bg_surface, bg_rect)
        
        # Draw text
        self.game.screen.blit(text_surface, text_rect)
        
        # Draw wave indicator for boss waves
        if self.game.wave_manager.is_boss_wave():
            boss_text = "⚠ BOSS WAVE ⚠"
            boss_color = (255, 0, 0)
            boss_font = pygame.font.Font(None, 24)
            boss_surface = boss_font.render(boss_text, True, boss_color)
            boss_rect = boss_surface.get_rect(center=(x, y + 25))
            self.game.screen.blit(boss_surface, boss_rect)

class DamageNumber:
    """Floating damage number for visual feedback"""
    def __init__(self, pos, damage, color=(255, 255, 0)):
        self.pos = pygame.Vector2(pos)
        self.damage = damage
        self.color = color
        self.lifetime = 1.0
        self.age = 0
        self.vel = pygame.Vector2(0, -50)  # Float upward
        
    def update(self, dt):
        self.age += dt
        self.pos += self.vel * dt
        return self.age < self.lifetime
        
    def draw(self, screen, font):
        alpha = 1.0 - (self.age / self.lifetime)
        color = (*self.color, int(255 * alpha))
        
        text = font.render(str(int(self.damage)), True, self.color)
        text_rect = text.get_rect(center=self.pos)
        screen.blit(text, text_rect)

class DamageNumberManager:
    """Manages floating damage numbers"""
    def __init__(self):
        self.damage_numbers = []
        self.font = pygame.font.Font(None, 20)
        
    def add_damage_number(self, pos, damage, color=(255, 255, 0)):
        """Add a new damage number"""
        self.damage_numbers.append(DamageNumber(pos, damage, color))
        
    def update(self, dt):
        """Update all damage numbers"""
        self.damage_numbers = [dn for dn in self.damage_numbers if dn.update(dt)]
        
    def draw(self, screen):
        """Draw all damage numbers"""
        for damage_number in self.damage_numbers:
            damage_number.draw(screen, self.font)
