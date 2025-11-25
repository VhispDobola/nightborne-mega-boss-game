# Bullet Heaven Game

A complete bullet-heaven (survivors-style) game built with Python and Pygame.

## Features

### Core Gameplay
- **Top-down arena** with player-centered movement
- **Auto-shooting** system with fire rate control
- **Real-time enemy spawning** with increasing difficulty
- **Delta time** for consistent movement regardless of FPS
- **Win condition**: Survive 10 minutes to achieve victory

### Player System
- **WASD movement** with screen boundary constraints
- **Stats system**:
  - HP/Max HP
  - Movement speed
  - Damage
  - Fire rate
  - Projectile speed
  - Pickup range
- **Auto-aim shooting** with directional spread patterns
- **Leveling system** with XP progression

### Enemy Types
1. **Basic Chaser** (Red Triangle)
   - Balanced stats (30 HP, 120 speed)
   - Standard damage (10)
   - 15 XP reward

2. **Tank** (Purple Square)
   - High HP, slow speed (100 HP, 60 speed)
   - High damage (20)
   - 30 XP reward

3. **Fast Melee** (Orange Diamond)
   - Low HP, high speed (20 HP, 200 speed)
   - Medium damage (15)
   - Zigzag movement pattern
   - 20 XP reward

### Weapon System
- **Multiple projectile types**:
  - Basic (Yellow)
  - Piercing (Purple)
  - Explosive (Orange)
  - Rapid Fire (Blue)
- **Stacking upgrades** (more projectiles, higher damage, etc.)
- **Piercing mechanics** for certain weapon types

### XP & Progression
- **XP orbs** with visual indicators based on value:
  - Blue: Low value (10 XP)
  - Green: Medium value (20 XP)
  - Gold: High value (40 XP)
- **Pickup radius** system with magnetic attraction
- **Level-up system** with 3 random upgrade choices

### Upgrade System
On each level-up, choose from 3 random upgrades:
- **Damage upgrades**: +5, +10, +20%
- **Fire rate upgrades**: +0.5, +100%
- **Movement upgrades**: +30 speed, +20%
- **Projectile upgrades**: +1/+2 projectiles, +100 speed
- **Pickup upgrades**: +20 range, +50%
- **Health upgrades**: Heal 50/Full, +20/+50 max HP
- **Special upgrades**: Piercing shots, explosive rounds

### UI Elements
- **HP bar** (top-left) with color coding
- **XP bar** (bottom) with level display
- **Stats display** (top-right)
- **Game timer** with progress bar
- **Upgrade selection interface** with hover effects

## 🎮 Game Controls

### **Movement**
- **W**: Move up
- **A**: Move left
- **S**: Move down
- **D**: Move right

### **Combat**
- **Mouse**: Aim direction (projectiles fire toward mouse position)
- **Hold Left Click**: Continuously shoot projectiles at fire rate
- **Release Left Click**: Stop shooting
- **Left Click (during level-up)**: Select upgrade option

### **Game Actions**
- **R**: Restart game (only on game over or victory screen)

### **Game States**
- **Playing**: WASD to move, hold left click to shoot
- **Paused (Level-up)**: Click to select one of 3 upgrade options
- **Game Over/Victory**: Press R to restart

## 🎯 Key Features

- **Manual Shooting**: Hold left mouse button to continuously fire
- **Mouse Aim**: Projectiles fire directly toward cursor position
- **Fire Rate Control**: Shooting speed determined by fire rate stat
- **Magnetic pickup**: XP orbs automatically move toward you when in range
- **Progressive difficulty**: Enemy spawn rate increases over time

The game requires active engagement - time your shots and position yourself carefully while dodging enemies!

## Installation & Running

1. **Install Pygame**:
```bash
pip install pygame
```

2. **Run the game**:
```bash
python main.py
```

## File Structure

```
windsurf-project-5/
├── main.py              # Entry point
├── game.py              # Main game class and loop
├── player.py            # Player class with stats and shooting
├── enemy.py             # Enemy classes and types
├── projectile.py        # Projectile and weapon systems
├── xp.py                # XP orb system
├── upgrades.py          # Upgrade management
├── ui.py                # UI rendering and elements
└── README.md            # This file
```

## Performance Features

- **Sprite groups** for efficient rendering
- **Delta time** for frame-independent movement
- **Collision optimization** with spatial grouping
- **60 FPS cap** for consistent performance

## Game Balance

- **Difficulty scaling**: Enemy spawn rate increases over time
- **Progressive enemy types**: New enemy types appear as time progresses
- **XP scaling**: Higher-level enemies give more XP
- **Upgrade variety**: Smart upgrade selection prevents overpowered combinations

## Extending the Game

The game is designed to be easily extensible:

- **Add new enemy types** by extending the `EnemyType` enum
- **Create new weapons** by adding to `ProjectileType`
- **Add new upgrades** in the `UpgradeManager.create_upgrades()` method
- **Modify game balance** through the various stat constants
- **Add new UI elements** in the `UI` class

## Tips for Playing

1. **Prioritize movement speed** early to dodge enemies
2. **Increase projectile count** for crowd control
3. **Balance damage and fire rate** for consistent DPS
4. **Watch your positioning** - don't get cornered
5. **Collect XP quickly** - they disappear after 10 seconds
6. **Choose upgrades based on current needs** (healing when low, damage when overwhelmed)

Enjoy surviving the bullet heaven!
