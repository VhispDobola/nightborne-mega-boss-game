import pygame
from typing import List, Tuple, Optional

class SpriteSheet:
    """Handles spritesheet animations"""
    
    def __init__(self, image_path: str, frame_width: int, frame_height: int, 
                 frames_per_row: int = None, scale: float = 1.0):
        """
        Initialize spritesheet
        
        Args:
            image_path: Path to spritesheet image
            frame_width: Width of each frame
            frame_height: Height of each frame
            frames_per_row: Number of frames per row (auto-calculated if None)
            scale: Scale factor for frames
        """
        self.image = pygame.image.load(image_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale = scale
        
        # Calculate frames per row if not provided
        if frames_per_row is None:
            frames_per_row = self.image.get_width() // frame_width
        
        self.frames_per_row = frames_per_row
        self.total_frames = (self.image.get_width() // frame_width) * (self.image.get_height() // frame_height)
        
        # Extract frames
        self.frames = self.extract_frames()
    
    def extract_frames(self) -> List[pygame.Surface]:
        """Extract all frames from the spritesheet"""
        frames = []
        
        for row in range(self.image.get_height() // self.frame_height):
            for col in range(self.frames_per_row):
                frame_index = row * self.frames_per_row + col
                if frame_index >= self.total_frames:
                    break
                
                # Calculate frame position
                x = col * self.frame_width
                y = row * self.frame_height
                
                # Extract frame
                frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                frame.blit(self.image, (0, 0), (x, y, self.frame_width, self.frame_height))
                
                # Scale frame if needed
                if self.scale != 1.0:
                    new_width = int(self.frame_width * self.scale)
                    new_height = int(self.frame_height * self.scale)
                    frame = pygame.transform.scale(frame, (new_width, new_height))
                
                frames.append(frame)
        
        return frames
    
    def get_frame(self, index: int) -> pygame.Surface:
        """Get a specific frame by index"""
        if 0 <= index < len(self.frames):
            return self.frames[index]
        return self.frames[0] if self.frames else None
    
    def get_all_frames(self) -> List[pygame.Surface]:
        """Get all frames"""
        return self.frames

class Animation:
    """Handles playing animations from sprite frames"""
    
    def __init__(self, frames: List[pygame.Surface], frame_duration: float = 0.1, 
                 loop: bool = True):
        """
        Initialize animation
        
        Args:
            frames: List of animation frames
            frame_duration: Duration of each frame in seconds
            loop: Whether to loop the animation
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.timer = 0
        self.playing = True
        self.finished = False
    
    def update(self, dt: float):
        """Update animation"""
        if not self.playing or not self.frames:
            return
        
        self.timer += dt
        
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
                    self.playing = False
    
    def get_current_frame(self) -> pygame.Surface:
        """Get current animation frame"""
        if self.frames:
            return self.frames[self.current_frame]
        return None
    
    def reset(self):
        """Reset animation to first frame"""
        self.current_frame = 0
        self.timer = 0
        self.playing = True
        self.finished = False
    
    def is_finished(self) -> bool:
        """Check if animation has finished"""
        return self.finished
    
    def set_frame(self, frame_index: int):
        """Set current frame manually"""
        if 0 <= frame_index < len(self.frames):
            self.current_frame = frame_index

class MegaBossAnimator:
    """Specialized animator for mega boss using spritesheets"""
    
    def __init__(self, spritesheet_path: str):
        """Initialize mega boss animator"""
        # Based on analysis: 1840x400 spritesheet
        # Trying 80x80 frames horizontally (23 frames total)
        self.spritesheet = SpriteSheet(spritesheet_path, frame_width=80, frame_height=80, scale=2.0)
        
        # Get all frames
        all_frames = self.spritesheet.get_all_frames()
        print(f"Total frames extracted: {len(all_frames)}")
        
        # Create animations based on user-identified exact frame ranges
        frame_ranges = {
            'normal': (0, 9),      # Frames 0-8: idle
            'dash': (5, 11),       # Frames 5-10: dash (overlaps with normal slightly)
            'run': (23, 29),       # Frames 23-28: run animation
            'attack': (45, 58),    # Frames 45-57: attack
            'hurt': (68, 74),      # Frames 68-73: hurt (exact)
            'death': (91, 115)     # Frames 91-114: death (exact)
        }
        
        self.animations = {}
        for anim_name, (start, end) in frame_ranges.items():
            frames = all_frames[start:end] if start < len(all_frames) and end <= len(all_frames) else []
            if frames:
                loop = anim_name in ['normal', 'dash', 'run']  # Loop idle, dash, and run animations
                frame_duration = 0.15 if anim_name == 'normal' else 0.12 if anim_name in ['dash', 'run'] else 0.1
                self.animations[anim_name] = Animation(frames, frame_duration, loop)
                print(f"✓ {anim_name}: {len(frames)} frames {'(looping)' if loop else '(one-time)'}")
            else:
                print(f"✗ {anim_name}: No frames found")
        
        self.current_animation = 'normal'
        self.current_anim = self.animations.get(self.current_animation, list(self.animations.values())[0])
    
    def set_animation(self, animation_name: str):
        """Set current animation"""
        if animation_name in self.animations and animation_name != self.current_animation:
            self.current_animation = animation_name
            self.current_anim = self.animations[animation_name]
            self.current_anim.reset()
    
    def update(self, dt: float):
        """Update current animation"""
        self.current_anim.update(dt)
    
    def get_current_frame(self) -> pygame.Surface:
        """Get current animation frame"""
        return self.current_anim.get_current_frame()
    
    def is_animation_finished(self) -> bool:
        """Check if current animation is finished"""
        return self.current_anim.is_finished()
