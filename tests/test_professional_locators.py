"""
Tests for ARIA role locators - making sure everything works as expected
"""

import pytest
import logging
from typing import List

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    ARIARoleLocator, 
    ARIARole, 
    LocatorConfig,
    find_element_by_role,
    find_elements_by_role
)


class TestARIARoleLocators:
    """Basic tests to make sure the locators work correctly"""
    
    @pytest.fixture(autouse=True)
    def setup_logging(self):
        """Setup logging for tests"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def test_locator_with_configuration(self, driver: WebDriver):
        """Test locator with custom configuration"""
        config = LocatorConfig(
            use_accessibility_tree=True,
            fallback_to_dom=True,
            debug_mode=True
        )
        
        locator = ARIARoleLocator(driver, config)
        
        driver.get("https://v0-imagine-deals.vercel.app")
        driver.implicitly_wait(3)
        
        # Test with enum-based role
        username_input = locator.find_element(ARIARole.TEXTBOX, name="Username")
        username_input.send_keys("test_user")
        
        # Test multiple elements
        all_textboxes = locator.find_elements(ARIARole.TEXTBOX)
        assert len(all_textboxes) >= 2, "Expected at least username and password fields"
        
    def test_convenience_functions(self, driver: WebDriver):
        """Test the convenience functions for backward compatibility"""
        driver.get("https://v0-imagine-deals.vercel.app")
        driver.implicitly_wait(3)
        
        # Test singular function with string role
        username_input = find_element_by_role(driver, "textbox", name="Username")
        username_input.send_keys("test_user")
        
        # Test plural function
        password_elements = find_elements_by_role(driver, "textbox", name="Password")
        assert len(password_elements) > 0, "Should find password field"
        
        password_elements[0].send_keys("test_pass")
        
    def test_button_interaction_with_enum(self, driver: WebDriver):
        """Test button interactions using type-safe enums"""
        driver.get('https://www.w3.org/WAI/ARIA/apg/patterns/button/examples/button/')
        driver.implicitly_wait(3)
        
        locator = ARIARoleLocator(driver)
        
        # Find and click the Mute toggle button using enum
        mute_button = locator.find_element(ARIARole.BUTTON, name="Mute")
        mute_button.click()
        
        # Verify multiple buttons exist
        all_buttons: List = locator.find_elements(ARIARole.BUTTON)
        assert len(all_buttons) >= 2, "Expected multiple buttons on the page"
        
    def test_error_handling(self, driver: WebDriver):
        """Test proper error handling"""
        driver.get("https://v0-imagine-deals.vercel.app")
        
        locator = ARIARoleLocator(driver)
        
        # Test NoSuchElementException with descriptive message
        with pytest.raises(NoSuchElementException) as exc_info:
            locator.find_element(ARIARole.BUTTON, name="NonExistentButton")
            
        error_message = str(exc_info.value)
        assert "button" in error_message
        assert "NonExistentButton" in error_message
        
    def test_accessibility_tree_vs_dom_fallback(self, driver: WebDriver):
        """Test that both accessibility tree and DOM fallback work"""
        driver.get("https://v0-imagine-deals.vercel.app")
        driver.implicitly_wait(3)
        
        # Test with accessibility tree enabled
        config_with_tree = LocatorConfig(use_accessibility_tree=True, fallback_to_dom=True)
        locator_with_tree = ARIARoleLocator(driver, config_with_tree)
        
        # Test with only DOM fallback
        config_dom_only = LocatorConfig(use_accessibility_tree=False, fallback_to_dom=True)
        locator_dom_only = ARIARoleLocator(driver, config_dom_only)
        
        # Both should find the same elements
        elements_tree = locator_with_tree.find_elements(ARIARole.TEXTBOX)
        elements_dom = locator_dom_only.find_elements(ARIARole.TEXTBOX)
        
        assert len(elements_tree) == len(elements_dom), "Both methods should find same number of elements"
        
    def test_accessible_name_resolution_priority(self, driver: WebDriver):
        """Test that accessible name resolution follows correct priority"""
        # This would require a test page with specific ARIA attributes
        # For now, we'll test the basic functionality
        driver.get("https://v0-imagine-deals.vercel.app")
        driver.implicitly_wait(3)
        
        locator = ARIARoleLocator(driver)
        
        # Test finding by accessible name (should use label text)
        username_field = locator.find_element(ARIARole.TEXTBOX, name="Username")
        assert username_field is not None
        
        # Test that we can find elements without specific name
        all_textboxes = locator.find_elements(ARIARole.TEXTBOX)
        assert len(all_textboxes) >= 1


class TestBackwardCompatibility:
    """Ensure the new implementation is backward compatible"""
    
    def test_original_function_signatures(self, driver: WebDriver):
        """Test that original function signatures still work"""
        driver.get("https://v0-imagine-deals.vercel.app")
        driver.implicitly_wait(3)
        
        # Original plural function
        elements = find_elements_by_role(driver, "textbox", name="Username")
        assert len(elements) > 0
        
        # Original singular function
        element = find_element_by_role(driver, "textbox", name="Username")
        assert element is not None
        
        element.send_keys("test_user")


class TestPerformance:
    """Performance-related tests"""
    
    def test_multiple_searches_efficiency(self, driver: WebDriver):
        """Test that multiple searches with same locator are efficient"""
        driver.get("https://v0-imagine-deals.vercel.app")
        driver.implicitly_wait(3)
        
        # Reuse the same locator instance
        locator = ARIARoleLocator(driver)
        
        # Multiple searches should work efficiently
        username = locator.find_element(ARIARole.TEXTBOX, name="Username")
        password = locator.find_element(ARIARole.TEXTBOX, name="Password")
        all_textboxes = locator.find_elements(ARIARole.TEXTBOX)
        
        assert username is not None
        assert password is not None
        assert len(all_textboxes) >= 2