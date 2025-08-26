# 🎵 Opus One - Audio Visualizer

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/PyQt6-6.5.0+-green.svg" alt="PyQt6">
  <img src="https://img.shields.io/badge/Status-Complete-success.svg" alt="Status">
</div>

> A stunning audio visualizer with real-time spectrum analysis and beautiful visual effects, built with Warp Terminal and Claude Opus 4.1.

## 🎯 Overview

Opus One is a modern audio visualizer that brings your music to life with mesmerizing visual effects. It features multiple visualization modes, real-time audio processing, and a sleek glassmorphic user interface.

### Key Features
- 🎨 **3 Visualization Modes**: Spectrum bars, circular display, and waveform oscilloscope
- 🎵 **Wide Format Support**: MP3, WAV, FLAC, M4A, OGG
- ⚡ **Real-time Processing**: FFT analysis with beat detection
- 💎 **Modern UI**: Glassmorphic design with smooth animations

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Windows 10/11, macOS 10.15+, or Linux

### Installation

```bash
# Clone the main repository
git clone https://github.com/voidfnc/warp-opus.git
cd warp-opus/opus-one

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📁 Project Structure

```
opus-one/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── src/
│   ├── ui/
│   │   ├── main_window.py    # Main window
│   │   └── title_bar.py      # Custom title bar
│   ├── visualizers/
│   │   ├── base_visualizer.py        # Base class
│   │   ├── spectrum_visualizer.py    # Bar spectrum
│   │   ├── circular_spectrum.py      # Radial display
│   │   └── waveform_visualizer.py    # Oscilloscope
│   └── audio/
│       └── simple_audio_engine.py    # Audio processing
```

## 🎮 Usage

### Controls
| Action | Method |
|--------|--------|
| Open File | Click "📁 Open File" or drag & drop |
| Play/Pause | Click play button or press `Space` |
| Switch Visualizer | Use arrow buttons |
| Adjust Volume | Use volume slider |

### Visualizers

#### Spectrum Analyzer
- 64 frequency bands
- Gradient coloring
- Beat-reactive animations

#### Circular Spectrum
- 360-degree visualization
- Rotating animations
- Particle effects

#### Waveform Oscilloscope
- Multiple render modes
- Trigger stabilization
- Persistence effects

## 🛠️ Technical Details

### Dependencies
- **PyQt6**: GUI framework
- **NumPy**: Numerical computing
- **SciPy**: Signal processing
- **PyAudio**: Audio I/O
- **PyDub**: Audio file handling

### Performance Optimizations
- Smart sampling for large waveforms
- Per-visualizer FPS control
- Efficient FFT processing
- Hardware-accelerated rendering

## 🐛 Troubleshooting

**Audio not playing?**
- Check PyAudio installation: `pip install --upgrade pyaudio`
- Verify audio output device settings

**Poor performance?**
- Switch to "Lines" mode in waveform visualizer
- Reduce window size
- Update graphics drivers

**MP3 not loading?**
- Install ffmpeg support: `pip install ffmpeg-python`

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

## 🙏 Credits

Built with [Warp Terminal](https://www.warp.dev/) and Claude Opus 4.1 AI assistant.

---

<div align="center">
  <b>Part of the <a href="https://github.com/voidfnc/warp-opus">Warp-Opus Projects</a></b><br>
  <i>Where AI meets Innovation</i>
</div>
