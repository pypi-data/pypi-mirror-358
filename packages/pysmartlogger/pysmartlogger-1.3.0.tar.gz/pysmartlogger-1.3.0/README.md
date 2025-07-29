<div align="center">
  <h1>🎨 SmartLogger</h1>
  <p><strong>Beautiful, colorful logging for Python with zero configuration</strong></p>
  
  [![PyPI version](https://badge.fury.io/py/pysmartlogger.svg)](https://badge.fury.io/py/pysmartlogger)
  [![Python versions](https://img.shields.io/pypi/pyversions/pysmartlogger.svg)](https://pypi.org/project/pysmartlogger/)
  [![Downloads](https://pepy.tech/badge/pysmartlogger)](https://pepy.tech/project/pysmartlogger)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
  
  <p>Transform your boring Python logs into beautiful, colorful masterpieces!</p>
</div>

---

## ✨ Why SmartLogger?

<div align="center">

### Transform Your Logs Instantly! 

![SmartLogger Before and After](https://raw.githubusercontent.com/DeepPythonist/smartlogger/master/image.png)

*Just one line of code transforms boring logs into beautiful, colorful masterpieces!*

</div>

**Before SmartLogger:**
```python
2024-01-06 10:30:45 - myapp - DEBUG - Processing user data...
2024-01-06 10:30:45 - myapp - INFO - User authenticated successfully
2024-01-06 10:30:45 - myapp - WARNING - API rate limit approaching
2024-01-06 10:30:45 - myapp - ERROR - Database connection failed
2024-01-06 10:30:45 - myapp - CRITICAL - System shutting down
```

**After SmartLogger:**
```python
import smartlogger.auto  # One line = Colorful logs! 🎨
```

Your logs instantly become beautiful and easy to read with distinctive colors for each level!

## 🚀 Features

<table>
<tr>
<td align="center" width="50%">

### 🎨 **Beautiful Colors**
Each log level gets its distinctive color:
- 🔵 **DEBUG** - Blue (development info)
- 🟢 **INFO** - Green (general info)  
- 🟡 **WARNING** - Yellow (potential issues)
- 🔴 **ERROR** - Red (actual errors)
- 🔥 **CRITICAL** - Bright Red + Bold (urgent!)

</td>
<td align="center" width="50%">

### ⚡ **Zero Configuration**
```python
import logging
import smartlogger.auto  # ← Right after logging!
```
No setup, no configuration files, no complex initialization. Just remember the import order!

</td>
</tr>
<tr>
<td align="center">

### 🖥️ **Universal Compatibility**
- ✅ **Windows** (CMD, PowerShell, Windows Terminal)
- ✅ **macOS** (Terminal, iTerm2)
- ✅ **Linux** (bash, zsh, fish)
- ✅ **IDEs** (VS Code, PyCharm, Jupyter)
- ✅ **Python 3.8+**

</td>
<td align="center">

### 🛡️ **Production Ready**
- 🚀 **Zero dependencies** - No external packages required
- ⚡ **Performance optimized** - Minimal overhead
- 🔒 **Safe** - Won't break existing logging code
- 🧠 **Smart detection** - Auto-detects color support

</td>
</tr>
</table>

## 📦 Installation

<div align="center">

### Choose your preferred method:

</div>

<table>
<tr>
<td align="center" width="50%">

### 🏎️ **Quick Install**
```bash
pip install pysmartlogger
```

</td>
<td align="center" width="50%">

### 🔧 **From Source**
```bash
git clone https://github.com/DeepPythonist/smartlogger.git
cd smartlogger
pip install .
```

</td>
</tr>
</table>

## 🚀 Quick Start

### 30-Second Setup

> ⚠️ **IMPORTANT: Import Order Matters!**  
> `smartlogger.auto` must be imported **immediately after** importing `logging` and **before** any logging configuration or usage.

```python
# 1. Import logging first
import logging

# 2. Import SmartLogger IMMEDIATELY after logging (THIS IS CRITICAL!)
import smartlogger.auto

# 3. Now configure your logging (BasicConfig, handlers, etc.)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 4. Your logs are now colorful! 🎨
logger.debug("🔍 Debug: Investigating user behavior")
logger.info("✅ Info: User login successful")
logger.warning("⚠️ Warning: API rate limit at 80%")
logger.error("❌ Error: Payment processing failed")
logger.critical("🚨 Critical: Database connection lost!")
```

<div align="center">

### ✅ Correct Import Order vs ❌ Wrong Import Order

</div>

<table>
<tr>
<td width="50%" align="center">

### ✅ **CORRECT** 
```python
import logging
import smartlogger.auto  # ← Right after logging!

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.info("✅ Colors work!")
```

</td>
<td width="50%" align="center">

### ❌ **WRONG**
```python
import logging
logging.basicConfig()  # ← Configuration before SmartLogger
import smartlogger.auto  # ← Too late!

logger = logging.getLogger(__name__)
logger.info("❌ No colors...")
```

</td>
</tr>
</table>

### Advanced Usage

<details>
<summary>🎛️ <strong>Custom Configuration</strong></summary>

```python
import logging
from smartlogger.core.formatter import ColorFormatter
from smartlogger.core.handler import ColorHandler

# Create a custom logger with SmartLogger
logger = logging.getLogger('my_custom_app')
logger.setLevel(logging.DEBUG)

# Use SmartLogger's handler and formatter
handler = ColorHandler()
formatter = ColorFormatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Your beautiful custom logs!
logger.info("🎨 Custom formatting with colors!")
```

</details>

<details>
<summary>🏢 <strong>Enterprise Integration</strong></summary>

```python
# ⚠️ Remember: Import order is critical!
import logging
import smartlogger.auto  # ← Must be imported before any logging configuration!

# Now configure your existing enterprise logging setup
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

# SmartLogger automatically enhances ALL your existing loggers!
logger = logging.getLogger('enterprise.module')
logger.info("🏢 Enterprise logging is now colorful!")
```

</details>

## 🎨 Color Palette

<div align="center">

| Log Level | Color | Visual | Use Case | Example |
|-----------|--------|---------|----------|---------|
| 🔵 **DEBUG** | Blue | `🔍` | Development & debugging | `"Processing user input: email@example.com"` |
| 🟢 **INFO** | Green | `ℹ️` | General information | `"User authenticated successfully"` |
| 🟡 **WARNING** | Yellow | `⚠️` | Potential issues | `"API rate limit approaching (80%)"` |
| 🔴 **ERROR** | Red | `❌` | Actual errors | `"Failed to connect to database"` |
| 🔥 **CRITICAL** | Bright Red + Bold | `🚨` | Urgent attention needed | `"System memory critically low!"` |

</div>

## 🌟 Real-world Examples

<details>
<summary>🚀 <strong>Web Application</strong></summary>

```python
import logging
import smartlogger.auto  # ← Immediately after logging import!
from flask import Flask

app = Flask(__name__)
logger = logging.getLogger('webapp')

@app.route('/users/<user_id>')
def get_user(user_id):
    logger.info(f"🔍 Fetching user data for ID: {user_id}")
    
    try:
        user = database.get_user(user_id)
        logger.info(f"✅ User found: {user.email}")
        return user.to_json()
    except UserNotFound:
        logger.warning(f"⚠️ User {user_id} not found in database")
        return {"error": "User not found"}, 404
    except DatabaseError as e:
        logger.error(f"❌ Database error: {e}")
        return {"error": "Internal server error"}, 500
```

</details>

<details>
<summary>🤖 <strong>Machine Learning Pipeline</strong></summary>

```python
import logging
import smartlogger.auto  # ← Import right after logging!

logger = logging.getLogger('ml_pipeline')

def train_model(dataset_path):
    logger.info(f"🚀 Starting model training with dataset: {dataset_path}")
    
    try:
        data = load_dataset(dataset_path)
        logger.info(f"📊 Dataset loaded: {len(data)} samples")
        
        if len(data) < 1000:
            logger.warning(f"⚠️ Small dataset detected ({len(data)} samples)")
        
        model = train_neural_network(data)
        accuracy = evaluate_model(model)
        
        if accuracy > 0.95:
            logger.info(f"🎯 Excellent model performance: {accuracy:.2%}")
        elif accuracy > 0.80:
            logger.warning(f"📈 Good model performance: {accuracy:.2%}")
        else:
            logger.error(f"📉 Poor model performance: {accuracy:.2%}")
            
    except Exception as e:
        logger.critical(f"🚨 Model training failed: {e}")
        raise
```

</details>

<details>
<summary>📊 <strong>Data Processing</strong></summary>

```python
import logging
import smartlogger.auto  # ← Critical: Import immediately after logging!
import pandas as pd

logger = logging.getLogger('data_processor')

def process_customer_data(file_path):
    logger.info(f"📁 Processing customer data from: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        logger.debug(f"🔍 Raw data shape: {df.shape}")
        
        # Data validation
        missing_data = df.isnull().sum().sum()
        if missing_data > 0:
            logger.warning(f"⚠️ Found {missing_data} missing values")
        
        # Process data
        cleaned_df = clean_data(df)
        logger.info(f"✅ Data cleaning completed: {cleaned_df.shape}")
        
        # Save results
        cleaned_df.to_csv('processed_data.csv')
        logger.info("💾 Processed data saved successfully")
        
    except FileNotFoundError:
        logger.error(f"❌ Data file not found: {file_path}")
    except pd.errors.EmptyDataError:
        logger.critical(f"🚨 Data file is empty: {file_path}")
```

</details>

## 🖥️ Compatibility Matrix

<div align="center">

### Tested and Verified ✅

</div>

<table>
<tr>
<td align="center" width="33%">

### 🐍 **Python Versions**
- ✅ Python 3.8
- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12

</td>
<td align="center" width="33%">

### 💻 **Operating Systems**
- ✅ **Windows 10/11**
- ✅ **macOS** (Intel & Apple Silicon)
- ✅ **Linux** (Ubuntu, CentOS, Alpine)
- ✅ **Docker** containers
- ✅ **Cloud** environments

</td>
<td align="center" width="33%">

### 🔧 **Development Tools**
- ✅ **VS Code** (+ extensions)
- ✅ **PyCharm** (Pro & Community)
- ✅ **Jupyter** Notebooks
- ✅ **Google Colab**
- ✅ **Terminal/CMD/PowerShell**

</td>
</tr>
</table>

### 🌐 Terminal Support

| Terminal | Windows | macOS | Linux | Notes |
|----------|---------|-------|-------|-------|
| **Windows Terminal** | ✅ | - | - | Full color support |
| **PowerShell** | ✅ | ✅ | ✅ | Core & 7+ |
| **Command Prompt** | ✅ | - | - | Windows 10+ |
| **iTerm2** | - | ✅ | - | Recommended for macOS |
| **Terminal.app** | - | ✅ | - | Built-in macOS terminal |
| **bash/zsh/fish** | ✅ | ✅ | ✅ | Universal support |

## 🔬 How It Works

<div align="center">

### The Magic Behind SmartLogger ✨

</div>

```python
import logging
import smartlogger.auto  # ← This triggers the magic! 🪄
# IMPORTANT: Must be imported right after logging and before any configuration!
```

<details>
<summary>🔧 <strong>Technical Implementation</strong></summary>

SmartLogger uses **intelligent monkey-patching** to enhance Python's logging module:

```python
# 1. 🕵️ Environment Detection
def detect_color_support():
    """Detects if the current environment supports ANSI colors"""
    # Checks terminal type, environment variables, IDE support
    return is_terminal_supports_color()

# 2. 🎨 Smart Color Application
def apply_colors(log_record):
    """Applies appropriate colors based on log level"""
    if not supports_colors:
        return original_format(log_record)
    
    color = get_color_for_level(log_record.levelname)
    return f"{color}{log_record.levelname}{RESET}"

# 3. 🔄 Safe Monkey-Patching
def patch_logging():
    """Safely patches logging without breaking existing code"""
    original_formatter = logging.Formatter
    logging.Formatter = EnhancedColorFormatter
    # Maintains 100% backward compatibility!
```

**Key Features:**
- 🔍 **Smart Detection**: Automatically detects color support
- 🛡️ **Safe Patching**: Won't break existing logging configurations  
- ⚡ **Performance**: Minimal overhead (~0.1ms per log message)
- 🔄 **Reversible**: Can be disabled at runtime if needed

</details>

<details>
<summary>🎯 <strong>Zero Dependencies Philosophy</strong></summary>

SmartLogger is built with **zero external dependencies** by design:

- 📦 **Pure Python**: Only uses standard library modules
- 🚀 **Fast Installation**: No compilation or external packages
- 🔒 **Secure**: No third-party code vulnerabilities
- 📱 **Lightweight**: Total package size < 50KB

```bash
# Compare installation times:
pip install some-logging-lib    # Downloads 20+ dependencies 😴
pip install pysmartlogger      # Just SmartLogger! ⚡
```

</details>

## 🤝 Contributing

We love contributions! SmartLogger is an open-source project and we welcome contributions of all kinds.

<details>
<summary>🚀 <strong>How to Contribute</strong></summary>

### Quick Start for Contributors

1. **🍴 Fork the repository**
   ```bash
   git clone https://github.com/DeepPythonist/smartlogger.git
   cd smartlogger
   ```

2. **🌟 Create a feature branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

3. **🧪 Run tests**
   ```bash
   python -m pytest tests/ -v
   python demo_smartlogger.py
   ```

4. **📝 Make your changes and commit**
   ```bash
   git add .
   git commit -m "✨ Add amazing new feature"
   ```

5. **🚀 Push and create PR**
   ```bash
   git push origin feature/amazing-new-feature
   # Then create a Pull Request on GitHub!
   ```

### 🎯 Areas We Need Help With

- 🌍 **Cross-platform testing** (especially Windows variations)
- 🎨 **New color schemes** and themes
- 📚 **Documentation** improvements
- 🐛 **Bug reports** and fixes
- 💡 **Feature suggestions**

### 📋 Development Guidelines

- ✅ **Code style**: We use `black` for formatting
- 🧪 **Testing**: Add tests for new features
- 📝 **Documentation**: Update README for new features
- 🔍 **Type hints**: Use type annotations where possible

</details>

## ⚠️ Common Mistakes

<div align="center">

### 🚫 Avoid These Import Order Mistakes!

</div>

<table>
<tr>
<td width="50%" align="center">

### ❌ **MISTAKE 1: Late Import**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Too late! SmartLogger can't patch existing config
import smartlogger.auto  
```
**Result:** No colors, plain text logging

</td>
<td width="50%" align="center">

### ❌ **MISTAKE 2: Missing logging import**
```python
# Missing: import logging
import smartlogger.auto

logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)
```
**Result:** Import error or unexpected behavior

</td>
</tr>
<tr>
<td align="center">

### ❌ **MISTAKE 3: Config Before Import**
```python
import logging

# Configuration happens first
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(handler)

import smartlogger.auto  # Too late!
```
**Result:** SmartLogger can't enhance existing loggers

</td>
<td align="center">

### ✅ **CORRECT WAY**
```python
import logging
import smartlogger.auto  # Perfect timing!

# All configuration after SmartLogger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("🎨 Beautiful colors!")
```
**Result:** Beautiful, colorful logs! 

</td>
</tr>
</table>

## ❓ FAQ

<details>
<summary><strong>Q: Why is import order important?</strong></summary>

**A:** SmartLogger uses monkey-patching to enhance Python's logging module. It must be imported **immediately after** `logging` and **before** any logging configuration to work properly:

```python
# ✅ CORRECT ORDER
import logging
import smartlogger.auto  # ← Must be here!
logging.basicConfig()   # ← Configuration after SmartLogger

# ❌ WRONG ORDER  
import logging
logging.basicConfig()   # ← Configuration before SmartLogger
import smartlogger.auto  # ← Too late! Colors won't work
```

</details>

<details>
<summary><strong>Q: Does SmartLogger affect performance?</strong></summary>

**A:** Minimal impact! SmartLogger adds ~0.1ms overhead per log message. Color detection is cached, so there's virtually no performance penalty after initialization.

</details>

<details>
<summary><strong>Q: Can I use SmartLogger in production?</strong></summary>

**A:** Absolutely! SmartLogger is designed for production use:
- 🛡️ **Safe**: Won't break existing logging
- 🚀 **Zero dependencies**: No external vulnerabilities  
- ⚡ **Performance optimized**: Minimal overhead
- 🔄 **Reversible**: Can be disabled if needed

</details>

<details>
<summary><strong>Q: What if my terminal doesn't support colors?</strong></summary>

**A:** SmartLogger automatically detects color support and gracefully falls back to plain text in non-color environments. No configuration needed!

</details>

<details>
<summary><strong>Q: Can I customize the colors?</strong></summary>

**A:** Yes! You can customize colors using the advanced configuration:

```python
from smartlogger.config.colors import Colors

# Customize colors
Colors.INFO = Colors.CYAN  # Make INFO messages cyan
Colors.DEBUG = Colors.MAGENTA  # Make DEBUG messages magenta
```

</details>

<details>
<summary><strong>Q: Does it work with existing logging configurations?</strong></summary>

**A:** Yes! SmartLogger is designed to work seamlessly with existing logging setups. Just add `import smartlogger.auto` and your existing loggers become colorful.

</details>

## 📄 License

<div align="center">

**MIT License** - see [LICENSE](LICENSE) file for details.

*Feel free to use SmartLogger in your projects, both personal and commercial!*

</div>

## 👨‍💻 Author

<div align="center">
  <img src="https://github.com/DeepPythonist.png" width="100" height="100" style="border-radius: 50%;" alt="Mohammad Rasol Esfandiari">
  
  **Mohammad Rasol Esfandiari**
  
  🐍 *Python Developer & Open Source Enthusiast*
  
  [![GitHub](https://img.shields.io/badge/GitHub-DeepPythonist-black?style=social&logo=github)](https://github.com/DeepPythonist)
  [![Email](https://img.shields.io/badge/Email-mrasolesfandiari@gmail.com-red?style=social&logo=gmail)](mailto:mrasolesfandiari@gmail.com)

</div>

---

<div align="center">

### 🌟 If SmartLogger made your logging beautiful, please give it a star! 

[![GitHub stars](https://img.shields.io/github/stars/DeepPythonist/smartlogger.svg?style=social&label=Star)](https://github.com/DeepPythonist/smartlogger)

**Made with ❤️ for the Python community**

*Transform your logs from boring to beautiful in seconds!* 🎨

</div> 