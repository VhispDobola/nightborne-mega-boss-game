import pygame
import sys
from game import Game
from main_menu import MainMenu

def main():
    pygame.init()
    
    # Create a dummy game object to pass fullscreen state
    class GameSettings:
        def __init__(self):
            self.fullscreen = False
    
    game_settings = GameSettings()
    
    while True:
        # Show main menu with game settings
        menu = MainMenu(game_settings)
        result = menu.run()
        
        # Update game settings from menu
        game_settings.fullscreen = menu.fullscreen
        
        if result == "start_game":
            # Start the game with current settings
            game = Game()
            game.fullscreen = menu.fullscreen
            game.endless_mode = False
            if game.fullscreen:
                game.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                info = pygame.display.Info()
                game.screen_width = info.current_w
                game.screen_height = info.current_h
            else:
                game.screen_width = 1280
                game.screen_height = 720
                game.screen = pygame.display.set_mode((game.screen_width, game.screen_height))
            game.run()
        elif result == "endless_mode":
            # Start endless mode with current settings
            game = Game()
            game.fullscreen = menu.fullscreen
            game.endless_mode = True
            if game.fullscreen:
                game.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                info = pygame.display.Info()
                game.screen_width = info.current_w
                game.screen_height = info.current_h
            else:
                game.screen_width = 1280
                game.screen_height = 720
                game.screen = pygame.display.set_mode((game.screen_width, game.screen_height))
            game.run()
        elif result == "exit":
            # Exit the application
            pygame.quit()
            sys.exit()
        else:
            # Unexpected result, exit
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()