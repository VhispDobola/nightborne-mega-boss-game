# NightBorne Mega Boss Game

A Python-based action game featuring a fully animated NightBorne mega boss with spritesheet animations, multiple enemy types, and wave-based gameplay.

## 🎮 Features

### 🦾 Mega Boss System
- **Fully Animated NightBorne** with 6 animation states:
  - Normal/Idle (9 frames, looping)
  - Dash (6 frames, looping) 
  - Run (6 frames, looping)
  - Attack (13 frames, one-time)
  - Hurt (6 frames, one-time)
  - Death (24 frames, one-time)
- **Spritesheet Animation System** - 115 frames from 1840x400 spritesheet
- **State-based Animation Switching** - Dynamic animation changes based on actions
- **0.8s Dash Pause** - Tactical dash mechanics as requested

### ⚔️ Enemy Types & Abilities
- **Basic Enemies** - Balanced chasers
- **Tanks** - High HP, slow movement
- **Fast Enemies** - Quick movement with dash abilities
- **Healers** - Visual healing effects for other enemies
- **Bombers** - Explosion mechanics with screen shake
- **Projectile Enemies** - Ranged attacks
- **Laser Enemies** - Beam attacks
- **Mortar Enemies** - Area damage
- **Summoner Enemies** - Spawn additional enemies
- **Assassin Enemies** - Stealth mechanics
- **Boss Enemies** - Special abilities and enhanced stats
- **Mega Boss** - The ultimate NightBorne challenge

### 🌊 Wave System
- **Progressive Difficulty** - Enemies unlock gradually
- **Endless Mode** - Continuous gameplay after wave 10
- **Smart Enemy Scaling** - Stats increase based on player level
- **Visual Wave Progression** - Clear indicators and transitions

### 🎨 Visual Effects
- **Particle System** - Explosions, healing, dash trails
- **Screen Shake** - Impact effects for explosions and abilities
- **Floating Damage Text** - Combat feedback
- **Custom Asset Loading** - Support for PNG, JPG, GIF, and spritesheets
- **Fallback Visuals** - Generated shapes when custom assets unavailable

### 🎵 Audio System
- **Dynamic Audio Manager** - Context-aware sound effects
- **Enemy Voice Types** - Different audio profiles for enemy types
- **Background Music** - Atmospheric gameplay music
- **Sound Effects** - Combat, abilities, and UI sounds

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Pygame-ce 2.5.6 or later

### Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/windsurf-project-5.git
   cd windsurf-project-5
   ```

2. **Install dependencies:**
   ```bash
   pip install pygame-ce
   ```

3. **Run the game:**
   ```bash
   python Main.py
   ```

## 🎮 How to Play

### Controls
- **WASD/Arrow Keys** - Move your character
- **Mouse** - Aim and shoot projectiles
- **Left Click** - Fire primary weapon
- **Right Click** - Special ability (if available)
- **ESC** - Pause game
- **Space** - Interact with menus

### Gameplay
1. **Survive waves** of increasingly difficult enemies
2. **Defeat the NightBorne mega boss** in later waves
3. **Collect XP** from defeated enemies to level up
4. **Choose upgrades** between waves to enhance your abilities
5. **Try Endless Mode** for continuous challenge after wave 10

### Game Modes
- **Normal Mode** - Complete 10 waves to win
- **Endless Mode** - Continue playing with escalating difficulty

## 🛠️ Development

### Project Structure
```
windsurf-project-5/
├── Main.py                 # Game entry point
├── game.py                 # Main game loop and logic
├── player.py               # Player character and mechanics
├── enemy.py                # Enemy system and AI
├── projectile.py           # Projectile mechanics
├── waves.py                # Wave management system
├── effects.py              # Visual effects and particles
├── ui.py                   # User interface elements
├── powerups.py             # Power-up system
├── upgrades.py             # Upgrade management
├── xp.py                   # Experience and leveling
├── stats_screen.py         # End game statistics
├── music.py                # Audio management
├── sounds.py               # Sound effects
├── enhanced_audio.py       # Advanced audio system
├── visual_feedback.py      # Visual feedback system
├── asset_loader.py          # Asset management
├── spritesheet_animator.py # Animation system
├── mega_boss_test.py       # Mega boss animation tester
├── frame_inspector.py      # Spritesheet analysis tool
└── assets/                 # Game assets
    ├── images/
    │   └── enemies/        # Enemy sprites and spritesheets
    └── README.md           # Asset instructions
```

### Key Systems

#### Animation System
- **Spritesheet Animator** - Frame-by-frame animation from spritesheets
- **Frame Inspector** - Visual tool for identifying animation frames
- **Asset Loader** - Centralized asset management with fallback support

#### Enemy System
- **Type-based Enemies** - Each with unique behaviors and abilities
- **Ability Cooldowns** - Strategic timing for special attacks
- **Visual Feedback** - Clear indicators for enemy actions

#### Progression System
- **Wave Manager** - Controls enemy spawning and difficulty
- **Progression Manager** - Unlocks content based on player progress
- **Upgrade System** - Player enhancement choices

### Testing Tools

#### Mega Boss Animation Tester
```bash
python mega_boss_test.py
```
- Test all NightBorne animations
- Switch between states with number keys (1-6)
- Visual feedback for animation timing

#### Frame Inspector
```bash
python frame_inspector.py
```
- Visual spritesheet analysis
- Scroll through all 115 frames
- Identify animation boundaries
- Export frame configurations

## 🎨 Custom Assets

### Adding Custom Enemy Sprites
1. Place images in `assets/images/enemies/`
2. Follow naming convention:
   - `mega_boss.png` - Main sprite
   - `mega_boss_spritesheet.png` - Animation spritesheet
   - `enemy_type.png` - Individual enemy sprites

### Spritesheet Format
- **Format**: PNG with transparency
- **Layout**: Horizontal frames (80x80 pixels each)
- **Frame Order**: Normal → Dash → Run → Attack → Hurt → Death

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Pygame-ce** - Game development framework
- **NightBorne Assets** - Custom mega boss sprites and animations
- **Community Feedback** - For helping shape the game mechanics

## 🐛 Bug Reports & Feature Requests

Please use the GitHub Issues tab to report bugs or request features:
- **Bug Reports**: Include steps to reproduce and system information
- **Feature Requests**: Describe the desired functionality and use case

---

**Enjoy battling the NightBorne mega boss!** 🦾⚔️✨
