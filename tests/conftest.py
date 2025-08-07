# General imports
import pytest
from selenium import webdriver

# Modern Selenium 4.6+ approach: Selenium Manager handles drivers automatically
import os

# Import options for headless mode
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="chrome", help="Send 'chrome' or 'firefox' as parameter for execution"
    )


@pytest.fixture()
def driver(request):
    browser = request.config.getoption("--browser")
    # Default driver value
    driver = ""
    
    # Setup
    print(f"\nSetting up: {browser} driver")
    if browser == "chrome":
        # Chrome options setup for headless mode
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # ✅ Enable BiDi for accessibility locators
        chrome_options.set_capability("webSocketUrl", True)
        
        # Modern approach: Use Selenium Manager (no webdriver-manager needed)
        driver = webdriver.Chrome(options=chrome_options)
        
    elif browser == "firefox":
        # Firefox options setup for headless mode
        firefox_options = FirefoxOptions()
        firefox_options.add_argument('--headless')
        
        # ✅ Enable BiDi for accessibility locators
        firefox_options.set_capability("webSocketUrl", True)
        
        # Modern approach: Use Selenium Manager (no webdriver-manager needed)
        driver = webdriver.Firefox(options=firefox_options)
        
    elif browser == "edge":
        # Edge options setup for headless mode
        edge_options = EdgeOptions()
        edge_options.add_argument('--headless')
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        
        # ✅ Enable BiDi for accessibility locators
        edge_options.set_capability("webSocketUrl", True)
        
        # Modern approach: Use Selenium Manager with Microsoft's official mirror
        os.environ["SE_DRIVER_MIRROR_URL"] = "https://msedgedriver.microsoft.com"
        driver = webdriver.Edge(options=edge_options)
    # Implicit wait setup for our framework
    driver.implicitly_wait(10)
    yield driver
    # Tear down
    print(f"\nTear down: {browser} driver")
    driver.quit()
