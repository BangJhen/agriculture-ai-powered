# 🚀 Developer Guide

## Project Organization

This project follows a clean, organized structure to make development easier:

### 📁 Directory Structure

- **Root Level**: Main application files and configuration
- **`docs/`**: All documentation (user guides, technical docs)
- **`scripts/`**: Utility scripts for running and deploying
- **`logs/`**: Runtime logs (auto-generated)
- **`assets/`**: Images, screenshots, and media files
- **`legacy/`**: Old versions and archived files

### 🔧 Development Workflow

1. **Setup Environment**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Setup Works**
   ```bash
   ./launch.sh
   ```

3. **Make Your Changes**
   - Main logic: `agricultural_chatbot.py`
   - Documentation: Update in `docs/`

4. **Verify Your Changes**
   ```bash
   ./launch.sh  # Test the application
   ```

5. **Update Documentation**
   - Update `docs/README.md` for user-facing changes
   - Update `docs/DOKUMENTASI_INDONESIA.md` for technical changes

### 📝 Code Organization Rules

1. **Keep it Clean**: No temporary files in root directory
2. **Categorize**: Put files in appropriate subdirectories
3. **Document**: Update docs when adding features
4. **Verify**: Test functionality through the Streamlit GUI
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

### 🎯 Adding New Features

1. Add the feature to `agricultural_chatbot.py`
2. Update documentation in `docs/`
3. Test thoroughly through the Streamlit GUI before committing

This organization makes the project much easier to navigate and maintain! 🌾
