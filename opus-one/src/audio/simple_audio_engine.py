"""
Simplified Audio Engine for Opus One Audio Visualizer
More robust with better error handling
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
import queue
from pathlib import Path
import logging
import traceback


class SimpleAudioEngine:
    """Simplified audio processing and playback engine"""
    
    def __init__(self, sample_rate=44100, block_size=1024):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.audio_data = None
        self.current_position = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        
        # Audio analysis buffers
        self.fft_data = None
        self.beat_detected = False
        
        # Stream
        self.stream = None
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
    def load_file(self, file_path: str):
        """Load audio file for playback - simplified version"""
        try:
            file_path = Path(file_path)
            self.logger.info(f"Loading audio file: {file_path}")
            
            # Stop any current playback
            self.stop()
            
            # For now, only use soundfile which is most reliable
            # Convert MP3 to WAV first if needed
            if file_path.suffix.lower() == '.mp3':
                self.logger.info("MP3 detected, attempting conversion...")
                # Try to load MP3 using a simple approach
                try:
                    import wave
                    import subprocess
                    import tempfile
                    
                    # Create temp WAV file
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                        temp_path = tmp_file.name
                    
                    # Find ffmpeg
                    ffmpeg_paths = [
                        Path("ffmpeg/ffmpeg.exe"),
                        Path("dist/OpusOne/ffmpeg/ffmpeg.exe"),
                        Path("C:/ffmpeg/bin/ffmpeg.exe"),
                    ]
                    
                    ffmpeg_exe = None
                    for path in ffmpeg_paths:
                        if path.exists():
                            ffmpeg_exe = str(path)
                            break
                    
                    if ffmpeg_exe:
                        # Convert MP3 to WAV using ffmpeg
                        cmd = [ffmpeg_exe, '-i', str(file_path), '-acodec', 'pcm_s16le', 
                               '-ar', '44100', '-ac', '1', '-y', temp_path]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            # Load the converted WAV
                            self.audio_data, self.sample_rate = sf.read(temp_path, always_2d=False)
                            Path(temp_path).unlink()  # Delete temp file
                        else:
                            raise Exception(f"FFmpeg conversion failed: {result.stderr}")
                    else:
                        raise Exception("FFmpeg not found for MP3 conversion")
                    
                except Exception as e:
                    self.logger.error(f"MP3 conversion failed: {e}")
                    # Fallback: try direct soundfile loading
                    self.audio_data, self.sample_rate = sf.read(str(file_path), always_2d=False)
            else:
                # Load WAV/FLAC directly
                self.audio_data, self.sample_rate = sf.read(str(file_path), always_2d=False)
            
            # Convert to mono if stereo
            if len(self.audio_data.shape) > 1:
                self.audio_data = np.mean(self.audio_data, axis=1)
            
            # Ensure float32
            if self.audio_data.dtype != np.float32:
                self.audio_data = self.audio_data.astype(np.float32)
            
            # Normalize
            max_val = np.max(np.abs(self.audio_data))
            if max_val > 0:
                self.audio_data = self.audio_data / max_val * 0.9
            
            # Reset position
            self.current_position = 0
            
            self.logger.info(f"Audio loaded: {len(self.audio_data)} samples at {self.sample_rate}Hz")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading audio file: {e}")
            self.logger.error(traceback.format_exc())
            self.audio_data = None
            return False
    
    def play(self):
        """Start audio playback"""
        if self.audio_data is None:
            self.logger.warning("No audio data to play")
            return
        
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            if self.stream:
                self.stream.start()
            return
        
        try:
            self.is_playing = True
            self.is_paused = False
            
            # Create output stream with error handling
            self.stream = sd.OutputStream(
                samplerate=int(self.sample_rate),
                channels=1,
                callback=self._audio_callback,
                blocksize=self.block_size,
                finished_callback=self._playback_finished
            )
            self.stream.start()
            self.logger.info("Playback started")
            
        except Exception as e:
            self.logger.error(f"Error starting playback: {e}")
            self.is_playing = False
    
    def pause(self):
        """Pause audio playback"""
        if self.stream and self.is_playing:
            self.is_paused = True
            self.is_playing = False
            self.stream.stop()
    
    def stop(self):
        """Stop audio playback"""
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0
        
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
            self.stream = None
    
    def _audio_callback(self, outdata, frames, time, status):
        """Audio stream callback for playback"""
        try:
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
                
                # Update visualization data (simplified)
                self._update_visualization_data(audio_chunk[:self.block_size])
            else:
                outdata[:] = 0
                self.is_playing = False
                
        except Exception as e:
            self.logger.error(f"Error in audio callback: {e}")
            outdata[:] = 0
    
    def _update_visualization_data(self, audio_chunk):
        """Update data for visualization"""
        try:
            if len(audio_chunk) < self.block_size:
                audio_chunk = np.pad(audio_chunk, (0, self.block_size - len(audio_chunk)))
            
            # Simple FFT for spectrum visualization
            self.fft_data = np.fft.rfft(audio_chunk * np.hanning(len(audio_chunk)))
            
            # Simple beat detection
            rms = np.sqrt(np.mean(audio_chunk**2))
            self.beat_detected = rms > 0.3
        except:
            pass
    
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
            # Ensure position is within bounds
            self.current_position = max(0, min(self.current_position, len(self.audio_data) - 1))
    
    def get_spectrum_data(self, num_bands: int = 32) -> np.ndarray:
        """Get current spectrum data for visualization"""
        if self.fft_data is None:
            return np.zeros(num_bands)
        
        try:
            # Convert FFT to magnitude spectrum
            magnitude = np.abs(self.fft_data)
            
            # Simple band averaging
            bands_per_bin = len(magnitude) // num_bands
            bands = np.zeros(num_bands)
            
            for i in range(num_bands):
                start = i * bands_per_bin
                end = start + bands_per_bin
                if start < len(magnitude):
                    bands[i] = np.mean(magnitude[start:min(end, len(magnitude))])
            
            # Simple normalization
            max_val = np.max(bands)
            if max_val > 0:
                bands = bands / max_val
            
            return bands
        except:
            return np.zeros(num_bands)
    
    def get_waveform_data(self, num_points: int = 256) -> np.ndarray:
        """Get current waveform data for visualization"""
        if self.audio_data is None or not self.is_playing:
            return np.zeros(num_points)
        
        try:
            # Get current chunk
            start = self.current_position
            end = min(start + num_points, len(self.audio_data))
            
            if end > start:
                waveform = self.audio_data[start:end]
                if len(waveform) < num_points:
                    waveform = np.pad(waveform, (0, num_points - len(waveform)))
                return waveform
            else:
                return np.zeros(num_points)
        except:
            return np.zeros(num_points)
    
    def is_beat(self) -> bool:
        """Check if a beat was detected"""
        return self.beat_detected
    
    def get_rms(self) -> float:
        """Get current RMS level"""
        try:
            if self.audio_data is None or not self.is_playing:
                return 0.0
            
            # Get current chunk
            start = self.current_position
            end = min(start + self.block_size, len(self.audio_data))
            
            if start < end:
                chunk = self.audio_data[start:end]
                return float(np.sqrt(np.mean(chunk**2)))
            
            return 0.0
        except:
            return 0.0
    
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
