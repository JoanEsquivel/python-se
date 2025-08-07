"""
WebDriver extensions to add ARIA role locator methods directly to WebDriver instances.
This enables usage like: driver.find_element_by_role("button", name="Submit")
"""

from typing import List, Union, Optional, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .aria_locators import ARIARoleLocator, ARIARole


def find_element_by_role(
    self, 
    role: Union[ARIARole, str], 
    name: Optional[str] = None,
    **filters: Any
) -> WebElement:
    """
    Find a single element by ARIA role.
    
    Args:
        role: The ARIA role to search for (e.g., 'button', 'textbox')
        name: The accessible name to match
        **filters: Additional ARIA properties
        
    Returns:
        First matching WebElement
        
    Example:
        button = driver.find_element_by_role("button", name="Submit")
        username = driver.find_element_by_role("textbox", name="Username")
    """
    locator = ARIARoleLocator(self)
    return locator.find_element(role, name=name, **filters)


def find_elements_by_role(
    self, 
    role: Union[ARIARole, str], 
    name: Optional[str] = None,
    **filters: Any
) -> List[WebElement]:
    """
    Find multiple elements by ARIA role.
    
    Args:
        role: The ARIA role to search for
        name: The accessible name to match
        **filters: Additional ARIA properties
        
    Returns:
        List of matching WebElements
        
    Example:
        buttons = driver.find_elements_by_role("button")
        textboxes = driver.find_elements_by_role("textbox")
    """
    locator = ARIARoleLocator(self)
    return locator.find_elements(role, name=name, **filters)


def install_aria_methods():
    """
    Install ARIA role finder methods into WebDriver class.
    Call this once at the beginning of your test suite.
    """
    # Add methods to WebDriver class
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


# Auto-install on import (you can disable this if you prefer manual control)
install_aria_methods()