# Python Selenium Project

This is a set of instructions to set Selenium with Python for the first time:

## First Time installation using venv (Windows)

### Create a virtual environment

- Install [Python](https://www.python.org/downloads/)
- Make sure pip was installed running the command

```bash
  pip -V
```

- Install virtualenv

```bash
  py -m pip install --user virtualenv
```
- Create a new virtual environment

```
   python -m venv se-python-env
```

- Activate it

```bash
cd se-python-env/Scripts
activate
```

### Configure the project using PyCharm

- Download [PyCharm](https://www.jetbrains.com/pycharm/download/?section=windows)
- Click on "New Project"
- Change the project name
- Select "Previously configured interpreter"
- Click on "Add Interpreter"
- In the environment section select "Existing"
- Look for the folder where you created your virtual env and select \se-python-env\Scripts\python.exe
- Wait for a few seconds until project is configured.

### Setup requirements

- Create a requirements.txt file in the root.
- Add the pytest requirement: https://docs.pytest.org/en/7.4.x/getting-started.html

```
  pytest==7.4.2
```

- Add the Selenium requirement: https://pypi.org/project/selenium/#history

```
  selenium==4.13.0
```

- Add the webdriver manager requirement: https://pypi.org/project/webdriver-manager/#history

```
  webdriver-manager==4.0.1
```

### Setup Conftest

- Create a test folder
- Under the test folder create the file named "conftest.py"
- Create a way to receive browser parameter from console based on documentation: https://docs.pytest.org/en/7.1.x/example/simple.html

```
  def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="chrome", help="Send 'chrome' or 'firefox' as parameter for execution"
    )
```

- Then create a general fixture for setup & tear download (notice the request parameter comes from the pytest_addoption method)

```
  @pytest.fixture()
  def driverSetup(request):
      browser = request.config.getOption("--browser")
      # Default driver value
      driver = "chrome"
      # Setup
      print(f"Setting up: {browser} driver")
      if browser == "chrome":
          driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
      elif browser == "firefox":
          driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
      yield driver
      # Tear down
      print(f"Tear down: {browser} driver")
      driver.quit()
```

### Type, Click, and validate URL example

```
    def test_valid_login(self, driver):
        driver.get("https://www.saucedemo.com/")
        time.sleep(2)

        # Type username
        username_input = driver.find_element(By.ID, "user-name")
        username_input.send_keys("standard_user")

        # Type password
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys("secret_sauce")

        # Click on the login button
        login_btn = driver.find_element(By.ID, "login-button")
        login_btn.click()

        # URL Validation
        actual_url = driver.current_url
        assert actual_url == "https://www.saucedemo.com/inventory.html"
```

### Send parameters to tests using Pytest
We can send parameters to functions following the guide in the official doc. Reference: https://docs.pytest.org/en/7.3.x/how-to/parametrize.html
Check this example where the same example is going to be executed twice with two set of data: 

```
 @pytest.mark.parametrize("username, password, error", [
        ("locked_out_user", "secret_sauce", "Epic sadface: Sorry, this user has been locked out."),
        ("invalidUser", "invalidPass", "Epic sadface: Username and password do not match any user in this service")])
    
    def test_invalid_login(self, driver, username, password, error):
        driver.get("https://www.saucedemo.com/")

        # Type username
        username_input = driver.find_element(By.ID, "user-name")
        username_input.send_keys(username)

        # Type password
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(password)

        # Click on the login button
        login_btn = driver.find_element(By.ID, "login-button")
        login_btn.click()

        # Error message validation
        error_msg_h3 = driver.find_element(By.TAG_NAME, "h3")
        error_msg_text = error_msg_h3.text
        assert error_msg_text == error


```

### Let's add a report library
Library: https://pypi.org/project/pytest-html/

If you want to add the report just add to the "requirements.txt" the following line(check the version you want to implement):
```
    pytest-html==4.0.2
```
#### How to configure it in your PyCharm?
- Create a folder named "reports"
- Add to the execution the following "Additional Arguments":
```
    --html=reports/automation-report-(BROWSER)-.html
```

## Contributing

Contributions are always welcome!

See `contributing.md` for ways to get started.

Please adhere to this project's `code of conduct`.

## License

[MIT](https://choosealicense.com/licenses/mit/)
