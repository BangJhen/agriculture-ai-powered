# 🚀 Developer Guide

## Project Organization

This project follows a clean, organized structure to make development easier:

### 📁 Directory Structure

- **Root Level**: Main application files and configuration
- **`docs/`**: All documentation (user guides, technical docs)
- **`tests/`**: Test files and verification scripts
- **`scripts/`**: Utility scripts for running and deploying
- **`logs/`**: Runtime logs (auto-generated)
- **`assets/`**: Images, screenshots, and media files
- **`legacy/`**: Old versions and archived files

### 🔧 Development Workflow

1. **Setup Environment**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Tests Before Changes**
   ```bash
   python tests/test_chatbot.py
   ```

3. **Make Your Changes**
   - Main logic: `agricultural_chatbot.py`
   - Tests: Add to `tests/`
   - Documentation: Update in `docs/`

4. **Test Your Changes**
   ```bash
   python tests/test_chatbot.py
   python tests/verify_fix.py
   ```

5. **Update Documentation**
   - Update `docs/README.md` for user-facing changes
   - Update `docs/DOKUMENTASI_INDONESIA.md` for technical changes

### 🧪 Testing Guidelines

- **`test_chatbot.py`**: Comprehensive functionality tests
- **`test_indonesia.py`**: Indonesian-specific features
- **`verify_fix.py`**: Bug fix verification

Always run tests before committing:
```bash
# Quick test
python tests/test_chatbot.py

# Full test suite
python tests/test_chatbot.py && python tests/test_indonesia.py
```

### 📝 Code Organization Rules

1. **Keep it Clean**: No temporary files in root directory
2. **Categorize**: Put files in appropriate subdirectories
3. **Document**: Update docs when adding features
4. **Test**: Add tests for new functionality

### 🚀 Deployment

Use the launch scripts:
```bash
# Development
./scripts/launch_chatbot.sh

# Alternative launcher
./scripts/start_chatbot.sh
```

### 🔍 Debugging

- Check logs in `logs/` directory
- Use `verify_fix.py` for specific issue diagnosis
- Test individual components with specific test files

### 📚 Key Files to Know

- **`agricultural_chatbot.py`**: Main application
- **`requirements.txt`**: Dependencies
- **`docs/README.md`**: User documentation
- **`tests/test_chatbot.py`**: Main test suite

### 🎯 Adding New Features

1. Add the feature to `agricultural_chatbot.py`
2. Create tests in `tests/`
3. Update documentation in `docs/`
4. Test thoroughly before committing

This organization makes the project much easier to navigate and maintain! 🌾
