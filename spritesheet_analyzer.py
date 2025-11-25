import pygame
import sys

def analyze_spritesheet(spritesheet_path):
    """Analyze spritesheet without display"""
    try:
        # Initialize just the image system
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display
        
        image = pygame.image.load(spritesheet_path).convert_alpha()
        width = image.get_width()
        height = image.get_height()
        
        print(f"📊 Spritesheet Analysis: {spritesheet_path}")
        print(f"📏 Dimensions: {width} x {height}")
        print()
        
        # Try common frame sizes
        common_sizes = [16, 24, 32, 48, 64, 96, 128, 256]
        
        valid_sizes = []
        for frame_size in common_sizes:
            if width % frame_size == 0 and height % frame_size == 0:
                cols = width // frame_size
                rows = height // frame_size
                total_frames = cols * rows
                valid_sizes.append((frame_size, cols, rows, total_frames))
        
        if valid_sizes:
            print("✅ Valid Frame Sizes:")
            for frame_size, cols, rows, total_frames in valid_sizes:
                print(f"   {frame_size}x{frame_size}: {cols} cols x {rows} rows = {total_frames} frames")
                
                # Show possible animation splits
                print(f"   Possible animations:")
                if rows >= 5:
                    frames_per_anim = total_frames // 5
                    print(f"     • 5 animations: {frames_per_anim} frames each")
                if rows >= 4:
                    frames_per_anim = total_frames // 4
                    print(f"     • 4 animations: {frames_per_anim} frames each")
                if rows >= 3:
                    frames_per_anim = total_frames // 3
                    print(f"     • 3 animations: {frames_per_anim} frames each")
                print()
        else:
            print("❌ No standard frame sizes found. Spritesheet might be irregular.")
            print(f"   Width divisors: {[d for d in range(16, 257) if width % d == 0]}")
            print(f"   Height divisors: {[d for d in range(16, 257) if height % d == 0]}")
        
        pygame.quit()
        
        # Ask for frame information
        print("\n🔧 To fix the animation, please tell me:")
        print("1. What frame size works best? (e.g., 64x64)")
        print("2. How many frames per animation?")
        print("3. How are animations arranged? (rows or columns)")
        
    except Exception as e:
        print(f"❌ Error analyzing spritesheet: {e}")

if __name__ == "__main__":
    spritesheet_path = "assets/images/enemies/nightborne_spritesheet.png"
    analyze_spritesheet(spritesheet_path)
