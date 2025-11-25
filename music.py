import pygame
import numpy as np
import math

class MusicManager:
    """Manages generated background music for the game"""
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
        self.current_music = None
        self.volume = 0.3
        self.enabled = True
        
        # Generate music tracks
        self.generate_music_tracks()
        
    def generate_music_tracks(self):
        """Generate background music tracks"""
        self.tracks = {
            'normal': self.generate_normal_music(),
            'boss': self.generate_boss_music(),
            'victory': self.generate_victory_music(),
            'game_over': self.generate_game_over_music()
        }
    
    def generate_normal_music(self):
        """Generate normal gameplay background music"""
        sample_rate = 22050
        duration = 30  # 30 seconds looping
        samples = int(sample_rate * duration)
        
        # Create a simple melodic pattern
        melody_freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C major scale
        
        # Base chord progression (C - Am - F - G)
        chord_progression = [
            [261.63, 329.63, 392.00],  # C major
            [220.00, 277.18, 329.63],  # A minor
            [174.61, 220.00, 261.63],  # F major
            [196.00, 246.94, 293.66]   # G major
        ]
        
        # Generate music
        music = np.zeros(samples)
        
        # Add bass line
        bass_pattern = [1, 0, 0, 1, 0, 1, 0, 0]  # Simple bass pattern
        for i in range(0, samples, sample_rate // 8):  # 8th notes
            if i + sample_rate // 8 <= samples:
                if bass_pattern[(i // (sample_rate // 8)) % len(bass_pattern)]:
                    chord_idx = (i // (sample_rate * 2)) % len(chord_progression)
                    freq = chord_progression[chord_idx][0]  # Root note
                    bass_wave = np.sin(2 * np.pi * freq * np.linspace(0, 0.125, sample_rate // 8))
                    bass_wave *= 0.3
                    music[i:i+len(bass_wave)] += bass_wave
        
        # Add simple melody
        for i in range(0, samples, sample_rate // 4):  # Quarter notes
            if i + sample_rate // 4 <= samples:
                freq = melody_freqs[np.random.randint(0, len(melody_freqs))]
                melody_wave = np.sin(2 * np.pi * freq * np.linspace(0, 0.25, sample_rate // 4))
                melody_wave *= 0.2 * np.exp(-np.linspace(0, 4, sample_rate // 4))  # Decay
                music[i:i+len(melody_wave)] += melody_wave
        
        # Add rhythm
        rhythm_pattern = [1, 0, 1, 0, 1, 1, 0, 1]
        for i in range(0, samples, sample_rate // 16):  # 16th notes
            if i + sample_rate // 16 <= samples:
                if rhythm_pattern[(i // (sample_rate // 16)) % len(rhythm_pattern)]:
                    # Simple kick drum sound
                    kick = np.sin(2 * np.pi * 60 * np.linspace(0, 0.0625, sample_rate // 16))
                    kick *= 0.4 * np.exp(-np.linspace(0, 10, sample_rate // 16))
                    music[i:i+len(kick)] += kick
        
        # Apply envelope and normalize
        music *= 0.5
        music = np.tanh(music)  # Soft clipping
        
        # Convert to pygame sound
        music = np.array(music * 32767, dtype=np.int16)
        music = np.repeat(music.reshape(-1, 1), 2, axis=1)
        
        return pygame.sndarray.make_sound(music)
    
    def generate_boss_music(self):
        """Generate boss battle music"""
        sample_rate = 22050
        duration = 30
        samples = int(sample_rate * duration)
        
        # Dark, dramatic music with minor chords
        minor_chords = [
            [220.00, 277.18, 329.63],  # A minor
            [196.00, 246.94, 293.66],  # G minor
            [174.61, 220.00, 261.63],  # F minor
            [246.94, 311.13, 369.99]   # B diminished
        ]
        
        music = np.zeros(samples)
        
        # Dramatic bass line
        for i in range(0, samples, sample_rate // 4):  # Quarter notes
            if i + sample_rate // 4 <= samples:
                chord_idx = (i // (sample_rate * 2)) % len(minor_chords)
                freq = minor_chords[chord_idx][0]
                bass_wave = np.sin(2 * np.pi * freq * np.linspace(0, 0.25, sample_rate // 4))
                bass_wave *= 0.4 * (1 + 0.3 * np.sin(2 * np.pi * 2 * np.linspace(0, 0.25, sample_rate // 4)))  # Tremolo
                music[i:i+len(bass_wave)] += bass_wave
        
        # Ominous melody
        melody_freqs = [220.00, 246.94, 261.63, 293.66, 311.13]
        for i in range(0, samples, sample_rate // 3):  # Slower melody
            if i + sample_rate // 3 <= samples:
                freq = melody_freqs[np.random.randint(0, len(melody_freqs))]
                melody_wave = np.sin(2 * np.pi * freq * np.linspace(0, 0.33, sample_rate // 3))
                melody_wave *= 0.15 * np.exp(-np.linspace(0, 2, sample_rate // 3))
                music[i:i+len(melody_wave)] += melody_wave
        
        # Heavy drums
        for i in range(0, samples, sample_rate // 8):  # 8th notes
            if i + sample_rate // 8 <= samples:
                # Kick
                kick = np.sin(2 * np.pi * 50 * np.linspace(0, 0.125, sample_rate // 8))
                kick *= 0.5 * np.exp(-np.linspace(0, 8, sample_rate // 8))
                music[i:i+len(kick)] += kick
                
                # Snare on off-beats
                if (i // (sample_rate // 8)) % 2 == 1:
                    snare = np.random.normal(0, 0.1, sample_rate // 8)  # Noise
                    snare *= np.exp(-np.linspace(0, 6, sample_rate // 8))
                    music[i:i+len(snare)] += snare
        
        # Normalize
        music *= 0.6
        music = np.tanh(music)
        
        music = np.array(music * 32767, dtype=np.int16)
        music = np.repeat(music.reshape(-1, 1), 2, axis=1)
        
        return pygame.sndarray.make_sound(music)
    
    def generate_victory_music(self):
        """Generate victory fanfare"""
        sample_rate = 22050
        duration = 5
        samples = int(sample_rate * duration)
        
        # Triumphant major chords
        victory_chords = [
            [261.63, 329.63, 392.00],  # C major
            [293.66, 369.99, 440.00],  # D major
            [329.63, 415.30, 493.88],  # E major
            [392.00, 493.88, 587.33]   # G major
        ]
        
        music = np.zeros(samples)
        
        # Ascending chord progression
        chord_duration = sample_rate // 2  # Half second per chord
        for i, chord in enumerate(victory_chords):
            start = i * chord_duration
            end = min(start + chord_duration, samples)
            
            if start < samples:
                for freq in chord:
                    chord_wave = np.sin(2 * np.pi * freq * np.linspace(0, 0.5, end - start))
                    chord_wave *= 0.3
                    music[start:end] += chord_wave
        
        # Add triumphant melody
        melody = [523.25, 587.33, 659.25, 698.46, 783.99]  # High C major scale
        note_duration = sample_rate // 4  # Quarter notes
        
        for i, freq in enumerate(melody):
            start = i * note_duration
            end = min(start + note_duration, samples)
            
            if start < samples:
                melody_wave = np.sin(2 * np.pi * freq * np.linspace(0, 0.25, end - start))
                melody_wave *= 0.2 * np.exp(-np.linspace(0, 3, end - start))
                music[start:end] += melody_wave
        
        music *= 0.7
        
        music = np.array(music * 32767, dtype=np.int16)
        music = np.repeat(music.reshape(-1, 1), 2, axis=1)
        
        return pygame.sndarray.make_sound(music)
    
    def generate_game_over_music(self):
        """Generate game over music"""
        sample_rate = 22050
        duration = 4
        samples = int(sample_rate * duration)
        
        # Descending minor melody
        descending_melody = [440.00, 392.00, 349.23, 329.63, 293.66, 261.63]
        
        music = np.zeros(samples)
        
        note_duration = sample_rate // len(descending_melody)
        for i, freq in enumerate(descending_melody):
            start = i * note_duration
            end = min(start + note_duration, samples)
            
            if start < samples:
                note_wave = np.sin(2 * np.pi * freq * np.linspace(0, 1/note_duration, end - start))
                note_wave *= 0.3 * np.exp(-np.linspace(0, 2, end - start))
                music[start:end] += note_wave
        
        # Add sad bass
        bass_freq = 130.81  # C3
        bass_wave = np.sin(2 * np.pi * bass_freq * np.linspace(0, duration, samples))
        bass_wave *= 0.2
        music += bass_wave
        
        music *= 0.5
        
        music = np.array(music * 32767, dtype=np.int16)
        music = np.repeat(music.reshape(-1, 1), 2, axis=1)
        
        return pygame.sndarray.make_sound(music)
    
    def play_music(self, track_name, loop=True):
        """Play a music track"""
        if self.enabled and track_name in self.tracks:
            if self.current_music:
                self.current_music.stop()
            
            self.current_music = self.tracks[track_name]
            self.current_music.set_volume(self.volume)
            
            if loop:
                self.current_music.play(-1)  # Loop indefinitely
            else:
                self.current_music.play(0)  # Play once
    
    def stop_music(self):
        """Stop current music"""
        if self.current_music:
            self.current_music.stop()
            self.current_music = None
    
    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.current_music:
            self.current_music.set_volume(self.volume)
    
    def toggle_music(self):
        """Toggle music on/off"""
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_music()

# Global music manager instance
music_manager = None

def init_music():
    """Initialize the music system"""
    global music_manager
    try:
        music_manager = MusicManager()
        return True
    except Exception as e:
        print(f"Failed to initialize music system: {e}")
        return False

def play_music(track_name, loop=True):
    """Play a music track"""
    global music_manager
    if music_manager and music_manager.enabled:
        music_manager.play_music(track_name, loop)

def stop_music():
    """Stop the current music"""
    global music_manager
    if music_manager:
        music_manager.stop_music()

def toggle_music():
    """Toggle music on/off"""
    global music_manager
    if music_manager:
        music_manager.toggle_music()
    return music_manager.enabled if music_manager else False
