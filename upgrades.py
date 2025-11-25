import pygame
import random
from projectile import ProjectileType, Weapon

class Upgrade:
    """Base class for upgrades"""
    def __init__(self, title, description, apply_func):
        self.title = title
        self.description = description
        self.apply_func = apply_func
    
    def apply(self, player):
        """Apply this upgrade to the player"""
        self.apply_func(player)

class UpgradeManager:
    def __init__(self, game):
        self.game = game
        self.waiting = False
        self.options = []
        self.selected_upgrade = None
        
        # Define all possible upgrades
        self.all_upgrades = self.create_upgrades()
        
    def create_upgrades(self):
        """Create all available upgrades"""
        upgrades = [
            # Damage upgrades
            Upgrade("Damage +5", "Increase projectile damage by 5", 
                   lambda p: setattr(p, 'damage', p.damage + 5)),
            Upgrade("Damage +10", "Increase projectile damage by 10", 
                   lambda p: setattr(p, 'damage', p.damage + 10)),
            Upgrade("Damage +20%", "Increase projectile damage by 20%", 
                   lambda p: setattr(p, 'damage', int(p.damage * 1.2))),
            
            # Fire rate upgrades
            Upgrade("Fire Rate +0.5", "Increase fire rate by 0.5 shots/sec", 
                   lambda p: setattr(p, 'fire_rate', p.fire_rate + 0.5)),
            Upgrade("Fire Rate +100%", "Double your fire rate", 
                   lambda p: setattr(p, 'fire_rate', p.fire_rate * 2)),
            
            # Movement upgrades
            Upgrade("Move Speed +30", "Increase movement speed by 30", 
                   lambda p: setattr(p, 'speed', p.speed + 30)),
            Upgrade("Move Speed +20%", "Increase movement speed by 20%", 
                   lambda p: setattr(p, 'speed', int(p.speed * 1.2))),
            
            # Projectile upgrades
            Upgrade("+1 Projectile", "Fire one additional projectile", 
                   lambda p: setattr(p.weapon, 'projectile_count', p.weapon.projectile_count + 1)),
            Upgrade("+2 Projectiles", "Fire two additional projectiles", 
                   lambda p: setattr(p.weapon, 'projectile_count', p.weapon.projectile_count + 2)),
            
            # Projectile speed
            Upgrade("Projectile Speed +100", "Increase projectile speed by 100", 
                   lambda p: setattr(p, 'projectile_speed', p.projectile_speed + 100)),
            
            # Pickup range
            Upgrade("Pickup Range +20", "Increase XP pickup range by 20", 
                   lambda p: setattr(p, 'pickup_range', p.pickup_range + 20)),
            Upgrade("Pickup Range +50%", "Increase XP pickup range by 50%", 
                   lambda p: setattr(p, 'pickup_range', int(p.pickup_range * 1.5))),
            
            # Health upgrades
            Upgrade("Heal 50", "Restore 50 HP", 
                   lambda p: p.heal(50)),
            Upgrade("Heal Full", "Restore full health", 
                   lambda p: p.heal(p.max_hp)),
            Upgrade("Max HP +20", "Increase maximum HP by 20", 
                   lambda p: self.increase_max_hp(p, 20)),
            Upgrade("Max HP +50", "Increase maximum HP by 50", 
                   lambda p: self.increase_max_hp(p, 50)),
            
            # Weapon type upgrades
            Upgrade("Spread Shot", "Fire 3 projectiles in spread pattern", 
                   lambda p: self.change_weapon(p, ProjectileType.SPREAD)),
            Upgrade("Change to Bouncing", "Bouncing projectiles", 
                   lambda p: self.change_weapon(p, ProjectileType.BOUNCING)),
            Upgrade("Change to Homing", "Homing projectiles", 
                   lambda p: self.change_weapon(p, ProjectileType.HOMING)),
            Upgrade("Change to Laser", "Omnidirectional laser projectiles", 
                   lambda p: self.change_weapon(p, ProjectileType.LASER)),
            
            # Hybrid weapon upgrades
            Upgrade("Explosive Piercing", "Combine explosive and piercing", 
                   lambda p: self.create_hybrid_weapon(p, Weapon(ProjectileType.EXPLOSIVE), piercing=True)),
            Upgrade("Homing Spread", "Combine homing and spread", 
                   lambda p: self.create_hybrid_weapon(p, Weapon(ProjectileType.SPREAD))),
            Upgrade("Bouncing Laser", "Combine bouncing and laser", 
                   lambda p: self.create_hybrid_weapon(p, Weapon(ProjectileType.BOUNCING))),
            Upgrade("Explosive Rounds", "Area damage explosions", 
                   lambda p: self.change_weapon(p, ProjectileType.EXPLOSIVE)),
            Upgrade("Rapid Fire", "Very fast firing rate", 
                   lambda p: self.change_weapon(p, ProjectileType.RAPID)),
            Upgrade("Piercing Shots", "Projectiles pierce through enemies", 
                   lambda p: self.change_weapon(p, ProjectileType.PIERCING)),
            
            # Enhancement upgrades (can be stacked)
            Upgrade("Enhance Weapon +1", "Increase current weapon power", 
                   lambda p: self.enhance_weapon(p, 1)),
            Upgrade("Enhance Weapon +2", "Greatly increase current weapon power", 
                   lambda p: self.enhance_weapon(p, 2)),
            
            # Special upgrades
            Upgrade("Hybrid: Explosive + Piercing", "Combine explosive and piercing", 
                   lambda p: self.create_hybrid_weapon(p, ProjectileType.EXPLOSIVE, True)),
            Upgrade("Hybrid: Homing + Bouncing", "Bouncing homing missiles", 
                   lambda p: self.create_hybrid_weapon(p, ProjectileType.HOMING, True)),
            Upgrade("Hybrid: Laser + Explosive", "Explosive laser beams", 
                   lambda p: self.create_hybrid_weapon(p, ProjectileType.LASER, True)),
            Upgrade("Hybrid: Spread + Homing", "Homing spread shots", 
                   lambda p: self.create_hybrid_weapon(p, ProjectileType.SPREAD, True)),
            
            # Ultimate upgrades
            Upgrade("Ultimate Damage", "Massive damage increase", 
                   lambda p: self.ultimate_upgrade(p, 'damage')),
            Upgrade("Ultimate Fire Rate", "Extreme fire rate boost", 
                   lambda p: self.ultimate_upgrade(p, 'fire_rate')),
            Upgrade("Ultimate Speed", "Maximum movement speed", 
                   lambda p: self.ultimate_upgrade(p, 'speed')),
            Upgrade("Ultimate Health", "Double max HP and full heal", 
                   lambda p: self.ultimate_upgrade(p, 'health')),
        ]
        
        return upgrades
    
    def increase_max_hp(self, player, amount):
        """Increase max HP and heal proportionally"""
        player.max_hp += amount
        player.hp = min(player.hp + amount, player.max_hp)
    
    def enhance_weapon(self, player, levels):
        """Enhance current weapon by increasing its level"""
        if not hasattr(player, 'weapon_level'):
            player.weapon_level = 1
        
        player.weapon_level += levels
        player.damage += levels * 3  # Increase base damage
        player.fire_rate *= 1.1  # Slightly increase fire rate
    
    def change_weapon(self, player, weapon_type):
        """Change player's weapon type"""
        player.weapon = Weapon(weapon_type)
    
    def create_hybrid_weapon(self, player, other_weapon, piercing=False):
        """Create a hybrid weapon with combined properties"""
        if isinstance(other_weapon, Weapon):
            # Create hybrid from current weapon and another weapon
            hybrid = player.weapon.create_hybrid(other_weapon)
            player.weapon = hybrid
        else:
            # Create hybrid from current weapon and a weapon type
            other_weapon_obj = Weapon(other_weapon)
            hybrid = player.weapon.create_hybrid(other_weapon_obj)
            player.weapon = hybrid
        
        player.piercing = piercing
        if not hasattr(player, 'weapon_level'):
            player.weapon_level = 1
        player.weapon_level += 1  # Hybrid weapons get extra power
    
    def ultimate_upgrade(self, player, upgrade_type):
        """Apply ultimate upgrade based on type"""
        if upgrade_type == 'damage':
            player.damage += 25
            player.weapon_level += 2
        elif upgrade_type == 'fire_rate':
            player.weapon.fire_rate *= 2.0
        elif upgrade_type == 'speed':
            player.speed = min(player.speed + 100, 500)
        elif upgrade_type == 'health':
            player.max_hp *= 2
            player.hp = player.max_hp
    
    def waiting_for_choice(self):
        """Check if waiting for upgrade selection"""
        return self.waiting
    
    def trigger_level_up(self):
        """Trigger level up and show upgrade options"""
        self.waiting = True
        self.options = self.get_random_upgrades(3)
    
    def get_random_upgrades(self, count):
        """Get random upgrades, weighted by player needs and progression"""
        available_upgrades = self.all_upgrades.copy()
        unlocked_weapons = self.game.progression_manager.get_available_weapons()
        
        # Remove already selected upgrades that shouldn't stack
        filtered_upgrades = []
        for upgrade in available_upgrades:
            should_include = True
            
            # Check weapon unlocks
            if "Change to" in upgrade.title or "Hybrid:" in upgrade.title:
                weapon_unlocked = False
                for weapon_type in unlocked_weapons:
                    if weapon_type.value.lower() in upgrade.title.lower():
                        weapon_unlocked = True
                        break
                if not weapon_unlocked:
                    should_include = False
            
            # Don't offer piercing if already have it
            if "Piercing" in upgrade.title and self.game.player.piercing:
                should_include = False
            
            # Don't offer max HP upgrades too many times
            if "Max HP" in upgrade.title and self.game.player.max_hp > 200:
                should_include = False
            
            # Don't offer too many projectiles
            if "Projectile" in upgrade.title and self.game.player.weapon.projectile_count >= 8:
                should_include = False
            
            # Don't offer healing if at full health
            if "Heal" in upgrade.title and self.game.player.hp >= self.game.player.max_hp:
                should_include = False
            
            # Don't offer hybrid weapons until unlocked
            if "Hybrid" in upgrade.title and ProjectileType.HYBRID not in unlocked_weapons:
                should_include = False
            
            if should_include:
                filtered_upgrades.append(upgrade)
        
        # If no upgrades left, just use basic upgrades
        if not filtered_upgrades:
            filtered_upgrades = [u for u in available_upgrades if "Change to" not in u.title and "Hybrid" not in u.title]
        
        # If still no upgrades, use all upgrades as fallback
        if not filtered_upgrades:
            filtered_upgrades = available_upgrades
        
        return random.sample(filtered_upgrades, min(count, len(filtered_upgrades)))
    
    def handle_event(self, event):
        """Handle mouse clicks for upgrade selection"""
        if not self.waiting:
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            # Check which upgrade was clicked
            for i, upgrade in enumerate(self.options):
                rect = self.get_upgrade_rect(i)
                if rect.collidepoint(mx, my):
                    self.apply_upgrade(upgrade)
                    self.waiting = False
                    break
    
    def get_upgrade_rect(self, index):
        """Get rectangle for upgrade option at given index"""
        x = 200 + index * 300
        y = 250
        return pygame.Rect(x, y, 250, 120)
    
    def apply_upgrade(self, upgrade):
        """Apply selected upgrade"""
        upgrade.apply(self.game.player)
        self.selected_upgrade = upgrade
        
        # Track upgrade selection
        self.game.update_stats("upgrade_chosen")
    
    def draw_ui(self):
        """Draw upgrade selection UI"""
        if not self.waiting:
            return
        
        screen = self.game.screen
        
        # Draw overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Draw title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("LEVEL UP!", True, (255, 255, 100))
        title_rect = title_text.get_rect(center=(640, 150))
        screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_font = pygame.font.Font(None, 24)
        subtitle_text = subtitle_font.render("Choose an upgrade:", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(640, 200))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw upgrade options
        for i, upgrade in enumerate(self.options):
            rect = self.get_upgrade_rect(i)
            
            # Draw card background
            card_color = (80, 80, 120) if i == 0 else (60, 60, 90)
            pygame.draw.rect(screen, card_color, rect, border_radius=8)
            pygame.draw.rect(screen, (120, 120, 160), rect, 2, border_radius=8)
            
            # Draw upgrade title
            font = pygame.font.Font(None, 28)
            title_text = font.render(upgrade.title, True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(rect.centerx, rect.y + 30))
            screen.blit(title_text, title_rect)
            
            # Draw upgrade description
            desc_font = pygame.font.Font(None, 20)
            desc_text = desc_font.render(upgrade.description, True, (200, 200, 200))
            desc_rect = desc_text.get_rect(center=(rect.centerx, rect.y + 60))
            screen.blit(desc_text, desc_rect)
            
            # Draw hover effect
            mouse_pos = pygame.mouse.get_pos()
            if rect.collidepoint(mouse_pos):
                hover_overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
                hover_overlay.fill((255, 255, 255, 30))
                screen.blit(hover_overlay, rect)
                pygame.draw.rect(screen, (200, 200, 255), rect, 3, border_radius=8)
