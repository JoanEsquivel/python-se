# General imports
import pytest
from selenium import webdriver

# Modern Selenium 4.6+ approach: Selenium Manager handles drivers automatically
import os

# Import options for headless mode
from selenium.webdriver.chrome.options import Options


def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="chrome", help="Send 'chrome' or 'firefox' as parameter for execution"
    )


@pytest.fixture()
def driver(request):
    browser = request.config.getoption("--browser")
    # Default driver value
    driver = ""
    # Option setup to run in headless mode (in order to run this in GH Actions)
    options = Options()
    # options.add_argument('--headless')
    # Setup
    print(f"\nSetting up: {browser} driver")
    if browser == "chrome":
        # Modern approach: Use Selenium Manager (no webdriver-manager needed)
        driver = webdriver.Chrome(options=options)
    elif browser == "firefox":
        # Modern approach: Use Selenium Manager (no webdriver-manager needed)
        driver = webdriver.Firefox()
    elif browser == "edge":
        # Modern approach: Use Selenium Manager with Microsoft's official mirror
        os.environ["SE_DRIVER_MIRROR_URL"] = "https://msedgedriver.microsoft.com"
        driver = webdriver.Edge()
    # Implicit wait setup for our framework
    driver.implicitly_wait(10)
    yield driver
    # Tear down
    print(f"\nTear down: {browser} driver")
    driver.quit()
