# General imports
import pytest
from selenium import webdriver

# Imports to get chrome driver working
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Imports to get firefox driver working
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

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
    options.add_argument('--headless')
    # Setup
    print(f"\nSetting up: {browser} driver")
    if browser == "chrome":
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    elif browser == "firefox":
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    # Implicit wait setup for our framework
    driver.implicitly_wait(10)
    yield driver
    # Tear down
    print(f"\nTear down: {browser} driver")
    driver.quit()
