# Modern Selenium Testing Framework

A modern Selenium testing framework with natural ARIA role locators that work directly on WebDriver instances.

## 🚀 **Key Features**

- **Natural Syntax**: Use `driver.find_element_by_role()` directly (like native Selenium methods)
- **ARIA Role Support**: Find elements by accessibility roles (similar to Playwright's getByRole)
- **Multi-Browser**: Chrome, Firefox, Edge with headless support
- **Type Safety**: ARIARole enums for better IDE support
- **Zero Setup**: Auto-installs methods when you import utils

## 📦 **Installation**

```bash
# Clone the project
git clone <repository-url>
cd python-se

# Create virtual environment (recommended)
python -m venv se-python-env
source se-python-env/bin/activate  # On Windows: se-python-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 **Usage**

### Simple and Natural
```python
import utils  # That's it! Methods are now available on driver

# Find elements naturally
username = driver.find_element_by_role("textbox", name="Username")
submit_btn = driver.find_element_by_role("button", name="Submit")
all_buttons = driver.find_elements_by_role("button")
```

### With Type Safety
```python
from utils import ARIARole

# Use enums for better IDE support
username = driver.find_element_by_role(ARIARole.TEXTBOX, name="Username")
submit_btn = driver.find_element_by_role(ARIARole.BUTTON, name="Submit")
```

### Complete Example
```python
import pytest
import utils
from utils import ARIARole

class TestLogin:
    def test_login_flow(self, driver):
        driver.get("https://example.com/login")
        
        # Natural ARIA role locators
        username = driver.find_element_by_role("textbox", name="Username")
        password = driver.find_element_by_role("textbox", name="Password")
        login_btn = driver.find_element_by_role("button", name="Login")
        
        username.send_keys("user@example.com")
        password.send_keys("password123")
        login_btn.click()
        
        # Verify success
        assert "dashboard" in driver.current_url
```

## 🧪 **Running Tests**

```bash
# Run all tests with Chrome (default)
pytest tests/ --browser chrome

# Run with Firefox
pytest tests/ --browser firefox  

# Run with Edge
pytest tests/ --browser edge

# Run specific test
pytest tests/test_get_by_role.py -v

# Run with verbose output
pytest tests/ -v -s
```

## 🎭 **Supported ARIA Roles**

| Role | Description | Example |
|------|-------------|---------|
| `textbox` | Input fields, textareas | `driver.find_element_by_role("textbox", name="Email")` |
| `button` | Buttons, submit buttons | `driver.find_element_by_role("button", name="Login")` |
| `checkbox` | Checkboxes | `driver.find_element_by_role("checkbox", name="Remember me")` |
| `radio` | Radio buttons | `driver.find_element_by_role("radio", name="Male")` |
| `link` | Links | `driver.find_element_by_role("link", name="Home")` |
| `heading` | Headings (h1-h6) | `driver.find_element_by_role("heading", level=1)` |

## 🌐 **Browser Support**

| Browser | Headless | GUI | Status |
|---------|----------|-----|--------|
| Chrome | ✅ | ✅ | Fully Supported |
| Firefox | ✅ | ✅ | Fully Supported |
| Edge | ✅ | ✅ | Fully Supported |

## 🔧 **How It Works**

1. **Import utils**: Automatically installs `find_element_by_role()` and `find_elements_by_role()` methods on WebDriver
2. **ARIA Role Detection**: Uses Chrome DevTools Protocol to access accessibility tree
3. **DOM Fallback**: Falls back to CSS selectors with intelligent accessible name resolution
4. **Natural API**: Works just like native Selenium methods (`find_element_by_id`, `find_element_by_class_name`, etc.)

## ⚙️ **Requirements**

- Python 3.8+
- Selenium 4.6+
- pytest

All browser drivers are automatically managed by Selenium Manager - no manual setup required!

## 📁 **Project Structure**

```
python-se/
├── tests/
│   ├── conftest.py          # Pytest configuration and driver setup
│   ├── test_get_by_role.py  # Main ARIA locator tests
│   └── test_login_page.py   # Additional test examples
├── utils/
│   ├── __init__.py          # Package initialization
│   ├── aria_locators.py     # Core ARIA locator implementation
│   └── webdriver_extensions.py  # WebDriver method extensions
├── requirements.txt         # Project dependencies
└── readme.md               # This file
```

## 🎉 **Why Use This Framework?**

### ✅ **Advantages over traditional Selenium:**
- **More Accessible**: Find elements like users do (by role and name)
- **More Reliable**: Less brittle than ID/CSS selectors
- **More Readable**: Self-documenting test code
- **More Natural**: Same syntax pattern as native Selenium methods

### 📝 **Comparison:**
```python
# ❌ Traditional Selenium (brittle)
username = driver.find_element(By.ID, "username-field-id-that-might-change")
submit = driver.find_element(By.XPATH, "//button[@class='btn btn-primary submit-btn']")

# ✅ This Framework (robust)
username = driver.find_element_by_role("textbox", name="Username")
submit = driver.find_element_by_role("button", name="Submit")
```

## 🤝 **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 **License**

[MIT](https://choosealicense.com/licenses/mit/)