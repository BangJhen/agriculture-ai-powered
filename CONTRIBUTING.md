# 🤝 Contributing Guide

**Quick start for new contributors to the Indonesian Agricultural Chatbot project.**

## 🚀 Getting Started (5 minutes)

```bash
# 1. Fork & clone
git clone https://github.com/yourusername/indonesian-agricultural-chatbot.git
cd indonesian-agricultural-chatbot

# 2. Setup environment
pip install -r requirements.txt
cp .env.example .env
# Add your OpenRouter API key to .env

# 3. Test everything works
python tests/test_chatbot.py
./launch.sh
```

## 📋 Before You Start

- [ ] Read the [README.md](README.md) for project overview
- [ ] Setup your API key using [API_SETUP.md](API_SETUP.md)
- [ ] Check [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed workflow
- [ ] Run tests to ensure everything works

## 🛠️ Making Changes

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Edit code in `agricultural_chatbot.py`
- Add tests in `tests/`
- Update docs if needed

### 3. Test Your Changes
```bash
# Test functionality
python tests/test_chatbot.py

# Test Indonesian features
python tests/test_indonesia.py

# Test the app
./launch.sh
```

### 4. Commit & Push
```bash
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
```

### 5. Create Pull Request
- Describe what you changed
- Include any relevant screenshots
- Link to any related issues

## 📁 Key Files to Know

| File | Purpose |
|------|---------|
| `agricultural_chatbot.py` | Main application code |
| `tests/test_chatbot.py` | Main test suite |
| `requirements.txt` | Python dependencies |
| `.env.example` | API key template |
| `docs/` | User documentation |

## 🧪 Testing Guidelines

Always test before submitting:
- [ ] `python tests/test_chatbot.py` passes
- [ ] App starts without errors
- [ ] Your feature works as expected
- [ ] Existing features still work

## 📝 Documentation

If you add new features:
- Update `README.md` if it affects quick start
- Add to `docs/README.md` for user-facing features
- Comment your code clearly
- Update relevant markdown files

## ❓ Need Help?

- **General questions**: Open an issue
- **Setup problems**: Check [API_SETUP.md](API_SETUP.md)
- **Development questions**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **All docs**: [DOCS_INDEX.md](DOCS_INDEX.md)

## 🎯 What We're Looking For

- 🌾 **Agricultural expertise** - Indonesian farming knowledge
- 🔧 **Technical improvements** - Better code, performance, features
- 📚 **Documentation** - Clear guides and examples
- 🧪 **Testing** - More comprehensive test coverage
- 🌍 **Localization** - Better Indonesian language support

## 🏆 Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes for significant contributions
- Project documentation

---

**Ready to contribute?** Jump to [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed instructions!
