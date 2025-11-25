import pygame
import numpy as np
import math

class SoundManager:
    """Manages generated sound effects for the game"""
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.enabled = True
        self.volume = 0.5
        
        # Generate all sounds
        self.generate_sounds()
        
    def generate_sounds(self):
        """Generate all sound effects"""
        self.sounds['shoot'] = self.generate_shoot_sound()
        self.sounds['hit'] = self.generate_hit_sound()
        self.sounds['explosion'] = self.generate_explosion_sound()
        self.sounds['pickup'] = self.generate_pickup_sound()
        self.sounds['level_up'] = self.generate_level_up_sound()
        self.sounds['boss_spawn'] = self.generate_boss_spawn_sound()
        self.sounds['combo'] = self.generate_combo_sound()
        
    def generate_shoot_sound(self):
        """Generate shooting sound"""
        sample_rate = 22050
        duration = 0.1
        samples = int(sample_rate * duration)
        
        # Create a simple shoot sound with noise and tone
        frequency = 800
        noise = np.random.normal(0, 0.1, samples)
        tone = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
        
        # Combine and envelope
        sound = (tone * 0.3 + noise * 0.7) * np.exp(-np.linspace(0, 10, samples))
        
        # Convert to pygame sound
        sound = np.array(sound * 32767, dtype=np.int16)
        sound = np.repeat(sound.reshape(-1, 1), 2, axis=1)  # Stereo
        
        return pygame.sndarray.make_sound(sound)
    
    def generate_hit_sound(self):
        """Generate hit sound"""
        sample_rate = 22050
        duration = 0.05
        samples = int(sample_rate * duration)
        
        # Create a sharp hit sound
        frequency = 200
        tone = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
        noise = np.random.normal(0, 0.2, samples)
        
        # Combine with envelope
        sound = (tone * 0.5 + noise * 0.5) * np.exp(-np.linspace(0, 20, samples))
        
        # Convert to pygame sound
        sound = np.array(sound * 32767, dtype=np.int16)
        sound = np.repeat(sound.reshape(-1, 1), 2, axis=1)
        
        return pygame.sndarray.make_sound(sound)
    
    def generate_explosion_sound(self):
        """Generate explosion sound"""
        sample_rate = 22050
        duration = 0.3
        samples = int(sample_rate * duration)
        
        # Create explosion with low frequency and noise
        frequency = 60
        tone = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
        noise = np.random.normal(0, 0.3, samples)
        
        # Combine with envelope
        envelope = np.exp(-np.linspace(0, 5, samples))
        sound = (tone * 0.4 + noise * 0.6) * envelope
        
        # Convert to pygame sound
        sound = np.array(sound * 32767, dtype=np.int16)
        sound = np.repeat(sound.reshape(-1, 1), 2, axis=1)
        
        return pygame.sndarray.make_sound(sound)
    
    def generate_pickup_sound(self):
        """Generate XP pickup sound"""
        sample_rate = 22050
        duration = 0.15
        samples = int(sample_rate * duration)
        
        # Create ascending tone for pickup
        frequencies = np.linspace(400, 800, samples)
        tone = np.sin(2 * np.pi * frequencies * np.linspace(0, duration, samples))
        
        # Add envelope
        sound = tone * np.exp(-np.linspace(0, 8, samples))
        
        # Convert to pygame sound
        sound = np.array(sound * 32767, dtype=np.int16)
        sound = np.repeat(sound.reshape(-1, 1), 2, axis=1)
        
        return pygame.sndarray.make_sound(sound)
    
    def generate_level_up_sound(self):
        """Generate level up sound"""
        sample_rate = 22050
        duration = 0.5
        samples = int(sample_rate * duration)
        
        # Create ascending chord
        frequencies = [523, 659, 784]  # C, E, G
        sound = np.zeros(samples)
        
        for freq in frequencies:
            tone = np.sin(2 * np.pi * freq * np.linspace(0, duration, samples))
            sound += tone * 0.3
        
        # Add envelope
        sound = sound * np.exp(-np.linspace(0, 3, samples))
        
        # Convert to pygame sound
        sound = np.array(sound * 32767, dtype=np.int16)
        sound = np.repeat(sound.reshape(-1, 1), 2, axis=1)
        
        return pygame.sndarray.make_sound(sound)
    
    def generate_boss_spawn_sound(self):
        """Generate boss spawn sound"""
        sample_rate = 22050
        duration = 0.8
        samples = int(sample_rate * duration)
        
        # Create descending ominous tone
        frequency = 100
        tone = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
        vibrato = np.sin(2 * np.pi * 10 * np.linspace(0, duration, samples)) * 0.2
        
        sound = (tone * (1 + vibrato)) * np.exp(-np.linspace(0, 2, samples))
        
        # Convert to pygame sound
        sound = np.array(sound * 32767, dtype=np.int16)
        sound = np.repeat(sound.reshape(-1, 1), 2, axis=1)
        
        return pygame.sndarray.make_sound(sound)
    
    def generate_combo_sound(self):
        """Generate combo sound"""
        sample_rate = 22050
        duration = 0.2
        samples = int(sample_rate * duration)
        
        # Create quick ascending beep
        frequency = 1200
        tone = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
        
        # Sharp envelope
        sound = tone * np.exp(-np.linspace(0, 15, samples))
        
        # Convert to pygame sound
        sound = np.array(sound * 32767, dtype=np.int16)
        sound = np.repeat(sound.reshape(-1, 1), 2, axis=1)
        
        return pygame.sndarray.make_sound(sound)
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if self.enabled and sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(self.volume)
            sound.play()
    
    def set_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled

# Create global sound manager instance
sound_manager = None

def init_sounds():
    """Initialize the sound system"""
    global sound_manager
    try:
        sound_manager = SoundManager()
        return True
    except Exception as e:
        print(f"Failed to initialize sound system: {e}")
        return False

def play_sound(sound_name):
    """Play a sound effect"""
    global sound_manager
    if sound_manager:
        sound_manager.play_sound(sound_name)
