# Mega Boss Asset Instructions

## 📁 Where to Place Your Images

Place your 5 mega boss images in the following folder:
```
assets/images/enemies/
```

## 🏷️ Image Naming Convention

Name your images as follows for them to be automatically loaded:

1. **mega_boss.png** - Main mega boss sprite (required)
2. **mega_boss_dash.png** - Dash/charging animation (optional)
3. **mega_boss_attack.png** - Attack animation (optional)
4. **mega_boss_hurt.png** - Hurt/damaged state (optional)
5. **mega_boss_death.png** - Death animation (optional)

## 🎮 How the System Works

- The game will automatically load any images in the `assets/images/enemies/` folder
- If no custom image is found, it falls back to the generated purple star shape
- Images are automatically scaled to fit the enemy size
- All images should have transparent backgrounds (PNG format recommended)

## 📐 Image Specifications

- **Format**: PNG (with transparency) or JPG
- **Size**: Any size (will be auto-scaled)
- **Background**: Transparent recommended
- **Orientation**: Facing upward/forward

## 🔄 Animation Support

The system is set up to support multiple states:
- Normal state: `mega_boss.png`
- Special states can be added later for animations

## 🚀 Quick Setup

1. Copy your 5 mega boss images to `assets/images/enemies/`
2. Rename the main image to `mega_boss.png`
3. Start the game - your custom mega boss will appear!

## 🎨 Tips

- Keep the image centered and roughly square for best results
- Higher resolution images will look better when scaled down
- Consider the color scheme matching your game's aesthetic
