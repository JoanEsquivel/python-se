"""
WebDriver BiDi accessibility locators implementation for SeleniumConf demo.

This module provides a minimal, production-ready implementation that uses
ONLY WebDriver BiDi APIs (no CDP, no legacy protocols, no fallbacks).

Key features:
- Pure WebDriver BiDi accessibility snapshot extraction
- Element location by ARIA role using accessibility tree
- Clean, well-commented code suitable for conference demonstration
"""

import logging
from typing import List, Optional, Dict, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from enum import Enum

logger = logging.getLogger(__name__)


class ARIARole(Enum):
    """Common ARIA roles for web elements"""
    BUTTON = "button"
    TEXTBOX = "textbox"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    LINK = "link"
    HEADING = "heading"
    LISTITEM = "listitem"
    LIST = "list"
    COMBOBOX = "combobox"
    SEARCHBOX = "searchbox"


class BiDiAccessibilityError(WebDriverException):
    """Raised when BiDi accessibility operations fail"""
    pass


class BiDiAccessibilityLocator:
    """
    Pure WebDriver BiDi accessibility locator implementation.
    
    This class provides element location capabilities using only the latest
    WebDriver BiDi standard APIs. No CDP, no legacy protocols, no fallbacks.
    
    Usage:
        locator = BiDiAccessibilityLocator(driver)
        elements = locator.find_elements_by_role("button", name="Submit")
    """
    
    def __init__(self, driver: WebDriver):
        """
        Initialize the BiDi accessibility locator.
        
        Args:
            driver: WebDriver instance with BiDi capabilities enabled
            
        Raises:
            BiDiAccessibilityError: If BiDi is not available
        """
        self.driver = driver
        self._validate_bidi_support()
        
    def _validate_bidi_support(self) -> None:
        """
        Validate that WebDriver BiDi is available and functional.
        
        Raises:
            BiDiAccessibilityError: If BiDi is not supported
        """
        try:
            # Check for native BiDi browsing context support (Selenium 4.15+)
            if not hasattr(self.driver, 'browsing_context'):
                raise BiDiAccessibilityError(
                    "WebDriver BiDi not available. Requires Selenium 4.15+ with BiDi enabled."
                )
            
            # Try to access browsing_context - this might trigger BiDi initialization
            browsing_context = self.driver.browsing_context
            if not browsing_context:
                raise BiDiAccessibilityError(
                    "BiDi browsing context not initialized. Ensure driver was created with BiDi enabled."
                )
                
            logger.debug("✅ WebDriver BiDi accessibility support validated")
            
        except Exception as e:
            # If BiDi is not available, provide helpful error message
            error_msg = f"BiDi validation failed: {e}. "
            error_msg += "This demo requires WebDriver BiDi support. "
            error_msg += "Make sure you're using Selenium 4.15+ with a BiDi-enabled driver."
            raise BiDiAccessibilityError(error_msg) from e
    
    def get_accessibility_snapshot(self) -> Dict[str, Any]:
        """
        Extract accessibility snapshot from the current page using WebDriver BiDi.
        
        This method uses the native BiDi browsingContext.getTree command to retrieve
        the complete accessibility tree structure of the current page.
        
        Returns:
            Dict containing the accessibility tree snapshot
            
        Raises:
            BiDiAccessibilityError: If snapshot extraction fails
        """
        try:
            logger.debug("📸 Extracting accessibility snapshot via BiDi...")
            
            # Get current browsing context ID
            context_id = self.driver.current_window_handle
            
            # Use BiDi browsingContext.getTree to get accessibility information
            # This is the W3C standard way to get accessibility tree
            snapshot = self.driver.browsing_context.get_tree(
                context=context_id,
                max_depth=None,  # Get full tree
                include_accessibility=True  # Include accessibility information
            )
            
            logger.debug(f"✅ Accessibility snapshot extracted with {len(snapshot.get('contexts', []))} contexts")
            return snapshot
            
        except Exception as e:
            error_msg = f"Failed to extract accessibility snapshot: {e}"
            logger.error(error_msg)
            raise BiDiAccessibilityError(error_msg) from e
    
    def find_elements_by_role(
        self, 
        role: str, 
        name: Optional[str] = None,
        max_count: int = 100
    ) -> List[WebElement]:
        """
        Find elements by ARIA role using WebDriver BiDi accessibility locators.
        
        This method uses the native BiDi browsingContext.locateNodes command
        with accessibility locator type to find elements by their ARIA role.
        
        Args:
            role: ARIA role to search for (e.g., 'button', 'textbox')
            name: Optional accessible name to match
            max_count: Maximum number of elements to return
            
        Returns:
            List of WebElements matching the criteria
            
        Raises:
            BiDiAccessibilityError: If element location fails
        """
        try:
            logger.debug(f"🔍 Finding elements by role '{role}'" + 
                        (f" with name '{name}'" if name else ""))
            
            # Get current browsing context
            context_id = self.driver.current_window_handle
            
            # Build BiDi accessibility locator
            locator_value = {"role": role}
            if name:
                locator_value["name"] = name
            
            # Use native BiDi locateNodes with accessibility locator
            result = self.driver.browsing_context.locate_nodes(
                context=context_id,
                locator={
                    "type": "accessibility",
                    "value": locator_value
                },
                max_node_count=max_count
            )
            
            # Convert BiDi node references to WebElements
            elements = self._convert_nodes_to_elements(result)
            
            logger.debug(f"✅ Found {len(elements)} elements with role '{role}'")
            return elements
            
        except Exception as e:
            error_msg = f"Failed to find elements by role '{role}': {e}"
            logger.error(error_msg)
            raise BiDiAccessibilityError(error_msg) from e
    
    def find_element_by_role(
        self, 
        role: str, 
        name: Optional[str] = None
    ) -> WebElement:
        """
        Find single element by ARIA role using WebDriver BiDi.
        
        Args:
            role: ARIA role to search for
            name: Optional accessible name to match
            
        Returns:
            First WebElement matching the criteria
            
        Raises:
            NoSuchElementException: If no element is found
            BiDiAccessibilityError: If element location fails
        """
        elements = self.find_elements_by_role(role, name, max_count=1)
        
        if not elements:
            criteria = f"role='{role}'"
            if name:
                criteria += f", name='{name}'"
            raise NoSuchElementException(f"No element found with {criteria}")
            
        return elements[0]
    
    def _convert_nodes_to_elements(self, nodes: List[Dict[str, Any]]) -> List[WebElement]:
        """
        Convert BiDi node references to Selenium WebElement objects.
        
        This method takes the node references returned by BiDi locateNodes
        and converts them to standard Selenium WebElement objects that can
        be used for interactions.
        
        Args:
            nodes: List of BiDi node references
            
        Returns:
            List of WebElement objects
        """
        elements = []
        
        for node in nodes:
            try:
                # BiDi nodes contain a 'sharedId' that can be used to create WebElements
                if "sharedId" in node:
                    element = self._create_element_from_shared_id(node["sharedId"])
                    if element:
                        elements.append(element)
                        logger.debug(f"✅ Converted node with sharedId: {node['sharedId']}")
                else:
                    logger.warning(f"⚠️ Node missing sharedId: {node}")
                    
            except Exception as e:
                logger.debug(f"❌ Failed to convert node to element: {e}")
                continue
        
        return elements
    
    def _create_element_from_shared_id(self, shared_id: str) -> Optional[WebElement]:
        """
        Create a WebElement from a BiDi shared ID.
        
        This method uses the BiDi shared ID to create a proper Selenium
        WebElement that can be used for all standard interactions.
        
        Args:
            shared_id: BiDi shared ID for the element
            
        Returns:
            WebElement instance or None if creation fails
        """
        try:
            # Create WebElement using BiDi shared ID
            # The shared ID serves as the element identifier in BiDi
            element = WebElement(self.driver, shared_id)
            
            # Validate element is accessible by checking a basic property
            # This will raise an exception if the element is stale/invalid
            _ = element.tag_name
            
            return element
            
        except Exception as e:
            logger.debug(f"Failed to create element from shared ID {shared_id}: {e}")
            return None


def create_bidi_locator(driver: WebDriver) -> BiDiAccessibilityLocator:
    """
    Factory function to create a BiDi accessibility locator.
    
    This is a convenience function that handles the initialization
    and validation of BiDi support.
    
    Args:
        driver: WebDriver instance with BiDi enabled
        
    Returns:
        BiDiAccessibilityLocator instance
        
    Raises:
        BiDiAccessibilityError: If BiDi is not available
    """
    return BiDiAccessibilityLocator(driver)
