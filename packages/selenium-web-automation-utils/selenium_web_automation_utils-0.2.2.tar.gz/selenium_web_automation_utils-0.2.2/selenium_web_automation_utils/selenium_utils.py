import os
import random
from contextlib import contextmanager, redirect_stderr
from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from selenium_web_automation_utils.logging_utils import print_error

try:
    import undetected_chromedriver as uc
except ImportError:
    uc = None


@contextmanager
def stderr_to_null():
    """
    Context manager to suppress stderr output temporarily.
    """
    with open(os.devnull, 'w') as devnull_file:
        with redirect_stderr(devnull_file):
            yield


@contextmanager
def get_webdriver(implicitly_wait_seconds=5,
                  user_agent=None,
                  user_profile_path=None,
                  disable_webdriver_detection: bool = True,
                  suppress_stderr: bool = True,
                  download_dir=None,
                  chrome_extensions: list = None,
                  use_guest_profile: bool = False,
                  mobile_emulation: bool = False,
                  use_undetected: bool = False,
                  headless: bool = False):  # ← added
    """
    Context manager that provides a Selenium webdriver instance.
    Supports stealth browsing via undetected-chromedriver.

    This function creates a new Chrome webdriver instance and yields it to the caller.
    When the caller is done with the webdriver, it will automatically quit the driver.

    :param implicitly_wait_seconds: The amount of time (in seconds) to wait when trying to locate elements on the page
    :param user_agent: Custom user agent (Google for 'What is my user agent')
    :param user_profile_path: Profile Path from chrome://version/
    :param disable_webdriver_detection: Disable Webdriver detection
    :param suppress_stderr: Suppress stderr to devnull
    :param download_dir: Custom download directory for Chrome
    :param chrome_extensions: List of chrome extensions to be added
    :param use_guest_profile: Launch Chrome in Guest mode
    :param mobile_emulation: Switches to a mobile screensize
    :param use_undetected: uses undetected-chromedriver
    :param headless: run Chrome in headless mode (in addition to CI forcing headless)
    :return: webdriver.Chrome: A new Chrome webdriver instance.
    """
    if use_undetected and uc is None:
        raise ImportError("undetected-chromedriver is not installed. Run: pip install undetected-chromedriver")

    # Choose appropriate options object
    options = uc.ChromeOptions() if use_undetected else webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])  # Disable logging
    options.add_argument("log-level=3")  # Set log level to ERROR to reduce verbosity
    options.add_argument("--silent")  # Suppresses log messages from ChromeDriver

    # Set custom download directory if provided
    if download_dir:
        download_dir_path = str(Path(download_dir).resolve())
        prefs = {
            "download.default_directory": download_dir_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)

    # Add chrome extensions
    if chrome_extensions:
        for extension in chrome_extensions:
            options.add_extension(extension)

    if user_agent:
        options.add_argument(f"user-agent={user_agent}")

    # Force headless mode in CI/CD environments or if explicitly requested
    if os.getenv("CI") or headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    else:
        if use_guest_profile:
            options.add_argument("--guest")
        elif user_profile_path:
            user_profile = Path(user_profile_path)
            options.add_argument(f"user-data-dir={user_profile.parent}")
            options.add_argument(f"profile-directory={user_profile.name}")

    if disable_webdriver_detection and not use_undetected:
        options.add_argument("--disable-blink-features=AutomationControlled")

    if mobile_emulation:
        options.add_experimental_option("mobileEmulation", {
            "deviceMetrics": {"width": 360, "height": 740, "pixelRatio": 4},
            "userAgent": (
                "Mozilla/5.0 (Linux; Android 7.0; SM-G950U Build/NRD90M; wv) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.91 Mobile Safari/537.36"
            )
        })

    # Create driver
    if use_undetected:
        driver = uc.Chrome(options=options)
    else:
        if suppress_stderr:
            with stderr_to_null():
                driver = webdriver.Chrome(options=options)
        else:
            driver = webdriver.Chrome(options=options)

    if disable_webdriver_detection and not use_undetected:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.implicitly_wait(implicitly_wait_seconds)

    try:
        yield driver
    finally:
        driver.quit()


def find_element_wait(driver,
                      by: str,
                      locator, timeout=10, raise_exception=True):
    """
    Find an element on a web page and wait for it to be clickable.

    Args:
        driver (webdriver.Chrome): The webdriver instance to use.
        by (str): The locator strategy to use (See: selenium.webdriver.common.by)
        locator (str): The locator value to use with the specified strategy.
        timeout (int, optional): The maximum time to wait for the element to be clickable. Defaults to 30.
        raise_exception (bool, optional): Whether to raise an exception if the element is not found. Defaults to True.

    Returns:
        webdriver.WebElement: The found element.

    Raises:
        Exception: If the element is not found and raise_exception is True.
    """
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
    except Exception as e:
        if raise_exception:
            raise e


