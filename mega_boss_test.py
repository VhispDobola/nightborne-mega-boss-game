import pygame
import sys
import math
from enemy import Enemy, EnemyType
from asset_loader import asset_loader
from spritesheet_animator import MegaBossAnimator

class MegaBossTest:
    def __init__(self):
        pygame.init()
        
        # Screen setup
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Mega Boss Animation Test")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Load assets
        asset_loader.load_images()
        
        # Create spritesheet animator
        try:
            self.spritesheet_animator = MegaBossAnimator("assets/images/enemies/nightborne_spritesheet.png")
            self.use_spritesheet = True
            print("✓ Spritesheet animator loaded successfully")
        except Exception as e:
            print(f"✗ Failed to load spritesheet: {e}")
            self.use_spritesheet = False
            self.spritesheet_animator = None
        
        # Create mega boss
        self.mega_boss = Enemy([self.screen_width // 2, self.screen_height // 2], EnemyType.MEGA_BOSS)
        self.mega_boss.hp = 1000  # Set high HP for testing
        self.mega_boss.max_hp = 1000
        
        # Animation control
        self.current_state = "normal"
        self.animation_timer = 0
        self.auto_cycle = True
        self.cycle_timer = 0
        self.cycle_interval = 3.0  # Change state every 3 seconds
        
        # Available animations
        self.available_states = ["normal", "dash", "run", "attack", "hurt", "death"]
        
        # Movement control
        self.boss_speed = 200
        self.target_pos = None
        
        # Visual effects
        self.particles = []
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Manual state control
                if event.key == pygame.K_1:
                    self.current_state = "normal"
                    self.auto_cycle = False
                elif event.key == pygame.K_2:
                    self.current_state = "dash"
                    self.auto_cycle = False
                elif event.key == pygame.K_3:
                    self.current_state = "run"
                    self.auto_cycle = False
                elif event.key == pygame.K_4:
                    self.current_state = "attack"
                    self.auto_cycle = False
                elif event.key == pygame.K_5:
                    self.current_state = "hurt"
                    self.auto_cycle = False
                elif event.key == pygame.K_6:
                    self.current_state = "death"
                    self.auto_cycle = False
                
                # Toggle auto-cycle
                elif event.key == pygame.K_SPACE:
                    self.auto_cycle = not self.auto_cycle
                
                # Movement controls
                elif event.key == pygame.K_LEFT:
                    self.target_pos = [self.mega_boss.pos.x - 100, self.mega_boss.pos.y]
                elif event.key == pygame.K_RIGHT:
                    self.target_pos = [self.mega_boss.pos.x + 100, self.mega_boss.pos.y]
                elif event.key == pygame.K_UP:
                    self.target_pos = [self.mega_boss.pos.x, self.mega_boss.pos.y - 100]
                elif event.key == pygame.K_DOWN:
                    self.target_pos = [self.mega_boss.pos.x, self.mega_boss.pos.y + 100]
                
                # Reset position
                elif event.key == pygame.K_r:
                    self.mega_boss.pos = pygame.Vector2(self.screen_width // 2, self.screen_height // 2)
                    self.target_pos = None
                
                # HP controls
                elif event.key == pygame.K_h:
                    self.mega_boss.hp = max(0, self.mega_boss.hp - 100)
                elif event.key == pygame.K_f:
                    self.mega_boss.hp = min(self.mega_boss.max_hp, self.mega_boss.hp + 100)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click - move to mouse position
                    self.target_pos = list(event.pos)
    
    def update(self, dt):
        # Auto-cycle animations
        if self.auto_cycle:
            self.cycle_timer += dt
            if self.cycle_timer >= self.cycle_interval:
                self.cycle_timer = 0
                # Cycle through states
                current_index = self.available_states.index(self.current_state) if self.current_state in self.available_states else 0
                self.current_state = self.available_states[(current_index + 1) % len(self.available_states)]
        
        # Update mega boss state
        self.mega_boss.current_state = self.current_state
        
        # Use spritesheet animator if available
        if self.use_spritesheet and self.spritesheet_animator:
            self.spritesheet_animator.set_animation(self.current_state)
            self.spritesheet_animator.update(dt)
            spritesheet_frame = self.spritesheet_animator.get_current_frame()
            if spritesheet_frame:
                self.mega_boss.image = spritesheet_frame
                self.mega_boss.rect = self.mega_boss.image.get_rect(center=self.mega_boss.pos)
        else:
            # Fallback to static images
            if hasattr(self.mega_boss, 'custom_images') and self.current_state in self.mega_boss.custom_images:
                custom_image = self.mega_boss.custom_images[self.current_state]
                self.mega_boss.image = pygame.transform.scale(custom_image, (self.mega_boss.size, self.mega_boss.size))
        
        # Update movement
        if self.target_pos:
            direction = pygame.Vector2(self.target_pos) - self.mega_boss.pos
            if direction.length() > 5:
                direction = direction.normalize()
                self.mega_boss.pos += direction * self.boss_speed * dt
            else:
                self.target_pos = None
        
        # Update rect
        self.mega_boss.rect.center = self.mega_boss.pos
        
        # Create particles for effects
        if self.current_state == "dash":
            if pygame.time.get_ticks() % 100 < 20:  # Every 100ms
                self.particles.append({
                    'pos': self.mega_boss.pos.copy(),
                    'vel': pygame.Vector2(math.cos(math.radians(pygame.time.get_ticks() * 0.1)) * 50,
                                        math.sin(math.radians(pygame.time.get_ticks() * 0.1)) * 50),
                    'life': 1.0,
                    'color': (255, 0, 255)
                })
        
        # Update particles
        for particle in self.particles[:]:
            particle['pos'] += particle['vel'] * dt
            particle['life'] -= dt
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self):
        self.screen.fill((20, 20, 40))
        
        # Draw grid
        for x in range(0, self.screen_width, 50):
            pygame.draw.line(self.screen, (30, 30, 50), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, 50):
            pygame.draw.line(self.screen, (30, 30, 50), (0, y), (self.screen_width, y), 1)
        
        # Draw particles
        for particle in self.particles:
            alpha = particle['life']
            size = int(5 * alpha)
            if size > 0:
                pygame.draw.circle(self.screen, particle['color'], 
                                 (int(particle['pos'].x), int(particle['pos'].y)), size)
        
        # Draw mega boss
        self.mega_boss.draw(self.screen)
        
        # Draw health bar
        bar_width = 200
        bar_height = 20
        bar_x = self.screen_width // 2 - bar_width // 2
        bar_y = 50
        
        pygame.draw.rect(self.screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        hp_percentage = self.mega_boss.hp / self.mega_boss.max_hp
        pygame.draw.rect(self.screen, (200, 0, 0), (bar_x, bar_y, int(bar_width * hp_percentage), bar_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        # Title
        title_text = self.font.render("Mega Boss Animation Test", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 10))
        
        # Current state
        state_text = self.font.render(f"State: {self.current_state.upper()}", True, (255, 255, 0))
        self.screen.blit(state_text, (50, 100))
        
        # Auto-cycle status
        cycle_text = self.small_font.render(f"Auto-cycle: {'ON' if self.auto_cycle else 'OFF'} (SPACE to toggle)", 
                                          True, (0, 255, 0) if self.auto_cycle else (255, 100, 100))
        self.screen.blit(cycle_text, (50, 140))
        
        # Controls
        controls = [
            "CONTROLS:",
            "1-6: Manual state selection",
            "SPACE: Toggle auto-cycle",
            "Arrow Keys: Move boss",
            "Click: Move to position",
            "R: Reset position",
            "H: Decrease HP",
            "F: Increase HP",
            "ESC: Exit"
        ]
        
        y_offset = 200
        for control in controls:
            control_text = self.small_font.render(control, True, (200, 200, 200))
            self.screen.blit(control_text, (50, y_offset))
            y_offset += 25
        
        # Asset info
        asset_info = [
            "ASSET STATUS:",
            f"Spritesheet: {'✓' if self.use_spritesheet else '✗'}",
            "",
            "STATIC IMAGES:",
            f"Normal: {'✓' if 'mega_boss_normal' in self.mega_boss.custom_images else '✗'}",
            f"Dash: {'✓' if 'mega_boss_dash' in self.mega_boss.custom_images else '✗'}",
            f"Attack: {'✓' if 'mega_boss_attack' in self.mega_boss.custom_images else '✗'}",
            f"Hurt: {'✓' if 'mega_boss_hurt' in self.mega_boss.custom_images else '✗'}",
            f"Death: {'✓' if 'mega_boss_death' in self.mega_boss.custom_images else '✗'}",
        ]
        
        y_offset = 200
        for info in asset_info:
            info_text = self.small_font.render(info, True, (200, 200, 200))
            self.screen.blit(info_text, (self.screen_width - 250, y_offset))
            y_offset += 25
        
        # HP info
        hp_text = self.small_font.render(f"HP: {self.mega_boss.hp}/{self.mega_boss.max_hp}", True, (255, 100, 100))
        self.screen.blit(hp_text, (self.screen_width // 2 - hp_text.get_width() // 2, 80))
    
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    test = MegaBossTest()
    test.run()
