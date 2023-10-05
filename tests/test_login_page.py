import time


class TestLoginpage:
    def test_valid_login(self, driver):
        driver.get("https://www.google.com")
        time.sleep(10)
