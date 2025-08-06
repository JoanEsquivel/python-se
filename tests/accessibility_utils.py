# accessibility_utils.py

def debug_accessibility_tree(driver):
    """
    Debug function to print the accessibility tree structure
    """
    driver.execute_cdp_cmd("DOM.enable", {})
    driver.execute_cdp_cmd("Runtime.enable", {})
    driver.execute_cdp_cmd("Accessibility.enable", {})

    ax_tree = driver.execute_cdp_cmd("Accessibility.getFullAXTree", {})
    
    print("=== ACCESSIBILITY TREE DEBUG ===")
    for i, node in enumerate(ax_tree.get("nodes", [])):
        if i > 30:  # Limit output but show more nodes
            break
        role = node.get("role")
        
        # Extract actual role value
        if isinstance(role, dict):
            actual_role = role.get("value")
        else:
            actual_role = role
            
        properties = node.get("properties", [])
        # Extract name property, handling CDP format
        name_prop = "No name"
        for prop in properties:
            if prop.get("name") == "name":
                value = prop.get("value")
                if isinstance(value, dict):
                    name_prop = value.get("value", "No name")
                else:
                    name_prop = value or "No name"
                break
        
        # Show ALL nodes to understand the full tree structure
        print(f"Node {i}: role='{actual_role}', name='{name_prop}', properties={len(properties)}")
        if properties:
            for prop in properties[:3]:  # Show first 3 properties
                prop_value = prop.get('value')
                if isinstance(prop_value, dict):
                    prop_value = prop_value.get('value', prop_value)
                print(f"  - {prop.get('name')}: {prop_value}")
    print("=== END DEBUG ===")

def find_elements_by_role_dom_fallback(driver, role, **filters):
    """
    Fallback method using DOM queries when accessibility tree doesn't work.
    Mimics Playwright's getByRole behavior for common HTML elements.
    """
    from selenium.webdriver.common.by import By
    
    # Role to CSS selector mappings (like Playwright does internally)
    role_selectors = {
        'textbox': 'input[type="text"], input[type="password"], input[type="email"], input[type="search"], input:not([type]), textarea',
        'button': 'button, input[type="button"], input[type="submit"], input[type="reset"], [role="button"]',
        'checkbox': 'input[type="checkbox"], [role="checkbox"]',
        'radio': 'input[type="radio"], [role="radio"]',
        'link': 'a[href], [role="link"]',
        'heading': 'h1, h2, h3, h4, h5, h6, [role="heading"]',
        'listitem': 'li, [role="listitem"]'
    }
    
    selector = role_selectors.get(role)
    if not selector:
        return []
    
    elements = driver.find_elements(By.CSS_SELECTOR, selector)
    filtered_elements = []
    
    for element in elements:
        if not filters:
            filtered_elements.append(element)
            continue
            
        # Apply name filter (most common)
        if 'name' in filters:
            expected_name = filters['name']
            
            # Check various ways an element can have an accessible name
            accessible_name = None
            
            # 1. aria-label
            accessible_name = element.get_attribute('aria-label')
            
            # 2. aria-labelledby
            if not accessible_name:
                labelledby_id = element.get_attribute('aria-labelledby')
                if labelledby_id:
                    try:
                        label_element = driver.find_element(By.ID, labelledby_id)
                        accessible_name = label_element.text.strip()
                    except:
                        pass
            
            # 3. For buttons, links, and similar elements - use text content
            if not accessible_name and role in ['button', 'link']:
                accessible_name = element.text.strip()
            
            # 4. Associated label element (mainly for form controls)
            if not accessible_name:
                element_id = element.get_attribute('id')
                if element_id:
                    try:
                        label_element = driver.find_element(By.CSS_SELECTOR, f'label[for="{element_id}"]')
                        accessible_name = label_element.text.strip()
                    except:
                        pass
            
            # 5. Parent label element (mainly for form controls)
            if not accessible_name:
                try:
                    parent_label = element.find_element(By.XPATH, './ancestor::label[1]')
                    accessible_name = parent_label.text.strip()
                except:
                    pass
            
            # 6. placeholder attribute (for inputs)
            if not accessible_name and role == 'textbox':
                accessible_name = element.get_attribute('placeholder')
            
            # 7. title attribute
            if not accessible_name:
                accessible_name = element.get_attribute('title')
            
            # 8. For textbox elements without other names, use text content as last resort
            if not accessible_name and role == 'textbox':
                accessible_name = element.text.strip()
            
            # Check if accessible name matches expected
            if accessible_name and accessible_name == expected_name:
                filtered_elements.append(element)
    
    return filtered_elements

