# ARIA Role Locators for Selenium

A clean Python implementation that brings Playwright's `getByRole()` functionality to Selenium WebDriver.

## Project Structure

```
utils/
├── __init__.py           # Main exports
└── aria_locators.py      # Core implementation
tests/
├── test_get_by_role.py   # Your main tests
└── test_professional_locators.py  # Additional test patterns
```

## Features

- **🎯 Type-Safe**: Full type hints and enum-based role definitions
- **🔄 Hybrid Approach**: Accessibility tree traversal with DOM fallback
- **⚡ Performance**: Configurable behavior and efficient element resolution
- **🛡️ Error Handling**: Comprehensive error handling with descriptive messages
- **📝 W3C Compliant**: Follows W3C accessible name computation specification
- **🔧 Configurable**: Flexible configuration for different use cases

## Quick Start

```python
from selenium import webdriver
from page_locators import find_element_by_role, ARIARole

driver = webdriver.Chrome()
driver.get("https://example.com")

# Simple usage with convenience functions
username = find_element_by_role(driver, "textbox", name="Username")
username.send_keys("user@example.com")

button = find_element_by_role(driver, ARIARole.BUTTON, name="Submit")
button.click()
```

## Advanced Usage

### Using the Locator Class

```python
from page_locators import ARIARoleLocator, ARIARole, LocatorConfig

# Configure the locator
config = LocatorConfig(
    use_accessibility_tree=True,
    fallback_to_dom=True,
    debug_mode=False
)

locator = ARIARoleLocator(driver, config)

# Find single element
submit_button = locator.find_element(ARIARole.BUTTON, name="Submit")

# Find multiple elements
all_textboxes = locator.find_elements(ARIARole.TEXTBOX)
```

### Supported Roles

```python
from page_locators import ARIARole

# All supported ARIA roles as type-safe enums
ARIARole.TEXTBOX     # Input fields, textareas
ARIARole.BUTTON      # Buttons and button-like elements
ARIARole.CHECKBOX    # Checkboxes
ARIARole.RADIO       # Radio buttons
ARIARole.LINK        # Links
ARIARole.HEADING     # Headings (h1-h6)
ARIARole.LISTITEM    # List items
ARIARole.LIST        # Lists
```

### Configuration Options

```python
from page_locators import LocatorConfig

config = LocatorConfig(
    use_accessibility_tree=True,    # Try accessibility tree first
    fallback_to_dom=True,           # Fallback to DOM if tree fails
    timeout_seconds=10.0,           # Timeout for operations
    debug_mode=False                # Enable debug logging
)
```

## How It Works

### 1. Accessibility Tree (Primary Method)
Uses Chrome DevTools Protocol to traverse the accessibility tree, providing the most accurate ARIA role matching.

### 2. DOM Fallback (Secondary Method)
When accessibility tree fails or is disabled, falls back to CSS selectors with accessible name resolution.

### 3. Accessible Name Resolution
Follows W3C specification priority:
1. `aria-label`
2. `aria-labelledby`
3. Element text content (for buttons/links)
4. Associated `<label>` element
5. Parent `<label>` element
6. `placeholder` attribute
7. `title` attribute

## Error Handling

```python
from selenium.common.exceptions import NoSuchElementException
from page_locators import AccessibilityTreeError

try:
    button = find_element_by_role(driver, "button", name="Submit")
except NoSuchElementException as e:
    print(f"Element not found: {e}")
except AccessibilityTreeError as e:
    print(f"Accessibility tree error: {e}")
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/test_professional_locators.py -v

# Run specific test class
pytest tests/test_professional_locators.py::TestARIARoleLocators -v

# Run with debug output
pytest tests/test_professional_locators.py -v -s
```

## Performance Considerations

- **Reuse Locator Instances**: Create one `ARIARoleLocator` instance per page
- **Configure Appropriately**: Disable accessibility tree if not needed
- **Use Type-Safe Enums**: Better IDE support and performance

## Comparison with Playwright

| Feature | Playwright | This Implementation |
|---------|------------|-------------------|
| Role-based selection | ✅ | ✅ |
| Accessible name | ✅ | ✅ |
| Type safety | ✅ | ✅ |
| Error messages | ✅ | ✅ |
| Configuration | ✅ | ✅ |
| DOM fallback | ✅ | ✅ |

## Requirements

- Python 3.8+
- Selenium WebDriver 4.0+
- Chrome/Chromium browser (for accessibility tree)

## Best Practices

1. **Use Type-Safe Enums**: Prefer `ARIARole.BUTTON` over `"button"`
2. **Configure Once**: Create locator config at test setup
3. **Handle Errors**: Always wrap in try-catch for production code
4. **Reuse Instances**: Don't create new locators for each element
5. **Test Both Methods**: Verify both accessibility tree and DOM fallback work

## Contributing

This implementation follows professional Python standards:
- Full type hints
- Comprehensive error handling
- Extensive documentation
- Configurable behavior
- Professional test patterns

## License

MIT License - Feel free to use in your projects.