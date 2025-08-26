# Changelog

All notable changes to the Warp-Opus projects will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Project Echo - TypeScript/React web application
- Project Nebula - Rust/Tauri desktop application
- Additional visualizers for Opus One
- GPU acceleration support

## [1.0.0] - 2025-08-26

### Opus One - Initial Release

#### Added
- **Core Features**
  - 3 visualization modes: Spectrum, Circular, and Waveform
  - Support for MP3, WAV, FLAC, M4A, and OGG audio formats
  - Real-time FFT spectrum analysis
  - Beat detection system
  - Smooth 30+ FPS rendering

- **Visualizers**
  - Spectrum Analyzer: 64-band frequency display with gradient colors
  - Circular Spectrum: 360-degree radial visualization with rotation
  - Waveform Oscilloscope: Multiple render modes (Lines, Dots, Filled, Bars, Mirror)

- **User Interface**
  - Modern glassmorphic design
  - Custom frameless window with title bar
  - Drag & drop file support
  - Audio controls (play, pause, seek, volume)
  - Visualizer switcher with smooth transitions

- **Audio Engine**
  - PyAudio-based real-time streaming
  - Automatic MP3 to WAV conversion
  - Seek functionality
  - Volume control

- **Performance Optimizations**
  - Smart sampling for large waveforms
  - Per-visualizer FPS control
  - Efficient FFT processing
  - Hardware-accelerated QPainter rendering

#### Fixed
- Title bar transparency issues
- Window maximize/restore functionality
- MP3 loading with automatic conversion
- Memory leaks in audio stream cleanup

#### Removed
- Matrix Rain visualizer (performance issues)

### Development Milestones

#### 2025-08-26
- Open-sourced on GitHub
- Created comprehensive documentation
- Set up repository structure for multiple projects

#### 2025-08-25
- Completed Opus One development
- Finalized three core visualizers
- Optimized performance

#### 2025-08-24
- Initial development with Warp Terminal and Claude Opus 4.1
- Created base architecture
- Implemented audio engine

## Version Numbering

- **Major (X.0.0)**: Breaking changes or major feature additions
- **Minor (0.X.0)**: New features, backwards compatible
- **Patch (0.0.X)**: Bug fixes and minor improvements

---

[Unreleased]: https://github.com/voidfnc/warp-opus/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/voidfnc/warp-opus/releases/tag/v1.0.0
