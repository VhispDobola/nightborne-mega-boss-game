#!/usr/bin/env python3
"""
Test script to verify fullscreen functionality
"""
import pygame
import sys
from main_menu import MainMenu

def test_fullscreen():
    pygame.init()
    
    print("Testing fullscreen functionality...")
    print("1. Menu should start in windowed mode (1280x720)")
    print("2. Press F to toggle fullscreen")
    print("3. Go to Settings and toggle Fullscreen option")
    print("4. Start game and press F to toggle fullscreen")
    print("5. Press ESC to exit")
    
    # Create a dummy game object to pass fullscreen state
    class GameSettings:
        def __init__(self):
            self.fullscreen = False
    
    game_settings = GameSettings()
    
    # Show main menu with game settings
    menu = MainMenu(game_settings)
    result = menu.run()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_fullscreen()
