"""
Monkey patch WebDriver to add my custom ARIA role methods.
Probably not the cleanest way to do this but it works!
"""

from typing import List, Union, Optional, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .aria_locators import ARIARoleLocator, ARIARole


def find_element_by_role(self, role, name=None, **filters):
    """Find element by ARIA role - like find_element_by_id but for accessibility"""
    locator = ARIARoleLocator(self)
    return locator.find_element(role, name=name, **filters)


def find_elements_by_role(self, role, name=None, **filters):
    """Find multiple elements by ARIA role"""
    locator = ARIARoleLocator(self)
    return locator.find_elements(role, name=name, **filters)


def install_aria_methods():
    """Monkey patch WebDriver with my role finder methods"""
    WebDriver.find_element_by_role = find_element_by_role
    WebDriver.find_elements_by_role = find_elements_by_role
    print("✅ ARIA role methods installed on WebDriver")


def uninstall_aria_methods():
    """
    Remove ARIA role finder methods from WebDriver class.
    Call this if you need to clean up (optional).
    """
    if hasattr(WebDriver, 'find_element_by_role'):
        delattr(WebDriver, 'find_element_by_role')
    if hasattr(WebDriver, 'find_elements_by_role'):
        delattr(WebDriver, 'find_elements_by_role')
    
    print("🗑️ ARIA role methods removed from WebDriver")


# Auto-install when imported - couldn't figure out a cleaner way to do this
install_aria_methods()