"""
W3C WebDriver BiDi accessibility locators implementation.

This module provides native BiDi accessibility locators following the W3C standard,
with intelligent fallback mechanisms for broader compatibility.

"""

import logging
from typing import List, Optional, Dict, Any, Union, Final
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException, NoSuchElementException

logger = logging.getLogger(__name__)

# Constants for better maintainability
DEFAULT_MAX_NODE_COUNT: Final[int] = 1000
SUPPORTED_ACCESSIBILITY_ATTRIBUTES: Final[frozenset] = frozenset([
    "checked", "pressed", "expanded", "level", "disabled", "readonly", "required"
])
BIDI_LOCATE_NODES_METHOD: Final[str] = "browsingContext.locateNodes"


class BiDiNotAvailableError(WebDriverException):
    """Raised when BiDi functionality isn't available in this Selenium version"""
    pass


class BiDiAccessibilityLocator:
    """
    Production-ready W3C WebDriver BiDi accessibility locator implementation.
    
    Provides native BiDi element location with intelligent fallback strategies.
    Optimized for performance and maintainability in enterprise environments.
    
    Args:
        driver: Selenium WebDriver instance with BiDi capabilities
        
    Raises:
        BiDiNotAvailableError: When BiDi functionality is unavailable
    """
    
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self._context_id: Optional[str] = None
        self._bidi_available: Optional[bool] = None  # Cache availability check
        
    def is_available(self) -> bool:
        """
        Check if BiDi accessibility locators are available.
        
        Uses caching to avoid repeated expensive checks.
        
        Returns:
            bool: True if BiDi accessibility locators are functional
        """
        if self._bidi_available is not None:
            return self._bidi_available
            
        try:
            # Primary check: browsing_context property (Selenium 4.15+)
            if hasattr(self.driver, 'browsing_context') and self.driver.browsing_context:
                self._bidi_available = True
                return True
                
            # Fallback: legacy bidi_connection check
            if hasattr(self.driver, 'bidi_connection') and self.driver.bidi_connection:
                self._bidi_available = True
                return True
                
            self._bidi_available = False
            return False
            
        except (AttributeError, WebDriverException) as e:
            logger.debug(f"BiDi availability check failed: {e}")
            self._bidi_available = False
            return False
    
    def _get_context_id(self) -> str:
        """
        Get the current browsing context ID with caching.
        
        Returns:
            str: The current browsing context identifier
            
        Raises:
            BiDiNotAvailableError: When context ID cannot be determined
        """
        if self._context_id:
            return self._context_id
            
        try:
            # BiDi context ID is typically the window handle
            window_handle = self.driver.current_window_handle
            if not window_handle:
                raise BiDiNotAvailableError("No active window handle available")
                
            self._context_id = window_handle
            return self._context_id
            
        except WebDriverException as e:
            logger.debug(f"Failed to retrieve context ID: {e}")
            raise BiDiNotAvailableError(f"Cannot determine browsing context: {e}") from e
    
    def find_elements(
        self, 
        role: str, 
        name: Optional[str] = None, 
        max_count: Optional[int] = None,
        **filters
    ) -> List[WebElement]:
        """
        Find elements using W3C BiDi accessibility locators.
        
        Args:
            role: ARIA role to search for (e.g., 'button', 'textbox')
            name: Accessible name to match (optional)
            max_count: Maximum number of elements to return
            **filters: Additional accessibility attributes to filter by
            
        Returns:
            List[WebElement]: Found elements, empty if none match
            
        Raises:
            BiDiNotAvailableError: When BiDi is not functional
            ValueError: When invalid parameters are provided
        """
        if not role or not isinstance(role, str):
            raise ValueError("Role must be a non-empty string")
            
        if not self.is_available():
            raise BiDiNotAvailableError("BiDi accessibility locators not available")
        
        context_id = self._get_context_id()
        locator_value = self._build_accessibility_locator(role, name, filters)
        
        try:
            result = self._execute_bidi_command(BIDI_LOCATE_NODES_METHOD, {
                "context": context_id,
                "locator": {
                    "type": "accessibility",
                    "value": locator_value
                },
                "maxNodeCount": max_count or DEFAULT_MAX_NODE_COUNT
            })
            
            return self._convert_nodes_to_elements(result.get("nodes", []))
            
        except Exception as e:
            logger.debug(f"BiDi accessibility search failed for role '{role}': {e}")
            raise BiDiNotAvailableError(f"BiDi locator execution failed: {e}") from e
    
    def _build_accessibility_locator(
        self, 
        role: str, 
        name: Optional[str], 
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build W3C-compliant accessibility locator dictionary.
        
        Args:
            role: ARIA role to search for
            name: Accessible name (optional)
            filters: Additional accessibility attributes
            
        Returns:
            Dict[str, Any]: W3C BiDi accessibility locator
        """
        locator_value = {"role": role}
        
        if name:
            locator_value["name"] = name
        
        # Only add supported accessibility attributes
        for key, value in filters.items():
            if key in SUPPORTED_ACCESSIBILITY_ATTRIBUTES:
                locator_value[key] = value
            else:
                logger.warning(f"Unsupported accessibility attribute '{key}' ignored")
        
        return locator_value
    
    def find_element(self, role: str, name: Optional[str] = None, **filters) -> WebElement:
        """
        Find single element using BiDi accessibility locators.
        
        Args:
            role: ARIA role to search for
            name: Accessible name (optional)
            **filters: Additional accessibility attributes
            
        Returns:
            WebElement: First matching element
            
        Raises:
            NoSuchElementException: When no elements match the criteria
            BiDiNotAvailableError: When BiDi is not functional
        """
        elements = self.find_elements(role, name, max_count=1, **filters)
        if not elements:
            criteria_desc = self._format_search_criteria(role, name, filters)
            raise NoSuchElementException(f"No element found with {criteria_desc}")
        return elements[0]
    
    def _format_search_criteria(
        self, 
        role: str, 
        name: Optional[str], 
        filters: Dict[str, Any]
    ) -> str:
        """Format search criteria for error messages."""
        parts = [f"role='{role}'"]
        
        if name:
            parts.append(f"name='{name}'")
            
        for key, value in filters.items():
            parts.append(f"{key}='{value}'")
            
        return ", ".join(parts)
    
    def _execute_bidi_command(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute BiDi command with intelligent fallback strategy.
        
        Args:
            method: BiDi method name (e.g., 'browsingContext.locateNodes')
            params: Method parameters
            
        Returns:
            Dict[str, Any]: BiDi command result
            
        Raises:
            BiDiNotAvailableError: When all execution methods fail
        """
        execution_strategies = [
            self._try_native_browsing_context,
            self._try_direct_bidi_command,
            self._try_legacy_bidi_connection,
            self._try_cdp_bridge
        ]
        
        last_error = None
        for strategy in execution_strategies:
            try:
                result = strategy(method, params)
                if result is not None:
                    return result
            except Exception as e:
                logger.debug(f"BiDi execution strategy failed: {strategy.__name__}: {e}")
                last_error = e
                continue
        
        # All strategies failed
        error_msg = f"All BiDi execution strategies failed for method '{method}'"
        if last_error:
            error_msg += f". Last error: {last_error}"
        raise BiDiNotAvailableError(error_msg)
    
    def _try_native_browsing_context(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try executing via native Selenium browsing_context (Selenium 4.15+)."""
        if not (hasattr(self.driver, 'browsing_context') and self.driver.browsing_context):
            return None
            
        if method != BIDI_LOCATE_NODES_METHOD:
            return None
            
        browsing_context = self.driver.browsing_context
        nodes = browsing_context.locate_nodes(
            context=params.get("context"),
            locator=params.get("locator"),
            max_node_count=params.get("maxNodeCount"),
            serialization_options=params.get("serializationOptions"),
            start_nodes=params.get("startNodes")
        )
        return {"nodes": nodes}
    
    def _try_direct_bidi_command(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try executing via direct BiDi command interface (future Selenium versions)."""
        if not hasattr(self.driver, 'execute_bidi_command'):
            return None
        return self.driver.execute_bidi_command(method, params)
    
    def _try_legacy_bidi_connection(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try executing via legacy bidi_connection interface."""
        if not hasattr(self.driver, 'bidi_connection'):
            return None
            
        bidi_conn = self.driver.bidi_connection()
        if hasattr(bidi_conn, 'execute'):
            return bidi_conn.execute(method, params)
        elif hasattr(bidi_conn, 'send'):
            return bidi_conn.send(method, params)
        return None
    
    def _try_cdp_bridge(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try executing via CDP bridge (experimental fallback)."""
        if not hasattr(self.driver, 'execute_cdp_cmd'):
            return None
        return self._execute_bidi_via_cdp(method, params)
    
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
    
    def _filter_accessibility_nodes(
        self, 
        nodes: List[Dict[str, Any]], 
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filter accessibility tree nodes by BiDi criteria.
        
        Args:
            nodes: List of accessibility tree nodes from CDP
            criteria: BiDi accessibility matching criteria
            
        Returns:
            List[Dict[str, Any]]: Nodes matching the criteria
        """
        matching_nodes = []
        
        for node in nodes:
            if self._node_matches_criteria(node, criteria):
                matching_nodes.append(node)
        
        logger.debug(f"Filtered {len(matching_nodes)} nodes from {len(nodes)} total")
        return matching_nodes
    
    def _node_matches_criteria(self, node: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if a single node matches the accessibility criteria."""
        # Check role matching
        if "role" in criteria:
            if not self._role_matches(node.get("role", {}), criteria["role"]):
                return False
        
        # Check name matching
        if "name" in criteria:
            if not self._name_matches(node.get("name", {}), criteria["name"]):
                return False
        
        return True
    
    def _role_matches(self, node_role: Dict[str, Any], expected_role: str) -> bool:
        """Check if node role matches expected role."""
        return (
            node_role.get("value") == expected_role or 
            node_role.get("type") == expected_role
        )
    
    def _name_matches(self, node_name: Dict[str, Any], expected_name: str) -> bool:
        """Check if node name matches expected name (case-insensitive)."""
        actual_name = node_name.get("value", "").lower()
        expected_name_lower = expected_name.lower()
        return expected_name_lower in actual_name


def is_bidi_accessibility_available(driver: WebDriver) -> bool:
    """
    Check if BiDi accessibility locators are available for the driver.
    
    This is a convenience function that provides a quick way to test
    BiDi availability without creating a full locator instance.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        bool: True if BiDi accessibility locators are functional
    """
    try:
        locator = BiDiAccessibilityLocator(driver)
        return locator.is_available()
    except Exception as e:
        logger.debug(f"BiDi availability check failed: {e}")
        return False