from helpers.parser import parse_api_response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
from selenium.webdriver.common.action_chains import ActionChains


def scrape_data(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Use new headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Realistic user-agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    # Connect to Selenium server in the Docker container
    selenium_url = "http://172.19.0.2:4444"  # Use the service name defined in the Docker Compose file

    # Set desired capabilities for Chrome
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:chromeOptions"] = {
        "args": ["--headless", "--disable-gpu", "--no-sandbox"],
    }

    # Set up the WebDriver to use the Selenium service
    driver = webdriver.Remote(
        command_executor=selenium_url,
        options=options,
        keep_alive=True,  # Keep the session alive
    )

    # Override navigator.webdriver
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            });
        """
        },
    )

    driver.get(f"{url}")  # No need to use view-source: — that doesn't work in headless

    # get content from pre
    content = driver.find_element(By.TAG_NAME, "pre").text

    json_data = json.loads(content)

    driver.quit()

    return json_data
