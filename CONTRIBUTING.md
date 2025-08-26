# Contributing to Warp-Opus Projects

Thank you for your interest in contributing to Warp-Opus projects! This document provides guidelines and instructions for contributing.

## 🎯 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect different viewpoints and experiences

## 🚀 Getting Started

1. **Fork the Repository**
   ```bash
   git clone https://github.com/voidfnc/warp-opus.git
   cd warp-opus
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Write clean, readable code
   - Follow the existing code style
   - Add comments where necessary

4. **Test Your Changes**
   ```bash
   cd opus-one
   python main.py
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of changes"
   ```

6. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Pull Request Guidelines

### PR Title Format
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for updates to existing features
- `Remove:` for removing features
- `Docs:` for documentation changes

### PR Description Should Include
- What changes were made
- Why these changes were necessary
- How to test the changes
- Screenshots (if UI changes)

## 🎨 Code Style Guidelines

### Python (Opus One)
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions small and focused

### Example
```python
def process_audio_data(self, data: np.ndarray) -> np.ndarray:
    """
    Process raw audio data for visualization.
    
    Args:
        data: Raw audio samples as numpy array
        
    Returns:
        Processed audio data ready for visualization
    """
    # Implementation here
    pass
```

## 🐛 Reporting Issues

### Before Creating an Issue
- Check if the issue already exists
- Try to reproduce the issue
- Collect relevant information (OS, Python version, error messages)

### Issue Template
```markdown
**Description:**
Brief description of the issue

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: Windows 11
- Python: 3.11.x
- PyQt6: 6.5.x
```

## 🎯 Areas for Contribution

### Opus One - Priority Areas
- [ ] New visualizer modes
- [ ] Performance optimizations
- [ ] UI/UX improvements
- [ ] Audio format support
- [ ] Cross-platform testing
- [ ] Documentation
- [ ] Unit tests

### Feature Ideas Welcome
- 3D visualizations
- Audio effects/filters
- Playlist support
- Theme customization
- Plugin system

## 📚 Documentation

When adding new features, please:
- Update the README if needed
- Add inline comments
- Update docstrings
- Include usage examples

## 🧪 Testing

### Running Tests
```bash
pytest tests/
```

### Writing Tests
- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test names

## 💡 Tips for Contributors

1. **Start Small**: Begin with small bug fixes or documentation improvements
2. **Ask Questions**: Don't hesitate to ask for help in issues or discussions
3. **Stay Updated**: Pull latest changes before starting work
4. **One Feature Per PR**: Keep PRs focused on a single feature/fix

## 📬 Contact

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas
- **Discord**: [Join our server](https://discord.gg/warp-opus)

## 🙏 Recognition

Contributors will be added to the README and given credit for their work.

---

Thank you for contributing to Warp-Opus projects! 🎉