def find_elements_by_role(driver, role, **filters):
    """
    Find multiple elements by ARIA role using the Accessibility tree (CDP).
    Automatically infers roles for common HTML elements like Playwright does.

    Args:
        driver: Selenium WebDriver instance.
        role (str): The ARIA role to match (e.g. 'button', 'checkbox', 'textbox').
        filters (dict): Optional ARIA filters, e.g. name="Submit", checked=True.

    Returns:
        List of Selenium WebElements matching the criteria.
    """
    driver.execute_cdp_cmd("DOM.enable", {})
    driver.execute_cdp_cmd("Runtime.enable", {})
    driver.execute_cdp_cmd("Accessibility.enable", {})

    ax_tree = driver.execute_cdp_cmd("Accessibility.getFullAXTree", {})
    matched_elements = []

    # Role mapping like Playwright does
    role_mappings = {
        'textbox': ['textbox', 'combobox', 'searchbox'],  # includes input[type=text], input[type=password], etc.
        'button': ['button'],
        'checkbox': ['checkbox'],
        'radio': ['radio'],
        'link': ['link'],
        'heading': ['heading'],
        'listitem': ['listitem'],
        'list': ['list']
    }

    # Get the roles to match (including implicit ones)
    roles_to_match = role_mappings.get(role, [role])

    for node in ax_tree.get("nodes", []):
        node_role = node.get("role")
        
        # Extract the actual role value from the CDP format
        if isinstance(node_role, dict):
            actual_role = node_role.get("value")
        else:
            actual_role = node_role
            
        if actual_role not in roles_to_match:
            continue

        # Apply filters
        if filters:
            matched = True
            for key, expected in filters.items():
                # Extract property value, handling CDP format
                prop_value = None
                for prop in node.get("properties", []):
                    if prop.get("name") == key:
                        value = prop.get("value")
                        if isinstance(value, dict):
                            prop_value = value.get("value")
                        else:
                            prop_value = value
                        break
                
                # Handle boolean comparisons
                if isinstance(expected, bool):
                    if isinstance(prop_value, str):
                        prop_value = prop_value.lower() == "true"
                    elif isinstance(prop_value, bool):
                        pass  # Already boolean
                    else:
                        prop_value = False
                
                if prop_value != expected:
                    matched = False
                    break
            if not matched:
                continue

        if "backendDOMNodeId" not in node:
            continue

        try:
            backend_id = node["backendDOMNodeId"]

            described = driver.execute_cdp_cmd("DOM.describeNode", {
                "backendNodeId": backend_id
            })
            node_id = described["node"]["nodeId"]

            resolved = driver.execute_cdp_cmd("DOM.resolveNode", {
                "nodeId": node_id
            })

            element = driver.execute_script("return arguments[0];", resolved["object"])
            matched_elements.append(element)

        except Exception as e:
            print(f"Error resolving node: {e}")
            continue

    # If accessibility tree didn't find elements, try DOM fallback
    if not matched_elements:
        matched_elements = find_elements_by_role_dom_fallback(driver, role, **filters)
    
    return matched_elements


def find_element_by_role(driver, role, **filters):
    """
    Find a single element by ARIA role using the Accessibility tree (CDP) with DOM fallback.
    Similar to Playwright's page.getByRole() but returns the first matching element.

    Args:
        driver: Selenium WebDriver instance.
        role (str): The ARIA role to match (e.g. 'button', 'checkbox', 'textbox').
        filters (dict): Optional ARIA filters, e.g. name="Submit", checked=True.

    Returns:
        Single Selenium WebElement matching the criteria.
        
    Raises:
        NoSuchElementException: If no element is found.
    """
    from selenium.common.exceptions import NoSuchElementException
    
    elements = find_elements_by_role(driver, role, **filters)
    
    if not elements:
        # Create a descriptive error message
        filter_desc = ""
        if filters:
            filter_parts = [f"{k}='{v}'" for k, v in filters.items()]
            filter_desc = f" with {', '.join(filter_parts)}"
        
        raise NoSuchElementException(
            f"No element found with role '{role}'{filter_desc}"
        )
    
    return elements[0]
