#!/usr/bin/env python3
"""
Test script to verify level up upgrade selection works correctly
"""
import pygame
import sys
from game import Game

def test_level_up_fix():
    pygame.init()
    
    print("Testing level up upgrade selection fix...")
    print("1. Start the game")
    print("2. Collect XP orbs or complete waves")
    print("3. When you level up, the game should pause and show upgrade options")
    print("4. After selecting an upgrade, the game should resume")
    print("5. This should work for both XP orb collection and wave completion")
    print("\nPress ESC to exit the test")
    
    game = Game()
    game.run()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_level_up_fix()
