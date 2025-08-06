"""
Selenium utilities for modern web automation
"""

from .aria_locators import (
    ARIARoleLocator,
    ARIARole,
    LocatorConfig,
    find_element_by_role,
    find_elements_by_role,
    AccessibilityTreeError
)

__all__ = [
    'ARIARoleLocator',
    'ARIARole',
    'LocatorConfig',
    'find_element_by_role',
    'find_elements_by_role',
    'AccessibilityTreeError'
]