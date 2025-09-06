"""
WebDriver BiDi find_element_by_role implementation for SeleniumConf demo.

This module provides the main implementation logic that extends WebDriver
with find_element_by_role and find_elements_by_role methods using pure
WebDriver BiDi APIs.

Key features:
- Extends WebDriver with role-based element finding methods
- Uses only WebDriver BiDi (no CDP, no legacy protocols)
- Demonstrates against W3C ARIA button example page
- Production-ready, well-commented code for conference demo
"""

import logging
from typing import List, Optional, Union
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aria_locators import BiDiAccessibilityLocator, ARIARole, BiDiAccessibilityError

logger = logging.getLogger(__name__)


def find_element_by_role(
    driver: WebDriver,
    role: Union[ARIARole, str], 
    name: Optional[str] = None
) -> WebElement:
    """
    Find a single element by ARIA role using WebDriver BiDi.
    
    This function uses pure WebDriver BiDi accessibility locators to find
    elements by their ARIA role and optional accessible name.
    
    Args:
        driver: WebDriver instance with BiDi enabled
        role: ARIA role to search for (enum or string)
        name: Optional accessible name to match
        
    Returns:
        WebElement matching the criteria
        
    Example:
        # Find a button by role and name
        submit_btn = find_element_by_role(driver, ARIARole.BUTTON, name="Submit")
        submit_btn.click()
        
        # Find any textbox
        username_field = find_element_by_role(driver, "textbox", name="Username")
        username_field.send_keys("demo_user")
    """
    # Convert enum to string if needed
    role_str = role.value if isinstance(role, ARIARole) else role
    
    # Create BiDi locator and find element
    locator = BiDiAccessibilityLocator(driver)
    return locator.find_element_by_role(role_str, name)


def find_elements_by_role(
    driver: WebDriver,
    role: Union[ARIARole, str], 
    name: Optional[str] = None
) -> List[WebElement]:
    """
    Find multiple elements by ARIA role using WebDriver BiDi.
    
    This function uses pure WebDriver BiDi accessibility locators to find
    all elements matching the specified ARIA role and optional accessible name.
    
    Args:
        driver: WebDriver instance with BiDi enabled
        role: ARIA role to search for (enum or string)
        name: Optional accessible name to match
        
    Returns:
        List of WebElements matching the criteria
        
    Example:
        # Find all buttons on the page
        all_buttons = find_elements_by_role(driver, ARIARole.BUTTON)
        print(f"Found {len(all_buttons)} buttons")
        
        # Find all textboxes
        textboxes = find_elements_by_role(driver, "textbox")
        for textbox in textboxes:
            print(f"Textbox: {textbox.get_attribute('name')}")
    """
    # Convert enum to string if needed
    role_str = role.value if isinstance(role, ARIARole) else role
    
    # Create BiDi locator and find elements
    locator = BiDiAccessibilityLocator(driver)
    return locator.find_elements_by_role(role_str, name)


def install_role_methods(driver: WebDriver) -> None:
    """
    Install find_element_by_role and find_elements_by_role methods on WebDriver instance.
    
    This function dynamically adds the role-based finding methods to the WebDriver
    instance, allowing them to be called directly as driver methods.
    
    Args:
        driver: WebDriver instance to extend
        
    Example:
        driver = create_bidi_driver()
        install_role_methods(driver)
        
        # Now you can use the methods directly on the driver
        button = driver.find_element_by_role(ARIARole.BUTTON, name="Submit")
        buttons = driver.find_elements_by_role("button")
    """
    # Create bound methods that include the driver instance
    def bound_find_element_by_role(role: Union[ARIARole, str], name: Optional[str] = None) -> WebElement:
        return find_element_by_role(driver, role, name)
    
    def bound_find_elements_by_role(role: Union[ARIARole, str], name: Optional[str] = None) -> List[WebElement]:
        return find_elements_by_role(driver, role, name)
    
    # Install methods on the driver instance
    driver.find_element_by_role = bound_find_element_by_role
    driver.find_elements_by_role = bound_find_elements_by_role
    
    logger.debug("✅ Role-based finding methods installed on WebDriver instance")


