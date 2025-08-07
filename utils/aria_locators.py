"""
ARIA role locators for Selenium - brings getByRole() to Selenium

This module provides a clean way to find elements by their accessibility roles,
making tests more readable and resilient to UI changes.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from .bidi_locators import BiDiAccessibilityLocator, BiDiNotAvailableError, is_bidi_accessibility_available


logger = logging.getLogger(__name__)


class ARIARole(Enum):
    """Common ARIA roles for web elements"""
    TEXTBOX = "textbox"
    BUTTON = "button"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    LINK = "link"
    HEADING = "heading"
    LISTITEM = "listitem"
    LIST = "list"
    COMBOBOX = "combobox"
    SEARCHBOX = "searchbox"


@dataclass
class LocatorConfig:
    """Settings for how the locator should behave"""
    use_accessibility_tree: bool = True
    fallback_to_dom: bool = True
    timeout_seconds: float = 10.0
    debug_mode: bool = False


class AccessibilityTreeError(WebDriverException):
    """When we can't read the accessibility tree"""
    pass


class ARIARoleLocator:
    """
    Find elements by their ARIA roles.
    
    This works in two ways:
    1. First tries to read the browser's accessibility tree (most accurate)
    2. Falls back to CSS selectors if that doesn't work
    
    Example:
        locator = ARIARoleLocator(driver)
        button = locator.find_element("button", name="Submit")
        button.click()
    """
    
    # Map roles to CSS selectors for DOM fallback
    ROLE_SELECTORS: Dict[str, str] = {
        "textbox": 'input[type="text"], input[type="password"], input[type="email"], input[type="search"], input:not([type]), textarea',
        "button": 'button, input[type="button"], input[type="submit"], input[type="reset"], [role="button"]',
        "checkbox": 'input[type="checkbox"], [role="checkbox"]',
        "radio": 'input[type="radio"], [role="radio"]',
        "link": 'a[href], [role="link"]',
        "heading": 'h1, h2, h3, h4, h5, h6, [role="heading"]',
        "listitem": 'li, [role="listitem"]',
        "list": 'ul, ol, [role="list"]'
    }
    
    # How the accessibility tree might report these roles
    ROLE_MAPPINGS: Dict[str, List[str]] = {
        "textbox": ['textbox', 'combobox', 'searchbox'],
        "button": ['button'],
        "checkbox": ['checkbox'],
        "radio": ['radio'],
        "link": ['link'],
        "heading": ['heading'],
        "listitem": ['listitem'],
        "list": ['list']
    }

    def __init__(self, driver: WebDriver, config: Optional[LocatorConfig] = None):
        self.driver = driver
        self.config = config or LocatorConfig()
        
        # Check if native BiDi accessibility is available
        self.bidi_locator = None
        if is_bidi_accessibility_available(driver):
            self.bidi_locator = BiDiAccessibilityLocator(driver)
            logger.debug("Using native BiDi accessibility locators")
        else:
            logger.debug("BiDi not available, using CDP/DOM fallback")
        
        if self.config.debug_mode:
            logging.basicConfig(level=logging.DEBUG)

    def find_elements(
        self, 
        role: Union[ARIARole, str], 
        name: Optional[str] = None,
        **filters: Any
    ) -> List[WebElement]:
        """
        Find all elements with the given role.
        
        Priority order:
        1. Native BiDi accessibility locators (W3C standard)
        2. CDP accessibility tree (fallback for older versions)
        3. DOM CSS selectors (fallback for compatibility)
        
        Args:
            role: What kind of element to look for (button, textbox, etc.)
            name: The accessible name (usually the visible text or label)
            **filters: Other properties like checked=True
            
        Returns:
            List of matching elements (empty if none found)
        """
        role_value = role.value if isinstance(role, ARIARole) else role
        
        if name is not None:
            filters['name'] = name
            
        logger.debug(f"Looking for {role_value} elements with {filters}")
        
        elements: List[WebElement] = []
        
        # Step 1: Try native BiDi accessibility locators first (the future!)
        if self.bidi_locator:
            try:
                elements = self.bidi_locator.find_elements(role_value, name, **filters)
                logger.debug(f"BiDi accessibility found {len(elements)} elements")
                if elements:
                    return elements
            except BiDiNotAvailableError as e:
                logger.debug(f"BiDi not available: {e}")
                # Disable BiDi for future calls in this session
                self.bidi_locator = None
            except Exception as e:
                logger.warning(f"BiDi accessibility failed: {e}")
        
        # Step 2: Try CDP accessibility tree (current implementation)
        if self.config.use_accessibility_tree:
            try:
                elements = self._find_via_accessibility_tree(role_value, filters)
                logger.debug(f"CDP accessibility tree found {len(elements)} elements")
                if elements:
                    return elements
            except Exception as e:
                logger.warning(f"CDP accessibility tree failed: {e}")
                if not self.config.fallback_to_dom:
                    raise AccessibilityTreeError(f"Accessibility tree failed: {e}")
        
        # Step 3: Fall back to DOM CSS selectors (compatibility mode)
        if self.config.fallback_to_dom:
            elements = self._find_via_dom(role_value, filters)
            logger.debug(f"DOM search found {len(elements)} elements")
            
        return elements

    def find_element(
        self, 
        role: Union[ARIARole, str], 
        name: Optional[str] = None,
        **filters: Any
    ) -> WebElement:
        """
        Find one element with the given role.
        
        Args:
            role: What kind of element to look for
            name: The accessible name
            **filters: Other properties
            
        Returns:
            The first matching element
            
        Raises:
            NoSuchElementException: If no element is found
        """
        elements = self.find_elements(role, name, **filters)
        
        if not elements:
            role_value = role.value if isinstance(role, ARIARole) else role
            filter_desc = self._describe_filters({'name': name, **filters} if name else filters)
            raise NoSuchElementException(
                f"Can't find {role_value} element{filter_desc}"
            )
            
        return elements[0]

    def _find_via_accessibility_tree(self, role: str, filters: Dict[str, Any]) -> List[WebElement]:
        """Use Chrome's accessibility tree to find elements"""
        try:
            self._enable_accessibility_apis()
            tree_data = self.driver.execute_cdp_cmd("Accessibility.getFullAXTree", {})
            
            return self._process_tree_nodes(tree_data.get("nodes", []), role, filters)
            
        except Exception as e:
            logger.error(f"Accessibility tree search failed: {e}")
            raise AccessibilityTreeError(f"Can't read accessibility tree: {e}")

    def _find_via_dom(self, role: str, filters: Dict[str, Any]) -> List[WebElement]:
        """Fall back to regular CSS selectors"""
        selector = self.ROLE_SELECTORS.get(role)
        if not selector:
            logger.warning(f"Don't know how to find {role} elements with CSS")
            return []
            
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return self._filter_by_accessible_name(elements, role, filters)
            
        except Exception as e:
            logger.error(f"DOM search failed for {role}: {e}")
            return []

    def _process_tree_nodes(
        self, 
        nodes: List[Dict[str, Any]], 
        target_role: str, 
        filters: Dict[str, Any]
    ) -> List[WebElement]:
        """Go through accessibility tree nodes to find matches"""
        matches = []
        possible_roles = self.ROLE_MAPPINGS.get(target_role, [target_role])
        
        for node in nodes:
            if not self._node_has_role(node, possible_roles):
                continue
                
            if not self._node_matches_filters(node, filters):
                continue
                
            element = self._convert_node_to_element(node)
            if element:
                matches.append(element)
                
        return matches

    def _filter_by_accessible_name(
        self, 
        elements: List[WebElement], 
        role: str, 
        filters: Dict[str, Any]
    ) -> List[WebElement]:
        """Check which elements match our criteria"""
        if not filters:
            return elements
            
        matches = []
        for element in elements:
            if self._element_matches_filters(element, role, filters):
                matches.append(element)
                
        return matches

    def _get_accessible_name(self, element: WebElement, role: str) -> Optional[str]:
        """
        Figure out what name a screen reader would announce for this element.
        This follows the same rules browsers use.
        """
        # Check aria-label first
        aria_label = element.get_attribute('aria-label')
        if aria_label:
            return aria_label.strip()
            
        # Check if another element labels this one
        labelledby_id = element.get_attribute('aria-labelledby')
        if labelledby_id:
            try:
                label_element = self.driver.find_element(By.ID, labelledby_id)
                return label_element.text.strip()
            except NoSuchElementException:
                pass
                
        # For buttons and links, use the text content
        if role in ["button", "link"]:
            text = element.text.strip()
            if text:
                return text
                
        # Look for a label element that points to this input
        element_id = element.get_attribute('id')
        if element_id:
            try:
                label = self.driver.find_element(By.CSS_SELECTOR, f'label[for="{element_id}"]')
                return label.text.strip()
            except NoSuchElementException:
                pass
                
        # Check if this element is inside a label
        try:
            parent_label = element.find_element(By.XPATH, './ancestor::label[1]')
            return parent_label.text.strip()
        except NoSuchElementException:
            pass
            
        # For text inputs, check the placeholder
        if role == "textbox":
            placeholder = element.get_attribute('placeholder')
            if placeholder:
                return placeholder.strip()
                
        # Last resort - check the title attribute
        title = element.get_attribute('title')
        if title:
            return title.strip()
            
        return None

    def _enable_accessibility_apis(self) -> None:
        """Turn on the Chrome DevTools APIs we need"""
        try:
            self.driver.execute_cdp_cmd("DOM.enable", {})
            self.driver.execute_cdp_cmd("Runtime.enable", {})
            self.driver.execute_cdp_cmd("Accessibility.enable", {})
        except Exception as e:
            raise AccessibilityTreeError(f"Can't enable accessibility APIs: {e}")

    def _node_has_role(self, node: Dict[str, Any], target_roles: List[str]) -> bool:
        """Check if this accessibility node has one of the roles we want"""
        node_role = node.get("role")
        if isinstance(node_role, dict):
            actual_role = node_role.get("value")
        else:
            actual_role = node_role
            
        return actual_role in target_roles

    def _node_matches_filters(self, node: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if this node matches all our search criteria"""
        if not filters:
            return True
            
        for key, expected in filters.items():
            actual = self._get_node_property(node, key)
            
            if isinstance(expected, bool):
                actual = self._convert_to_bool(actual)
                
            if actual != expected:
                return False
                
        return True

    def _element_matches_filters(self, element: WebElement, role: str, filters: Dict[str, Any]) -> bool:
        """Check if this DOM element matches our search criteria"""
        if not filters:
            return True
            
        for key, expected in filters.items():
            if key == 'name':
                actual = self._get_accessible_name(element, role)
                if actual != expected:
                    return False
            # We could add other filter types here later
            
        return True

    def _get_node_property(self, node: Dict[str, Any], property_name: str) -> Any:
        """Extract a property value from an accessibility tree node"""
        for prop in node.get("properties", []):
            if prop.get("name") == property_name:
                value = prop.get("value")
                if isinstance(value, dict):
                    return value.get("value")
                return value
        return None

    def _convert_to_bool(self, value: Any) -> bool:
        """Convert various representations to a proper boolean"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == "true"
        return False

    def _convert_node_to_element(self, node: Dict[str, Any]) -> Optional[WebElement]:
        """Turn an accessibility tree node into a Selenium WebElement"""
        if "backendDOMNodeId" not in node:
            return None
            
        try:
            backend_id = node["backendDOMNodeId"]
            
            # Method 1: Try direct backend node resolution
            try:
                resolved = self.driver.execute_cdp_cmd("DOM.resolveNode", {
                    "backendNodeId": backend_id
                })
                if "object" in resolved:
                    element = self.driver.execute_script("return arguments[0];", resolved["object"])
                    if element:
                        return element
            except:
                pass  # Try alternative methods
            
            # Method 2: Use DOM.describeNode to get attributes and find via CSS
            try:
                described = self.driver.execute_cdp_cmd("DOM.describeNode", {
                    "backendNodeId": backend_id
                })
                node_info = described.get("node", {})
                
                # Build CSS selector from node attributes
                selector = self._build_selector_from_node(node_info)
                if selector:
                    elements = self.driver.find_elements("css selector", selector)
                    if elements:
                        return elements[0]  # Return first match
                        
            except Exception as e:
                logger.debug(f"Method 2 failed: {e}")
            
            # Method 3: Use JavaScript to find element by matching attributes
            try:
                described = self.driver.execute_cdp_cmd("DOM.describeNode", {
                    "backendNodeId": backend_id
                })
                node_info = described.get("node", {})
                attributes = node_info.get("attributes", [])
                
                # Build JavaScript to find element
                script = self._build_find_script(node_info.get("localName", ""), attributes)
                if script:
                    element = self.driver.execute_script(script)
                    if element:
                        return element
                        
            except Exception as e:
                logger.debug(f"Method 3 failed: {e}")
            
        except Exception as e:
            logger.debug(f"Couldn't convert accessibility node to element: {e}")
            
        return None
    
    def _build_selector_from_node(self, node_info: Dict[str, Any]) -> Optional[str]:
        """Build CSS selector from DOM node information"""
        try:
            tag_name = node_info.get("localName", "").lower()
            if not tag_name:
                return None
            
            attributes = node_info.get("attributes", [])
            selector_parts = [tag_name]
            
            # Process attributes in pairs (name, value)
            for i in range(0, len(attributes), 2):
                if i + 1 < len(attributes):
                    attr_name = attributes[i]
                    attr_value = attributes[i + 1]
                    
                    # Add useful attributes to selector
                    if attr_name in ["id", "class", "name", "type", "data-testid"]:
                        if attr_name == "id" and attr_value:
                            selector_parts.append(f"#{attr_value}")
                        elif attr_name == "class" and attr_value:
                            classes = attr_value.split()
                            for cls in classes[:2]:  # Limit to first 2 classes
                                selector_parts.append(f".{cls}")
                        elif attr_name in ["name", "type", "data-testid"] and attr_value:
                            selector_parts.append(f'[{attr_name}="{attr_value}"]')
            
            return "".join(selector_parts) if len(selector_parts) > 1 else None
            
        except Exception as e:
            logger.debug(f"Failed to build selector: {e}")
            return None
    
    def _build_find_script(self, tag_name: str, attributes: List[str]) -> Optional[str]:
        """Build JavaScript to find element by attributes"""
        try:
            if not tag_name:
                return None
            
            conditions = [f'elem.tagName.toLowerCase() === "{tag_name.lower()}"']
            
            # Process attributes in pairs
            for i in range(0, len(attributes), 2):
                if i + 1 < len(attributes):
                    attr_name = attributes[i]
                    attr_value = attributes[i + 1]
                    
                    if attr_name in ["id", "name", "type", "data-testid"] and attr_value:
                        conditions.append(f'elem.getAttribute("{attr_name}") === "{attr_value}"')
            
            if len(conditions) > 1:  # Only if we have identifying attributes
                condition_str = " && ".join(conditions)
                return f"""
                const elements = document.querySelectorAll('{tag_name}');
                for (let elem of elements) {{
                    if ({condition_str}) {{
                        return elem;
                    }}
                }}
                return null;
                """
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to build find script: {e}")
            return None

    def _describe_filters(self, filters: Dict[str, Any]) -> str:
        """Create a human-readable description of search filters"""
        if not filters:
            return ""
            
        clean_filters = {k: v for k, v in filters.items() if v is not None}
        if not clean_filters:
            return ""
            
        descriptions = [f"{k}='{v}'" for k, v in clean_filters.items()]
        return f" with {', '.join(descriptions)}"


# Simple functions for quick use
def find_elements_by_role(
    driver: WebDriver, 
    role: Union[ARIARole, str], 
    name: Optional[str] = None,
    **filters: Any
) -> List[WebElement]:
    """
    Quick way to find multiple elements by role.
    
    Example:
        buttons = find_elements_by_role(driver, "button")
        submit_buttons = find_elements_by_role(driver, "button", name="Submit")
    """
    locator = ARIARoleLocator(driver)
    return locator.find_elements(role, name, **filters)


def find_element_by_role(
    driver: WebDriver, 
    role: Union[ARIARole, str], 
    name: Optional[str] = None,
    **filters: Any
) -> WebElement:
    """
    Quick way to find one element by role.
    
    Example:
        submit_btn = find_element_by_role(driver, "button", name="Submit")
        submit_btn.click()
    """
    locator = ARIARoleLocator(driver)
    return locator.find_element(role, name, **filters)