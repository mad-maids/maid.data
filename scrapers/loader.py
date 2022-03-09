"""Logging is configured and instance of the webdriver is launched here."""

import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format="#%(levelname)-8s %(message)s")

# Workflow is failing if the browser window is not maximized.
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# create an instance of and launch chrome webdriver
browser = webdriver.Chrome(options=chrome_options)
