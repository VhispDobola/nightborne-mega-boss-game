import pygame
import random
import math
from enum import Enum

class AudioEventType(Enum):
    PLAYER_SHOOT = "player_shoot"
    PLAYER_HIT = "player_hit"
    PLAYER_HEAL = "player_heal"
    PLAYER_LEVEL_UP = "player_level_up"
    ENEMY_HIT = "enemy_hit"
    ENEMY_DEATH = "enemy_death"
    EXPLOSION = "explosion"
    POWER_UP_PICKUP = "power_up_pickup"
    COMBO_MILESTONE = "combo_milestone"
    WAVE_START = "wave_start"
    WAVE_COMPLETE = "wave_complete"
    BOSS_SPAWN = "boss_spawn"
    BOSS_DEFEATED = "boss_defeated"
    CRITICAL_HIT = "critical_hit"
    AREA_DAMAGE = "area_damage"

class EnemyVoiceType(Enum):
    BASIC = "basic"
    FAST = "fast"
    TANK = "tank"
    BOSS = "boss"
    MEGA_BOSS = "mega_boss"

class DynamicAudioManager:
    """Enhanced audio system with dynamic music and enemy voices"""
    def __init__(self, game):
        self.game = game
        self.sound_enabled = True
        self.music_enabled = True
        
        # Sound channels
        self.sfx_channel = pygame.mixer.Channel(0)
        self.voice_channel = pygame.mixer.Channel(1)
        self.ambient_channel = pygame.mixer.Channel(2)
        
        # Sound effects library
        self.sounds = {}
        self.enemy_voices = {}
        self.music_tracks = {}
        
        # Dynamic music system
        self.current_music_state = "normal"
        self.music_intensity = 0.5
        self.target_intensity = 0.5
        self.intensity_transition_speed = 0.1
        
        # Voice cooldowns to prevent spam
        self.voice_cooldowns = {}
        self.voice_cooldown_time = 2.0  # 2 seconds between same voice type
        
        # Initialize audio
        self.init_audio()
    
    def init_audio(self):
        """Initialize all audio assets"""
        # Generate sound effects
        self.generate_sounds()
        
        # Generate enemy voices
        self.generate_enemy_voices()
        
        # Generate music tracks
        self.generate_music_tracks()
    
    def generate_sounds(self):
        """Generate procedural sound effects"""
        # Player sounds
        self.sounds[AudioEventType.PLAYER_SHOOT] = self.generate_shoot_sound(800, 0.1)
        self.sounds[AudioEventType.PLAYER_HIT] = self.generate_impact_sound(200, 0.2)
        self.sounds[AudioEventType.PLAYER_HEAL] = self.generate_heal_sound(600, 0.3)
        self.sounds[AudioEventType.PLAYER_LEVEL_UP] = self.generate_level_up_sound(0.5)
        
        # Enemy sounds
        self.sounds[AudioEventType.ENEMY_HIT] = self.generate_impact_sound(300, 0.15)
        self.sounds[AudioEventType.ENEMY_DEATH] = self.generate_death_sound(0.4)
        self.sounds[AudioEventType.EXPLOSION] = self.generate_explosion_sound(0.6)
        
        # Game event sounds
        self.sounds[AudioEventType.POWER_UP_PICKUP] = self.generate_pickup_sound(1000, 0.2)
        self.sounds[AudioEventType.COMBO_MILESTONE] = self.generate_combo_sound(0.3)
        self.sounds[AudioEventType.WAVE_START] = self.generate_wave_sound(0.4)
        self.sounds[AudioEventType.WAVE_COMPLETE] = self.generate_victory_sound(0.5)
        self.sounds[AudioEventType.BOSS_SPAWN] = self.generate_boss_spawn_sound(0.8)
        self.sounds[AudioEventType.BOSS_DEFEATED] = self.generate_mega_victory_sound(1.0)
        self.sounds[AudioEventType.CRITICAL_HIT] = self.generate_critical_sound(0.3)
        self.sounds[AudioEventType.AREA_DAMAGE] = self.generate_area_damage_sound(0.4)
    
    def generate_enemy_voices(self):
        """Generate enemy voice sounds"""
        self.enemy_voices[EnemyVoiceType.BASIC] = {
            "spawn": self.generate_voice_sound(150, 0.2, "growl"),
            "attack": self.generate_voice_sound(200, 0.1, "hiss"),
            "death": self.generate_voice_sound(100, 0.3, "groan"),
            "pain": self.generate_voice_sound(180, 0.15, "yelp")
        }
        
        self.enemy_voices[EnemyVoiceType.FAST] = {
            "spawn": self.generate_voice_sound(300, 0.15, "squeal"),
            "attack": self.generate_voice_sound(400, 0.1, "chirp"),
            "death": self.generate_voice_sound(200, 0.25, "scream"),
            "pain": self.generate_voice_sound(350, 0.1, "yelp")
        }
        
        self.enemy_voices[EnemyVoiceType.TANK] = {
            "spawn": self.generate_voice_sound(80, 0.4, "rumble"),
            "attack": self.generate_voice_sound(100, 0.2, "grunt"),
            "death": self.generate_voice_sound(60, 0.6, "roar"),
            "pain": self.generate_voice_sound(90, 0.3, "growl")
        }
        
        self.enemy_voices[EnemyVoiceType.BOSS] = {
            "spawn": self.generate_voice_sound(50, 0.8, "roar"),
            "attack": self.generate_voice_sound(80, 0.3, "bellow"),
            "death": self.generate_voice_sound(40, 1.2, "death_roar"),
            "pain": self.generate_voice_sound(70, 0.4, "growl")
        }
        
        self.enemy_voices[EnemyVoiceType.MEGA_BOSS] = {
            "spawn": self.generate_voice_sound(30, 1.5, "mega_roar"),
            "attack": self.generate_voice_sound(50, 0.5, "mega_bellow"),
            "death": self.generate_voice_sound(25, 2.0, "mega_death"),
            "pain": self.generate_voice_sound(40, 0.6, "mega_growl")
        }
    
    def generate_music_tracks(self):
        """Generate dynamic music tracks"""
        self.music_tracks = {
            "normal": self.generate_music_track("ambient", 120, 0.3),
            "intense": self.generate_music_track("action", 140, 0.5),
            "boss": self.generate_music_track("boss", 100, 0.7),
            "victory": self.generate_music_track("victory", 80, 0.4),
            "game_over": self.generate_music_track("somber", 60, 0.3)
        }
    
    def generate_shoot_sound(self, frequency, duration):
        """Generate shoot sound effect"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        waves = pygame.sndarray.make_sound(
            self.generate_shoot_wave(frequency, duration, sample_rate)
        )
        return waves
    
    def generate_shoot_wave(self, frequency, duration, sample_rate):
        """Generate shoot wave data"""
        import numpy as np
        samples = int(sample_rate * duration)
        waves = np.zeros(samples, dtype=np.float32)
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Sharp attack with quick decay
            envelope = math.exp(-t * 20)
            waves[i] = envelope * math.sin(2 * math.pi * frequency * t)
            # Add some noise for texture
            waves[i] += random.uniform(-0.1, 0.1) * envelope
        
        return np.array(waves * 32767, dtype=np.int16)
    
    def generate_impact_sound(self, frequency, duration):
        """Generate impact sound effect"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Sharp attack with medium decay
            envelope = math.exp(-t * 15)
            waves[i, 0] = envelope * (
                math.sin(2 * math.pi * frequency * t) +
                0.3 * math.sin(4 * math.pi * frequency * t)  # Add harmonic
            )
            # Add impact noise
            waves[i, 0] += random.uniform(-0.2, 0.2) * envelope
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_heal_sound(self, frequency, duration):
        """Generate healing sound effect"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Rising pitch with smooth envelope
            pitch = frequency * (1 + t * 0.5)
            envelope = math.sin(math.pi * t)  # Smooth rise and fall
            waves[i, 0] = envelope * math.sin(2 * math.pi * pitch * t)
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_level_up_sound(self, duration):
        """Generate level up sound effect"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Rising arpeggio
            base_freq = 400
            freq = base_freq * (1 + t * 2)
            envelope = math.sin(math.pi * t)
            waves[i, 0] = envelope * math.sin(2 * math.pi * freq * t)
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_death_sound(self, duration):
        """Generate death sound effect"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Falling pitch with noise
            freq = 200 * (1 - t * 0.8)
            envelope = math.exp(-t * 3)
            waves[i, 0] = envelope * (
                0.7 * math.sin(2 * math.pi * freq * t) +
                0.3 * random.uniform(-1, 1)
            )
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_explosion_sound(self, duration):
        """Generate explosion sound effect"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Low frequency rumble with noise
            envelope = math.exp(-t * 2)
            waves[i, 0] = envelope * (
                0.5 * math.sin(2 * math.pi * 50 * t) +
                0.5 * random.uniform(-1, 1)
            )
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_pickup_sound(self, frequency, duration):
        """Generate pickup sound effect"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Twinkly sound
            envelope = math.exp(-t * 10)
            waves[i, 0] = envelope * (
                math.sin(2 * math.pi * frequency * t) +
                0.5 * math.sin(4 * math.pi * frequency * t)
            )
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_combo_sound(self, duration):
        """Generate combo milestone sound"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Quick ascending notes
            freq = 400 + (i / samples) * 800
            envelope = math.exp(-t * 5)
            waves[i, 0] = envelope * math.sin(2 * math.pi * freq * t)
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_wave_sound(self, duration):
        """Generate wave start sound"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Dramatic horn sound
            freq = 150 + math.sin(t * 10) * 50
            envelope = math.sin(math.pi * t)
            waves[i, 0] = envelope * math.sin(2 * math.pi * freq * t)
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_victory_sound(self, duration):
        """Generate victory sound"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Triumphant fanfare
            freq = 300 + (i / samples) * 400
            envelope = math.sin(math.pi * t)
            waves[i, 0] = envelope * (
                math.sin(2 * math.pi * freq * t) +
                0.3 * math.sin(3 * math.pi * freq * t)
            )
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_boss_spawn_sound(self, duration):
        """Generate boss spawn sound"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Deep, menacing sound
            freq = 60 + math.sin(t * 2) * 20
            envelope = math.sin(math.pi * t)
            waves[i, 0] = envelope * (
                math.sin(2 * math.pi * freq * t) +
                0.4 * random.uniform(-1, 1)
            )
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_mega_victory_sound(self, duration):
        """Generate mega victory sound"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Epic victory fanfare
            base_freq = 200
            freq = base_freq * (1 + (i / samples) * 2)
            envelope = math.sin(math.pi * t)
            waves[i, 0] = envelope * (
                math.sin(2 * math.pi * freq * t) +
                0.5 * math.sin(2 * math.pi * freq * 1.5 * t) +
                0.3 * math.sin(2 * math.pi * freq * 2 * t)
            )
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_critical_sound(self, duration):
        """Generate critical hit sound"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Sharp, high-pitched impact
            freq = 1000 + (i / samples) * 500
            envelope = math.exp(-t * 20)
            waves[i, 0] = envelope * math.sin(2 * math.pi * freq * t)
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_area_damage_sound(self, duration):
        """Generate area damage sound"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Whoosh + impact
            freq = 100 * (1 + t * 3)
            envelope = math.sin(math.pi * t) * math.exp(-t * 2)
            waves[i, 0] = envelope * (
                0.6 * math.sin(2 * math.pi * freq * t) +
                0.4 * random.uniform(-1, 1)
            )
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_voice_sound(self, frequency, duration, voice_type):
        """Generate enemy voice sound"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        for i in range(samples):
            t = float(i) / sample_rate
            
            # Different voice characteristics
            if voice_type == "growl":
                freq = frequency * (1 + random.uniform(-0.2, 0.2))
                envelope = math.exp(-t * 3)
                waves[i, 0] = envelope * (
                    0.7 * math.sin(2 * math.pi * freq * t) +
                    0.3 * random.uniform(-1, 1)
                )
            elif voice_type == "hiss":
                freq = frequency * (1 + t * 0.5)
                envelope = math.exp(-t * 5)
                waves[i, 0] = envelope * (
                    0.5 * math.sin(2 * math.pi * freq * t) +
                    0.5 * random.uniform(-1, 1)
                )
            elif voice_type == "squeal":
                freq = frequency * (1 + t * 2)
                envelope = math.exp(-t * 4)
                waves[i, 0] = envelope * math.sin(2 * math.pi * freq * t)
            elif voice_type == "rumble":
                freq = frequency
                envelope = math.sin(math.pi * t)
                waves[i, 0] = envelope * (
                    0.8 * math.sin(2 * math.pi * freq * t) +
                    0.2 * random.uniform(-1, 1)
                )
            elif voice_type == "roar":
                freq = frequency * (1 - t * 0.3)
                envelope = math.sin(math.pi * t)
                waves[i, 0] = envelope * (
                    0.6 * math.sin(2 * math.pi * freq * t) +
                    0.4 * random.uniform(-1, 1)
                )
            else:  # default
                freq = frequency
                envelope = math.exp(-t * 3)
                waves[i, 0] = envelope * math.sin(2 * math.pi * freq * t)
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def generate_music_track(self, style, tempo, intensity):
        """Generate a simple music track"""
        duration = 10.0  # 10 second loop
        sample_rate = 22050
        samples = int(sample_rate * duration)
        
        import numpy as np
        waves = np.zeros((samples, 1))  # 2D array for mono
        
        # Generate simple melody based on style
        if style == "ambient":
            # Slow, peaceful melody
            melody_freqs = [220, 247, 262, 294, 330, 294, 262, 247]
        elif style == "action":
            # Fast, energetic melody
            melody_freqs = [440, 494, 523, 587, 659, 587, 523, 494]
        elif style == "boss":
            # Dramatic, low melody
            melody_freqs = [110, 123, 131, 147, 165, 147, 131, 123]
        elif style == "victory":
            # Triumphant melody
            melody_freqs = [330, 370, 415, 440, 494, 440, 415, 370]
        else:  # somber
            # Slow, minor melody
            melody_freqs = [196, 220, 247, 262, 294, 262, 247, 220]
        
        note_duration = duration / len(melody_freqs)
        
        for i in range(samples):
            t = float(i) / sample_rate
            
            # Find current note
            note_index = int(t / note_duration) % len(melody_freqs)
            note_t = (t % note_duration) / note_duration
            
            freq = melody_freqs[note_index]
            
            # Simple envelope
            envelope = math.sin(math.pi * note_t) * 0.3
            
            # Add some harmony
            waves[i, 0] = envelope * (
                0.6 * math.sin(2 * math.pi * freq * t) +
                0.3 * math.sin(2 * math.pi * freq * 1.5 * t) +
                0.1 * math.sin(2 * math.pi * freq * 2 * t)
            )
        
        return pygame.sndarray.make_sound(np.array(waves * 32767, dtype=np.int16))
    
    def play_sound(self, event_type, volume=0.5):
        """Play a sound effect"""
        if not self.sound_enabled or event_type not in self.sounds:
            return
        
        sound = self.sounds[event_type]
        sound.set_volume(volume)
        self.sfx_channel.play(sound)
    
    def play_enemy_voice(self, enemy_type, voice_event, volume=0.4):
        """Play enemy voice sound"""
        if not self.sound_enabled:
            return
        
        # Check cooldown
        cooldown_key = f"{enemy_type.value}_{voice_event}"
        if cooldown_key in self.voice_cooldowns:
            if self.voice_cooldowns[cooldown_key] > 0:
                return
        
        if enemy_type in self.enemy_voices and voice_event in self.enemy_voices[enemy_type]:
            voice = self.enemy_voices[enemy_type][voice_event]
            voice.set_volume(volume)
            self.voice_channel.play(voice)
            
            # Set cooldown
            self.voice_cooldowns[cooldown_key] = self.voice_cooldown_time
    
    def update_voice_cooldowns(self, dt):
        """Update voice cooldowns"""
        keys_to_remove = []
        for key, cooldown in self.voice_cooldowns.items():
            new_cooldown = cooldown - dt
            if new_cooldown <= 0:
                keys_to_remove.append(key)
            else:
                self.voice_cooldowns[key] = new_cooldown
        
        for key in keys_to_remove:
            del self.voice_cooldowns[key]
    
    def update_dynamic_music(self, dt):
        """Update dynamic music based on game state"""
        # Calculate target intensity based on game state
        enemy_count = len(self.game.enemies)
        player_hp_percentage = self.game.player.hp / self.game.player.max_hp
        
        # Determine target music state and intensity
        if self.game.game_state == "game_over":
            self.target_intensity = 0.2
            target_state = "game_over"
        elif self.game.game_state == "victory":
            self.target_intensity = 0.8
            target_state = "victory"
        elif any(enemy.enemy_type.value in ["boss", "mega_boss"] for enemy in self.game.enemies):
            self.target_intensity = 0.9
            target_state = "boss"
        elif enemy_count > 10:
            self.target_intensity = 0.7
            target_state = "intense"
        elif enemy_count > 5:
            self.target_intensity = 0.6
            target_state = "intense"
        else:
            self.target_intensity = 0.4
            target_state = "normal"
        
        # Smoothly transition intensity
        if abs(self.music_intensity - self.target_intensity) > 0.01:
            direction = 1 if self.target_intensity > self.music_intensity else -1
            self.music_intensity += direction * self.intensity_transition_speed * dt
            self.music_intensity = max(0, min(1, self.music_intensity))
        
        # Change music track if needed
        if target_state != self.current_music_state:
            self.current_music_state = target_state
            if self.music_enabled and target_state in self.music_tracks:
                music = self.music_tracks[target_state]
                music.set_volume(self.music_intensity * 0.3)  # Background music volume
                self.ambient_channel.play(music, loops=-1)
    
    def update(self, dt):
        """Update audio system"""
        self.update_voice_cooldowns(dt)
        self.update_dynamic_music(dt)
    
    def toggle_sound(self):
        """Toggle sound effects"""
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            self.sfx_channel.stop()
            self.voice_channel.stop()
    
    def toggle_music(self):
        """Toggle music"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.ambient_channel.stop()
        else:
            self.update_dynamic_music(0)  # Restart music
    
    def set_master_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        volume = max(0, min(1, volume))
        self.sfx_channel.set_volume(volume)
        self.voice_channel.set_volume(volume)
        self.ambient_channel.set_volume(volume * 0.3)  # Keep music quieter