def find_element_by_text(driver, tag, text, anywhere_incl_children=True, timeout=10, raise_exception=True):
    """
        Find an element on a web page by text and wait for it to be clickable.

        Args:
            driver (webdriver.Chrome): The webdriver instance to use.
            tag (str): The HTML tag to search for.
            text (str): The text to search for within the element.
            anywhere_incl_children (bool, optional): Search for text anywhere in element or direct node only (if False).
            timeout (int, optional): The maximum time to wait for the element to be clickable. Defaults to 30.
            raise_exception (bool, optional): Whether to raise an exception if element is not found. Defaults to True.

        Returns:
            webdriver.WebElement: The found element.

        Raises:
            Exception: If the element is not found and raise_exception is True.
        """
    if anywhere_incl_children:
        xpath = f"//{tag}[contains(., '{text}')]"
    else:
        xpath = f"//{tag}[contains(text(), '{text}')]"
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except Exception as e:
        if raise_exception:
            raise e


def find_element_until_none(driver, xpath, timeout=10):
    """
    Generator function that yields elements found by the specified XPath expression until no more elements are found.

    Parameters:
    - driver: The WebDriver instance used to perform the search.
    - xpath: The XPath expression used to locate elements.
    - timeout: Maximum time (in secs) to wait for the element to appear before considering it not found (default: 10).

    Yields:
    - WebElement: The found WebElement that matches the XPath expression.

    Exceptions:
    - Prints an error message if an exception occurs during element search.
    - Stops yielding elements when no more elements are found or an exception is raised.

    Example:
    >>> for element in find_element_until_none(driver, "//*[local-name()='svg' and @aria-label='Go back']"):
    >>>     element.click()
    """
    while True:
        try:
            yield find_element_wait(driver, By.XPATH, xpath, timeout=timeout, raise_exception=True)
        except Exception as e:
            print(f"No longer able to find element with xpath: {xpath}. {repr(e)}")
            return


# Helper function to add random delays
def human_delay(min_delay=0.1, max_delay=0.5):
    sleep(random.uniform(min_delay, max_delay))


def type_keys(web_element: WebElement, message: str, min_delay: int = 50, max_delay: int = 200):
    """
    Types a message into a web element character by character with a random delay between keystrokes.

    Parameters:
    - web_element: The WebElement where the message will be typed.
    - message: The string message to be typed into the web element.
    - min_delay: Minimum time delay between keystrokes in milliseconds.
    - max_delay: Maximum time delay between keystrokes in milliseconds.

    Returns:
    - None: This function does not return any value.

    Example:
    >>> type_keys(web_element, "Hello World")
    """
    for char in message:
        web_element.send_keys(char)
        # Introduce a new random delay between keystrokes
        sleep(random.randint(min_delay, max_delay) / 1000)


def scroll_randomly(driver, min_scrolls=1, max_scrolls=5):
    scrolls = random.randint(min_scrolls, max_scrolls)
    for _ in range(scrolls):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")  # Scroll down
        human_delay(1, 3)  # Random delay between scrolls


def move_mouse_randomly(driver):
    """Simulate random mouse movements to mimic human behavior."""
    width = driver.execute_script("return window.innerWidth")
    height = driver.execute_script("return window.innerHeight")

    # Get current mouse position
    current_x = driver.execute_script("return window.scrollX")
    current_y = driver.execute_script("return window.scrollY")

    # Generate random offsets within the bounds of the viewport
    x_offset = random.randint(-int(width / 4), int(width / 4))
    y_offset = random.randint(-int(height / 4), int(height / 4))

    # Calculate new mouse position
    new_x = current_x + x_offset
    new_y = current_y + y_offset

    # Ensure the new position is within the bounds of the viewport
    new_x = max(0, min(new_x, width - 1))
    new_y = max(0, min(new_y, height - 1))

    # Move the mouse to the calculated position
    try:
        ActionChains(driver).move_by_offset(new_x - current_x, new_y - current_y).perform()
    except Exception as e:
        print_error(repr(e))
    human_delay()  # Pause after moving the mouse


def clean_error_str(e: Exception):
    return str(e).split('Stacktrace')[0].strip()
