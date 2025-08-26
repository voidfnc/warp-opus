"""
Audio Engine for Opus One Audio Visualizer
Handles audio loading, playback, and real-time processing
"""

# Setup FFmpeg first
try:
    from . import ffmpeg_setup
except ImportError:
    import ffmpeg_setup

import numpy as np
import sounddevice as sd
import soundfile as sf
import librosa
import threading
import queue
from pathlib import Path
from pydub import AudioSegment
from scipy import signal
from typing import Optional, Tuple
import logging


class AudioEngine:
    """Main audio processing and playback engine"""
    
    def __init__(self, sample_rate=44100, block_size=2048):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.audio_data = None
        self.current_position = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        
        # Audio analysis buffers
        self.fft_data = None
        self.frequency_bands = None
        self.beat_detected = False
        
        # Threading
        self.playback_thread = None
        self.audio_queue = queue.Queue(maxsize=10)
        
        # Stream
        self.stream = None
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
    def load_file(self, file_path: str):
        """Load audio file for playback and analysis"""
        try:
            file_path = Path(file_path)
            
            # Load audio using librosa for analysis
            self.logger.info(f"Loading audio file: {file_path}")
            
            # Try multiple loading methods
            try:
                # Method 1: Try librosa (works for most formats)
                self.audio_data, self.sample_rate = librosa.load(str(file_path), sr=None, mono=True)
                self.logger.info(f"Loaded with librosa: {len(self.audio_data)} samples at {self.sample_rate}Hz")
            except Exception as e1:
                self.logger.warning(f"Librosa failed: {e1}, trying soundfile...")
                try:
                    # Method 2: Try soundfile for WAV/FLAC
                    self.audio_data, self.sample_rate = sf.read(str(file_path), always_2d=False)
                    if len(self.audio_data.shape) > 1:
                        self.audio_data = np.mean(self.audio_data, axis=1)  # Convert to mono
                    self.logger.info(f"Loaded with soundfile: {len(self.audio_data)} samples at {self.sample_rate}Hz")
                except Exception as e2:
                    self.logger.warning(f"Soundfile failed: {e2}, trying pydub...")
                    # Method 3: Try pydub with audioread backend
                    try:
                        import audioread
                        with audioread.audio_open(str(file_path)) as f:
                            self.sample_rate = f.samplerate
                            audio_data = []
                            for buf in f:
                                audio_data.append(np.frombuffer(buf, dtype=np.int16))
                            self.audio_data = np.concatenate(audio_data).astype(np.float32) / 32768.0
                            if f.channels > 1:
                                # Convert to mono
                                self.audio_data = self.audio_data.reshape(-1, f.channels).mean(axis=1)
                        self.logger.info(f"Loaded with audioread: {len(self.audio_data)} samples at {self.sample_rate}Hz")
                    except Exception as e3:
                        self.logger.error(f"All loading methods failed: {e3}")
                        raise Exception(f"Unable to load audio file: {file_path}")
            
            # Reset position
            self.current_position = 0
            
            # Preprocess for visualization
            self._preprocess_audio()
            
            self.logger.info(f"Audio loaded successfully: {len(self.audio_data)} samples at {self.sample_rate}Hz")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading audio file: {e}")
            return False
    
    def _preprocess_audio(self):
        """Preprocess audio for visualization"""
        if self.audio_data is None:
            return
        
        # Apply normalization
        max_val = np.max(np.abs(self.audio_data))
        if max_val > 0:
            self.audio_data = self.audio_data / max_val
        
        # Create frequency bands for visualization
        self.frequency_bands = self._create_frequency_bands()
    
    def _create_frequency_bands(self):
        """Create logarithmic frequency bands for visualization"""
        # Define frequency bands (in Hz)
        bands = [
            (20, 60),      # Sub-bass
            (60, 250),     # Bass
            (250, 500),    # Low midrange
            (500, 2000),   # Midrange
            (2000, 4000),  # Upper midrange
            (4000, 6000),  # Presence
            (6000, 20000)  # Brilliance
        ]
        return bands
    
    def play(self):
        """Start audio playback"""
        if self.audio_data is None:
            return
        
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            return
        
        self.is_playing = True
        self.is_paused = False
        
        # Create output stream
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self._audio_callback,
            blocksize=self.block_size,
            finished_callback=self._playback_finished
        )
        self.stream.start()
        
    def pause(self):
        """Pause audio playback"""
        self.is_paused = True
        self.is_playing = False
    
    def stop(self):
        """Stop audio playback"""
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def _audio_callback(self, outdata, frames, time, status):
        """Audio stream callback for playback"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        
        if not self.is_playing or self.is_paused or self.audio_data is None:
            outdata[:] = 0
            return
        
        # Calculate how many frames to read
        end_position = min(self.current_position + frames, len(self.audio_data))
        chunk_size = end_position - self.current_position
        
        if chunk_size > 0:
            # Get audio chunk
            audio_chunk = self.audio_data[self.current_position:end_position]
            
            # Apply volume
            audio_chunk = audio_chunk * self.volume
            
            # Fill output buffer
            outdata[:chunk_size, 0] = audio_chunk
            
            # Zero-fill any remaining frames
            if chunk_size < frames:
                outdata[chunk_size:] = 0
                self.is_playing = False  # End of file
            
            # Update position
            self.current_position = end_position
            
            # Store chunk for visualization
            self._update_visualization_data(audio_chunk)
        else:
            outdata[:] = 0
            self.is_playing = False
    
    def _update_visualization_data(self, audio_chunk):
        """Update data for visualization"""
        if len(audio_chunk) < self.block_size:
            audio_chunk = np.pad(audio_chunk, (0, self.block_size - len(audio_chunk)))
        
        # Compute FFT for spectrum visualization
        window = signal.windows.hann(len(audio_chunk))
        windowed = audio_chunk * window
        self.fft_data = np.fft.rfft(windowed)
        
        # Detect beats (simple onset detection)
        rms = np.sqrt(np.mean(audio_chunk**2))
        self.beat_detected = rms > 0.3  # Simple threshold
    
    def _playback_finished(self):
        """Called when playback finishes"""
        self.logger.info("Playback finished")
        self.is_playing = False
        self.current_position = 0
    
    def set_volume(self, volume: float):
        """Set playback volume (0.0 to 1.0)"""
        self.volume = np.clip(volume, 0.0, 1.0)
    
    def seek(self, position: float):
        """Seek to position in audio (0.0 to 1.0)"""
        if self.audio_data is not None:
            self.current_position = int(position * len(self.audio_data))
    
    def get_current_time(self) -> float:
        """Get current playback time in seconds"""
        if self.sample_rate > 0:
            return self.current_position / self.sample_rate
        return 0.0
    
    def get_total_time(self) -> float:
        """Get total audio duration in seconds"""
        if self.audio_data is not None and self.sample_rate > 0:
            return len(self.audio_data) / self.sample_rate
        return 0.0
    
    def get_spectrum_data(self, num_bands: int = 32) -> np.ndarray:
        """Get current spectrum data for visualization"""
        if self.fft_data is None:
            return np.zeros(num_bands)
        
        # Convert FFT to magnitude spectrum
        magnitude = np.abs(self.fft_data)
        
        # Create logarithmic bands
        freq_bins = len(magnitude)
        band_limits = np.logspace(np.log10(1), np.log10(freq_bins), num_bands + 1, dtype=int)
        
        # Average magnitude in each band
        bands = np.zeros(num_bands)
        for i in range(num_bands):
            start = band_limits[i]
            end = band_limits[i + 1]
            if start < len(magnitude):
                bands[i] = np.mean(magnitude[start:min(end, len(magnitude))])
        
        # Normalize and apply logarithmic scaling
        bands = np.log10(bands + 1e-10) * 20  # Convert to dB
        bands = np.clip(bands + 60, 0, 60) / 60  # Normalize to 0-1
        
        return bands
    
    def get_waveform_data(self, num_points: int = 256) -> np.ndarray:
        """Get current waveform data for visualization"""
        if self.audio_data is None or not self.is_playing:
            return np.zeros(num_points)
        
        # Get a window of audio around current position
        start = max(0, self.current_position - num_points // 2)
        end = min(len(self.audio_data), start + num_points)
        
        waveform = self.audio_data[start:end]
        
        # Resample if needed
        if len(waveform) != num_points:
            indices = np.linspace(0, len(waveform) - 1, num_points).astype(int)
            waveform = waveform[indices]
        
        return waveform
    
    def is_beat(self) -> bool:
        """Check if a beat was detected"""
        return self.beat_detected
    
    def get_rms(self) -> float:
        """Get current RMS level"""
        if self.audio_data is None or not self.is_playing:
            return 0.0
        
        # Get current chunk
        start = self.current_position
        end = min(start + self.block_size, len(self.audio_data))
        
        if start < end:
            chunk = self.audio_data[start:end]
            return np.sqrt(np.mean(chunk**2))
        
        return 0.0
