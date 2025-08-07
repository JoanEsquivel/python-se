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
            # Method 1: Direct BiDi command execution (future Selenium versions)
            if hasattr(self.driver, 'execute_bidi_command'):
                return self.driver.execute_bidi_command(method, params)
            
            # Method 2: BiDi connection property (current approach)
            elif hasattr(self.driver, 'bidi_connection'):
                # Get the actual BiDi connection
                bidi_conn = self.driver.bidi_connection()  # Call it as a method
                if hasattr(bidi_conn, 'execute'):
                    return bidi_conn.execute(method, params)
                elif hasattr(bidi_conn, 'send'):
                    return bidi_conn.send(method, params)
                else:
                    raise BiDiNotAvailableError("BiDi connection exists but has no execute/send method")
            
            # Method 3: Try using CDP as BiDi bridge (experimental)
            elif hasattr(self.driver, 'execute_cdp_cmd'):
                return self._execute_bidi_via_cdp(method, params)
            
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
    
    def _execute_bidi_via_cdp(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Experimental: Execute BiDi commands via CDP bridge"""
        logger.debug(f"Attempting BiDi command '{method}' via CDP bridge")
        
        if method == "browsingContext.locateNodes":
            # Convert BiDi locateNodes to CDP accessibility search
            context_id = params.get("context")
            locator = params.get("locator", {})
            
            if locator.get("type") == "accessibility":
                # Use CDP Accessibility to find nodes
                try:
                    # Enable accessibility domain
                    self.driver.execute_cdp_cmd("Accessibility.enable", {})
                    
                    # Get accessibility tree
                    tree_result = self.driver.execute_cdp_cmd("Accessibility.getFullAXTree", {})
                    
                    # Filter nodes by accessibility criteria
                    matching_nodes = self._filter_accessibility_nodes(
                        tree_result.get("nodes", []), 
                        locator.get("value", {})
                    )
                    
                    return {"nodes": matching_nodes}
                    
                except Exception as e:
                    logger.debug(f"CDP accessibility bridge failed: {e}")
                    raise BiDiNotAvailableError(f"CDP bridge failed: {e}")
        
        raise BiDiNotAvailableError(f"BiDi command '{method}' not supported via CDP bridge")
    
    def _filter_accessibility_nodes(self, nodes: List[Dict], criteria: Dict[str, Any]) -> List[Dict]:
        """Filter accessibility tree nodes by BiDi criteria"""
        matching = []
        
        for node in nodes:
            # Check role matching
            role_match = True
            if "role" in criteria:
                node_role = node.get("role", {})
                expected_role = criteria["role"]
                
                # Handle different role formats
                if node_role.get("value") != expected_role and node_role.get("type") != expected_role:
                    role_match = False
            
            # Check name matching  
            name_match = True
            if "name" in criteria:
                node_name = node.get("name", {})
                expected_name = criteria["name"]
                actual_name = node_name.get("value", "")
                
                if expected_name.lower() not in actual_name.lower():
                    name_match = False
            
            if role_match and name_match:
                matching.append(node)
        
        logger.debug(f"Filtered {len(matching)} nodes from {len(nodes)} total")
        return matching


def is_bidi_accessibility_available(driver: WebDriver) -> bool:
    """Check if BiDi accessibility locators are available for this driver"""
    try:
        locator = BiDiAccessibilityLocator(driver)
        return locator.is_available()
    except Exception:
        return False