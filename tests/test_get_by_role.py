import pytest
from selenium.webdriver.common.by import By
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import find_elements_by_role, find_element_by_role


class TestLoginPage:
    def test_login_using_singular_function(self, driver):
        """Test using find_element_by_role (singular) - cleaner and more direct"""
        driver.get("https://v0-imagine-deals.vercel.app")
        
        # Find and fill username field (using singular function)
        username_input = find_element_by_role(driver, "textbox", name="Username")
        username_input.send_keys("test_user")
        
        # Find and fill password field (using singular function)
        password_input = find_element_by_role(driver, "textbox", name="Password")
        password_input.send_keys("test_pass")

        driver.get('https://www.w3.org/WAI/ARIA/apg/patterns/button/examples/button/')

        # Find and click the Mute toggle button (using singular function)
        mute_button = find_element_by_role(driver, "button", name="Mute")
        mute_button.click()

    def test_login_using_plural_function(self, driver):
        """Test using find_elements_by_role (plural) - more explicit about multiple elements"""
        driver.get("https://v0-imagine-deals.vercel.app")
        
        # Find and fill username field (using plural function)
        username_elements = find_elements_by_role(driver, "textbox", name="Username")
        assert len(username_elements) > 0, "No input elements with name 'Username' found"
        username_input = username_elements[0]  # Get the first matching element
        username_input.send_keys("test_user")
        
        # Find and fill password field (using plural function)
        password_elements = find_elements_by_role(driver, "textbox", name="Password")
        assert len(password_elements) > 0, "No input elements with name 'Password' found"
        password_input = password_elements[0]  # Get the first matching element
        password_input.send_keys("test_pass")

        driver.get('https://www.w3.org/WAI/ARIA/apg/patterns/button/examples/button/')

        # Find and click the Mute toggle button (using plural function)
        button_elements = find_elements_by_role(driver, "button", name="Mute")
        assert len(button_elements) > 0, "No button elements with name 'Mute' found"
        mute_button = button_elements[0]  # Get the first matching element
        mute_button.click()
        
        # Additional verification: check how many buttons exist on the page
        all_buttons = find_elements_by_role(driver, "button")
        print(f"DEBUG: Found {len(all_buttons)} total buttons on the page")
        
        # Verify we can find multiple elements of the same type
        assert len(all_buttons) >= 2, "Expected at least 2 buttons on the page"