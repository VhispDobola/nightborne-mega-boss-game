import pygame
import sys
from spritesheet_animator import SpriteSheet

class FrameInspector:
    """Visual tool to inspect spritesheet frames"""
    
    def __init__(self, spritesheet_path):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Frame Inspector - Find Your Animations")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        
        # Load spritesheet
        self.spritesheet = SpriteSheet(spritesheet_path, frame_width=80, frame_height=80, scale=1.5)
        self.all_frames = self.spritesheet.get_all_frames()
        
        # Navigation
        self.current_frame = 0
        self.frames_per_row = 10
        self.show_grid = True
        self.scroll_y = 0
        total_rows = (len(self.all_frames) + self.frames_per_row - 1) // self.frames_per_row
        visible_rows = 6
        self.max_scroll = max(0, (total_rows - visible_rows) * 100)
        print(f"Total frames: {len(self.all_frames)}, Total rows: {total_rows}, Max scroll: {self.max_scroll}")
        
        # Animation markers
        self.markers = {
            'normal_start': 0,
            'normal_end': 5,
            'dash_start': 6,
            'dash_end': 11,
            'attack_start': 20,
            'attack_end': 25,
            'hurt_start': 30,
            'hurt_end': 33,
            'death_start': 40,
            'death_end': 42
        }
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEWHEEL:
                # Mouse wheel scrolling
                scroll_amount = event.y * 50  # Adjust scroll speed
                self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - scroll_amount))
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # Navigation
                elif event.key == pygame.K_LEFT:
                    self.current_frame = max(0, self.current_frame - 1)
                elif event.key == pygame.K_RIGHT:
                    self.current_frame = min(len(self.all_frames) - 1, self.current_frame + 1)
                elif event.key == pygame.K_UP:
                    self.current_frame = max(0, self.current_frame - self.frames_per_row)
                elif event.key == pygame.K_DOWN:
                    self.current_frame = min(len(self.all_frames) - 1, self.current_frame + self.frames_per_row)
                
                # Scrolling
                elif event.key == pygame.K_PAGEUP:
                    self.scroll_y = max(0, self.scroll_y - 200)
                elif event.key == pygame.K_PAGEDOWN:
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 200)
                elif event.key == pygame.K_HOME:
                    self.scroll_y = 0
                elif event.key == pygame.K_END:
                    self.scroll_y = self.max_scroll
                
                # Toggle grid
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                
                # Quick jump to animation starts
                elif event.key == pygame.K_1:
                    self.current_frame = self.markers['normal_start']
                elif event.key == pygame.K_2:
                    self.current_frame = self.markers['dash_start']
                elif event.key == pygame.K_3:
                    self.current_frame = self.markers['attack_start']
                elif event.key == pygame.K_4:
                    self.current_frame = self.markers['hurt_start']
                elif event.key == pygame.K_5:
                    self.current_frame = self.markers['death_start']
                
                # Mark animation boundaries
                elif event.key == pygame.K_n:  # Mark normal start
                    self.markers['normal_start'] = self.current_frame
                elif event.key == pygame.K_d:  # Mark dash start
                    self.markers['dash_start'] = self.current_frame
                elif event.key == pygame.K_a:  # Mark attack start
                    self.markers['attack_start'] = self.current_frame
                elif event.key == pygame.K_h:  # Mark hurt start
                    self.markers['hurt_start'] = self.current_frame
                elif event.key == pygame.K_e:  # Mark death start
                    self.markers['death_start'] = self.current_frame
                
                # Print current markers
                elif event.key == pygame.K_p:
                    self.print_markers()
        
        return True
    
    def print_markers(self):
        print("\n🎯 CURRENT ANIMATION MARKERS:")
        print(f"Normal: frames {self.markers['normal_start']}-{self.markers['normal_end']}")
        print(f"Dash: frames {self.markers['dash_start']}-{self.markers['dash_end']}")
        print(f"Attack: frames {self.markers['attack_start']}-{self.markers['attack_end']}")
        print(f"Hurt: frames {self.markers['hurt_start']}-{self.markers['hurt_end']}")
        print(f"Death: frames {self.markers['death_start']}-{self.markers['death_end']}")
        print("\nCopy this configuration:")
        print("frame_ranges = {")
        print(f"    'normal': ({self.markers['normal_start']}, {self.markers['normal_end'] + 1}),")
        print(f"    'dash': ({self.markers['dash_start']}, {self.markers['dash_end'] + 1}),")
        print(f"    'attack': ({self.markers['attack_start']}, {self.markers['attack_end'] + 1}),")
        print(f"    'hurt': ({self.markers['hurt_start']}, {self.markers['hurt_end'] + 1}),")
        print(f"    'death': ({self.markers['death_start']}, {self.markers['death_end'] + 1})")
        print("}")
    
    def draw(self):
        self.screen.fill((30, 30, 50))
        
        # Title
        title = self.title_font.render("Frame Inspector - Find Your Animation Frames", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 20))
        
        # Draw frame grid
        start_y = 80
        visible_rows = 6  # Show 6 rows at a time
        
        for i, frame in enumerate(self.all_frames):
            row = i // self.frames_per_row
            col = i % self.frames_per_row
            x = 50 + col * 100
            y = start_y + row * 100 - self.scroll_y
            
            # Skip frames that are outside visible area
            if y < start_y - 100 or y > start_y + visible_rows * 100:
                continue
            
            # Highlight current frame
            if i == self.current_frame:
                pygame.draw.rect(self.screen, (255, 255, 0), (x - 5, y - 5, 90, 90), 3)
            
            # Highlight animation ranges
            color = (100, 100, 100)
            if self.markers['normal_start'] <= i <= self.markers['normal_end']:
                color = (0, 255, 0)  # Green for normal
            elif self.markers['dash_start'] <= i <= self.markers['dash_end']:
                color = (0, 255, 255)  # Cyan for dash
            elif self.markers['attack_start'] <= i <= self.markers['attack_end']:
                color = (255, 0, 0)  # Red for attack
            elif self.markers['hurt_start'] <= i <= self.markers['hurt_end']:
                color = (255, 255, 0)  # Yellow for hurt
            elif self.markers['death_start'] <= i <= self.markers['death_end']:
                color = (128, 0, 128)  # Purple for death
            
            if self.show_grid or i == self.current_frame:
                pygame.draw.rect(self.screen, color, (x - 2, y - 2, 84, 84), 1)
            
            # Draw frame
            self.screen.blit(frame, (x, y))
            
            # Frame number
            frame_text = self.font.render(str(i), True, (255, 255, 255))
            self.screen.blit(frame_text, (x + 35, y + 70))
        
        # Scroll indicator and scrollbar
        if self.max_scroll > 0:
            # Scroll text
            scroll_text = self.font.render(f"Scroll: {self.scroll_y // 100}/{self.max_scroll // 100}", True, (200, 200, 200))
            self.screen.blit(scroll_text, (50, 60))
            
            # Draw scrollbar
            scrollbar_x = 1080
            scrollbar_y = 80
            scrollbar_height = 600
            scrollbar_width = 20
            
            # Background
            pygame.draw.rect(self.screen, (60, 60, 60), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
            
            # Scroll thumb
            if self.max_scroll > 0:
                thumb_height = max(20, scrollbar_height * (scrollbar_height / (scrollbar_height + self.max_scroll)))
                thumb_y = scrollbar_y + (self.scroll_y / self.max_scroll) * (scrollbar_height - thumb_height)
                pygame.draw.rect(self.screen, (150, 150, 150), (scrollbar_x, thumb_y, scrollbar_width, thumb_height))
            
            # Labels
            scroll_help = self.font.render("Use mouse wheel or Page Up/Down", True, (150, 150, 150))
            self.screen.blit(scroll_help, (scrollbar_x - 100, scrollbar_y + scrollbar_height + 10))
        
        # Current frame info
        info_y = 650
        current_frame = self.all_frames[self.current_frame]
        self.screen.blit(current_frame, (50, info_y))
        
        info_texts = [
            f"Current Frame: {self.current_frame}",
            f"Total Frames: {len(self.all_frames)}",
            f"Scroll: {self.scroll_y // 100} rows down",
            "",
            "CONTROLS:",
            "Arrow Keys: Navigate frames",
            "Page Up/Down: Scroll view",
            "Home/End: Jump to top/bottom",
            "1-5: Jump to animation starts",
            "N/D/A/H/E: Mark animation starts",
            "G: Toggle grid",
            "P: Print configuration",
            "ESC: Exit"
        ]
        
        x_offset = 300
        for i, text in enumerate(info_texts):
            text_surface = self.font.render(text, True, (200, 200, 200))
            self.screen.blit(text_surface, (x_offset, info_y + i * 25))
        
        # Legend
        legend_x = 800
        legend_items = [
            ("Normal", (0, 255, 0)),
            ("Dash", (0, 255, 255)),
            ("Attack", (255, 0, 0)),
            ("Hurt", (255, 255, 0)),
            ("Death", (128, 0, 128))
        ]
        
        legend_text = self.font.render("ANIMATION COLORS:", True, (255, 255, 255))
        self.screen.blit(legend_text, (legend_x, info_y))
        
        for i, (name, color) in enumerate(legend_items):
            pygame.draw.rect(self.screen, color, (legend_x, info_y + 30 + i * 25, 20, 20))
            text_surface = self.font.render(name, True, (200, 200, 200))
            self.screen.blit(text_surface, (legend_x + 30, info_y + 30 + i * 25))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    inspector = FrameInspector("assets/images/enemies/nightborne_spritesheet.png")
    inspector.run()
