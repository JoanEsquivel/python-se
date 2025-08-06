"""
Test ARIA role locators using the modern driver.find_element_by_role() syntax
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import utils to enable the new driver.find_element_by_role() syntax
import utils
from utils import ARIARole


class TestLoginPage:
    """Test login functionality using modern ARIA role locators"""
    
    def test_login_using_single_element_lookup(self, driver):
        """Test login flow using driver.find_element_by_role() - clean and direct"""
        driver.get("https://v0-imagine-deals.vercel.app")
        
        # Modern syntax - clean and natural
        username_input = driver.find_element_by_role("textbox", name="Username")
        username_input.send_keys("test_user")
        
        password_input = driver.find_element_by_role("textbox", name="Password")
        password_input.send_keys("test_pass")

        # Test button interaction on different page
        driver.get('https://www.w3.org/WAI/ARIA/apg/patterns/button/examples/button/')

        # Find and click the Mute toggle button
        mute_button = driver.find_element_by_role("button", name="Mute")
        mute_button.click()
        
    def test_login_using_multiple_elements_lookup(self, driver):
        """Test using driver.find_elements_by_role() - when you need to find multiple elements"""
        driver.get("https://v0-imagine-deals.vercel.app")
        
        # Find all textboxes on the page
        textbox_elements = driver.find_elements_by_role("textbox")
        assert len(textbox_elements) >= 2, "Should find at least username and password fields"
        
        # Find specific textboxes by name
        username_elements = driver.find_elements_by_role("textbox", name="Username")
        password_elements = driver.find_elements_by_role("textbox", name="Password")
        
        assert len(username_elements) == 1, "Should find exactly one username field"
        assert len(password_elements) == 1, "Should find exactly one password field"
        
        # Use the elements
        username_elements[0].send_keys("test_user")
        password_elements[0].send_keys("test_pass")

        # Test multiple buttons
        driver.get('https://www.w3.org/WAI/ARIA/apg/patterns/button/examples/button/')

        # Find all buttons and verify count
        all_buttons = driver.find_elements_by_role("button")
        print(f"Found {len(all_buttons)} buttons on the page")
        assert len(all_buttons) >= 2, "Expected multiple buttons on the page"
        
        # Find specific button and click it
        mute_buttons = driver.find_elements_by_role("button", name="Mute")
        assert len(mute_buttons) == 1, "Should find exactly one Mute button"
        mute_buttons[0].click()

    def test_using_aria_role_enums(self, driver):
        """Test using ARIARole enums for type safety"""
        driver.get("https://v0-imagine-deals.vercel.app")
        
        # Using enums for better type safety and IDE support
        username_input = driver.find_element_by_role(ARIARole.TEXTBOX, name="Username")
        username_input.send_keys("test_user")
        
        password_input = driver.find_element_by_role(ARIARole.TEXTBOX, name="Password")
        password_input.send_keys("test_pass")

        # Test with button enum
        driver.get('https://www.w3.org/WAI/ARIA/apg/patterns/button/examples/button/')

        # Find all buttons using enum
        all_buttons = driver.find_elements_by_role(ARIARole.BUTTON)
        assert len(all_buttons) >= 2, "Expected multiple buttons"
        
        # Find specific button using enum
        mute_button = driver.find_element_by_role(ARIARole.BUTTON, name="Mute")
        mute_button.click()