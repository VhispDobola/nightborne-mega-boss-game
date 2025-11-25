import pygame
import os
from typing import Dict, Optional, List

class AssetLoader:
    """Centralized asset loading and management system"""
    
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.loaded = False
        
    def load_images(self, base_path: str = "assets/images"):
        """Load all images from the assets directory"""
        if self.loaded:
            return
            
        # Load enemy images
        enemy_path = os.path.join(base_path, "enemies")
        if os.path.exists(enemy_path):
            for filename in os.listdir(enemy_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    name = os.path.splitext(filename)[0].lower()
                    try:
                        image_path = os.path.join(enemy_path, filename)
                        
                        # Handle GIF animations
                        if filename.lower().endswith('.gif'):
                            # Try to load as animated GIF
                            frames = self.load_gif_frames(image_path)
                            if len(frames) > 1:
                                # It's an animated GIF
                                self.animations[name] = frames
                                # Use first frame as default image
                                self.images[name] = frames[0]
                                print(f"Loaded animated GIF: {name} ({len(frames)} frames)")
                            else:
                                # Single frame GIF
                                self.images[name] = frames[0]
                                print(f"Loaded GIF image: {name}")
                        else:
                            # Regular image
                            image = pygame.image.load(image_path).convert_alpha()
                            self.images[name] = image
                            print(f"Loaded enemy image: {name}")
                    except Exception as e:
                        print(f"Failed to load {filename}: {e}")
        
        self.loaded = True
    
    def load_gif_frames(self, gif_path: str) -> List[pygame.Surface]:
        """Load all frames from a GIF file"""
        frames = []
        try:
            # For now, we'll load GIF as a single image
            # Full GIF animation support would require additional libraries
            gif_surface = pygame.image.load(gif_path).convert_alpha()
            frames.append(gif_surface)
        except Exception as e:
            print(f"Error loading GIF {gif_path}: {e}")
            # Create a placeholder surface
            placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255, 128))  # Semi-transparent magenta
            frames.append(placeholder)
        
        return frames
    
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Get a loaded image by name"""
        return self.images.get(name)
    
    def has_image(self, name: str) -> bool:
        """Check if an image is loaded"""
        return name in self.images
    
    def scale_image(self, image: pygame.Surface, size: tuple) -> pygame.Surface:
        """Scale an image to the specified size"""
        return pygame.transform.scale(image, size)
    
    def rotate_image(self, image: pygame.Surface, angle: float) -> pygame.Surface:
        """Rotate an image by the specified angle"""
        return pygame.transform.rotate(image, angle)

# Global asset loader instance
asset_loader = AssetLoader()