def create_bidi_driver(headless: bool = False) -> WebDriver:
    """
    Create a Chrome WebDriver with BiDi enabled.
    
    This function creates a properly configured Chrome WebDriver instance
    with WebDriver BiDi capabilities enabled. This is required for the
    role-based element finding to work.
    
    Args:
        headless: Whether to run in headless mode (default: False for demo)
        
    Returns:
        Chrome WebDriver instance with BiDi enabled
        
    Example:
        # Create BiDi-enabled driver for demo
        driver = create_bidi_driver(headless=False)
        install_role_methods(driver)
        
        # Use the driver with role-based finding
        driver.get("https://example.com")
        button = driver.find_element_by_role("button", name="Click me")
    """
    # Configure Chrome options for BiDi
    options = Options()
    
    # Enable WebDriver BiDi using the same approach as conftest.py
    options.set_capability("webSocketUrl", True)
    
    # Additional BiDi-related options
    options.add_argument("--enable-bidi")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Set headless mode if requested
    if headless:
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    
    # Create driver with BiDi capabilities
    driver = Chrome(options=options)
    driver.implicitly_wait(10)
    
    # Install role-based finding methods
    install_role_methods(driver)
    
    logger.debug("✅ BiDi-enabled Chrome driver created and configured")
    return driver


def demo_w3c_aria_buttons(driver: WebDriver) -> None:
    """
    Demonstrate the BiDi role-based element finding against W3C ARIA button examples.
    
    This function runs the exact demo scenario described in the prompt,
    showing how to find and interact with buttons using ARIA roles.
    
    Args:
        driver: WebDriver instance with role methods installed
        
    Example:
        driver = create_bidi_driver()
        demo_w3c_aria_buttons(driver)
    """
    try:
        print("🚀 Starting W3C ARIA button demo...")
        
        # Navigate to W3C ARIA button example page
        print("📍 Navigating to W3C ARIA button examples...")
        driver.get('https://www.w3.org/WAI/ARIA/apg/patterns/button/examples/button/')
        
        # Find all buttons using enum
        print("🔍 Finding all buttons using ARIARole.BUTTON...")
        all_buttons = driver.find_elements_by_role(ARIARole.BUTTON)
        print(f"✅ Found {len(all_buttons)} buttons")
        assert len(all_buttons) >= 2, f"Expected multiple buttons, found {len(all_buttons)}"
        
        # List all found buttons
        print("\n📋 Button inventory:")
        for i, button in enumerate(all_buttons, 1):
            button_text = button.text or button.get_attribute('aria-label') or 'No text'
            print(f"  {i}. {button_text}")
        
        # Find specific button using enum
        print("\n🎯 Finding specific 'Mute' button...")
        try:
            mute_button = driver.find_element_by_role(ARIARole.BUTTON, name="Mute")
            print(f"✅ Found Mute button: {mute_button.text}")
            
            # Click the mute button
            print("🖱️ Clicking Mute button...")
            mute_button.click()
            print("✅ Mute button clicked successfully")
            
        except Exception as e:
            print(f"⚠️ Could not find/click Mute button: {e}")
            # Try to find any button and click it for demo purposes
            if all_buttons:
                print("🔄 Clicking first available button instead...")
                first_button = all_buttons[0]
                print(f"🖱️ Clicking: {first_button.text}")
                first_button.click()
                print("✅ Button clicked successfully")
        
        print("\n🎉 Demo completed successfully!")
        
    except BiDiAccessibilityError as e:
        print(f"❌ BiDi accessibility error: {e}")
        print("💡 Make sure you're using Selenium 4.15+ with BiDi enabled")
        raise
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    """
    Main demo script - run this to see the BiDi role-based element finding in action.
    
    This script demonstrates the complete workflow:
    1. Create BiDi-enabled WebDriver
    2. Install role-based finding methods
    3. Navigate to W3C ARIA examples
    4. Find and interact with elements by role
    """
    # Set up logging for demo
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    driver = None
    try:
        # Create BiDi-enabled driver
        print("🔧 Creating BiDi-enabled WebDriver...")
        driver = create_bidi_driver(headless=False)  # Keep visible for demo
        driver.maximize_window()
        # Run the demo
        demo_w3c_aria_buttons(driver)
        
        # Keep browser open for a moment to see results
        print("\n⏳ Keeping browser open for 5 seconds...")
        import time
        time.sleep(5)
        
    except Exception as e:
        print(f"💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("🧹 Cleaning up...")
            driver.quit()
            print("✅ Demo cleanup complete")
