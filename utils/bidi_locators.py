"""
Native WebDriver BiDi accessibility locators - the future of element finding

This implements W3C WebDriver BiDi standard for accessibility-based element location.
Falls back gracefully when BiDi isn't available yet.
"""

import logging
from typing import List, Optional, Dict, Any, Union
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException, NoSuchElementException

logger = logging.getLogger(__name__)


class BiDiNotAvailableError(WebDriverException):
    """Raised when BiDi functionality isn't available in this Selenium version"""
    pass


class BiDiAccessibilityLocator:
    """
    Finds elements using W3C WebDriver BiDi accessibility locators.
    
    This is the "proper" way to do it according to the spec, but requires
    newer Selenium versions that support BiDi locate_nodes with accessibility.
    """
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._context_id = None
        
    def is_available(self) -> bool:
        """Check if BiDi accessibility locators are available"""
        try:
            # Try to access BiDi session
            if not hasattr(self.driver, 'bidi_connection'):
                return False
            
            # Check if connection exists and is active
            if not self.driver.bidi_connection:
                return False
                
            return True
        except (AttributeError, WebDriverException):
            return False
    
    def _get_context_id(self) -> str:
        """Get the current browsing context ID"""
        if self._context_id:
            return self._context_id
            
        try:
            # Get current window handle and convert to BiDi context
            window_handle = self.driver.current_window_handle
            # In BiDi, context IDs are often the same as window handles
            self._context_id = window_handle
            return self._context_id
        except Exception as e:
            logger.debug(f"Failed to get context ID: {e}")
            raise BiDiNotAvailableError("Cannot determine browsing context")
    
    def find_elements(self, role: str, name: Optional[str] = None, **filters) -> List[WebElement]:
        """
        Find elements using BiDi accessibility locators
        
        This uses the official W3C spec for accessibility-based element location.
        Much cleaner than CDP hacks.
        """
        if not self.is_available():
            raise BiDiNotAvailableError("BiDi accessibility locators not available")
        
        context_id = self._get_context_id()
        
        # Build the locator according to W3C spec
        locator_value = {"role": role}
        if name:
            locator_value["name"] = name
        
        # Add any additional accessibility attributes
        for key, value in filters.items():
            if key in ["checked", "pressed", "expanded", "level", "disabled"]:
                locator_value[key] = value
        
        try:
            # Use the BiDi locate_nodes command with accessibility locator
            result = self._execute_bidi_command("browsingContext.locateNodes", {
                "context": context_id,
                "locator": {
                    "type": "accessibility",
                    "value": locator_value
                },
                "maxNodeCount": 1000  # Reasonable limit
            })
            
            # Convert BiDi node results to WebElements
            return self._convert_nodes_to_elements(result.get("nodes", []))
            
        except Exception as e:
            logger.debug(f"BiDi accessibility locator failed: {e}")
            # Re-raise as our custom exception
            raise BiDiNotAvailableError(f"BiDi locator execution failed: {e}")
    
    def find_element(self, role: str, name: Optional[str] = None, **filters) -> WebElement:
        """Find single element using BiDi accessibility locators"""
        elements = self.find_elements(role, name, **filters)
        if not elements:
            filter_desc = f"role='{role}'"
            if name:
                filter_desc += f", name='{name}'"
            if filters:
                filter_desc += ", " + ", ".join([f"{k}='{v}'" for k, v in filters.items()])
            raise NoSuchElementException(f"No element found with {filter_desc}")
        return elements[0]
    
    def _execute_bidi_command(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a BiDi command through the active connection"""
        try:
            # This is how you'd execute BiDi commands in modern Selenium
            # The exact API might vary slightly depending on version
            if hasattr(self.driver, 'execute_bidi_command'):
                return self.driver.execute_bidi_command(method, params)
            elif hasattr(self.driver, 'bidi_connection'):
                # Alternative approach for different Selenium versions
                return self.driver.bidi_connection.execute(method, params)
            else:
                raise BiDiNotAvailableError("No BiDi execution method available")
                
        except Exception as e:
            logger.debug(f"BiDi command execution failed: {e}")
            raise BiDiNotAvailableError(f"BiDi command '{method}' failed: {e}")
    
    def _convert_nodes_to_elements(self, nodes: List[Dict[str, Any]]) -> List[WebElement]:
        """Convert BiDi node references to WebElement objects"""
        elements = []
        
        for node in nodes:
            try:
                # BiDi nodes have a 'sharedId' that can be used to create WebElements
                if "sharedId" in node:
                    # Create WebElement from shared ID
                    element = self._create_element_from_shared_id(node["sharedId"])
                    if element:
                        elements.append(element)
                elif "backendNodeId" in node:
                    # Alternative: use backend node ID
                    element = self._create_element_from_backend_id(node["backendNodeId"])
                    if element:
                        elements.append(element)
                        
            except Exception as e:
                logger.debug(f"Failed to convert node to element: {e}")
                continue
        
        return elements
    
    def _create_element_from_shared_id(self, shared_id: str) -> Optional[WebElement]:
        """Create WebElement from BiDi shared ID"""
        try:
            # This would use Selenium's internal BiDi -> WebElement conversion
            # The exact implementation depends on Selenium's internal API
            from selenium.webdriver.remote.webelement import WebElement
            
            # Create element with shared ID reference
            element = WebElement(self.driver, None)
            element._id = shared_id  # Set the shared ID as element ID
            
            # Verify element is still valid
            element.tag_name  # This will throw if element is stale
            return element
            
        except Exception as e:
            logger.debug(f"Failed to create element from shared ID {shared_id}: {e}")
            return None
    
    def _create_element_from_backend_id(self, backend_id: int) -> Optional[WebElement]:
        """Create WebElement from backend node ID (fallback method)"""
        try:
            # Convert backend node ID to something Selenium can use
            # This might require additional BiDi calls
            result = self._execute_bidi_command("script.evaluate", {
                "expression": f"document.querySelector('[data-backend-id=\"{backend_id}\"]')",
                "target": {"context": self._get_context_id()}
            })
            
            if result and "result" in result:
                # Extract element reference from result
                return self._handle_script_result(result["result"])
                
        except Exception as e:
            logger.debug(f"Failed to create element from backend ID {backend_id}: {e}")
            
        return None
    
    def _handle_script_result(self, result: Dict[str, Any]) -> Optional[WebElement]:
        """Handle script evaluation result and convert to WebElement"""
        try:
            if result.get("type") == "node" and "sharedId" in result:
                return self._create_element_from_shared_id(result["sharedId"])
        except Exception as e:
            logger.debug(f"Failed to handle script result: {e}")
            
        return None


def is_bidi_accessibility_available(driver: WebDriver) -> bool:
    """Check if BiDi accessibility locators are available for this driver"""
    try:
        locator = BiDiAccessibilityLocator(driver)
        return locator.is_available()
    except Exception:
        return False