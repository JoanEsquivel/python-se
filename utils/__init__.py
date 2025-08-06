"""
Modern Selenium utilities with ARIA role locators

This package automatically enables driver.find_element_by_role() and 
driver.find_elements_by_role() methods on all WebDriver instances.

Usage:
    import utils
    
    # Then use directly on driver
    element = driver.find_element_by_role("button", name="Submit")
    elements = driver.find_elements_by_role("textbox")
"""

from .aria_locators import ARIARole, LocatorConfig
from .webdriver_extensions import install_aria_methods, uninstall_aria_methods

# Auto-install methods on WebDriver when utils is imported
# This happens automatically, no manual setup required

__all__ = [
    'ARIARole',
    'LocatorConfig', 
    'install_aria_methods',
    'uninstall_aria_methods'
]