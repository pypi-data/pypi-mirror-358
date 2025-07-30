import time
import logging
from pathlib import Path
from typing import Optional, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import vobject

import urllib.parse

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

class LinkedInRemoteAugmentor:
    """
    Automates LinkedIn profile contact info extraction using an existing Chrome login session.

    Requirements:
    - User must be already logged into LinkedIn in Chrome.
    - Chrome must be closed before starting this script (profile cannot be in use).
    """

    def __init__(self, chrome_user_data_dir: Path, chrome_profile: str = "Default"):
        """
        Initialize with path to Chrome user data and profile.

        :param chrome_user_data_dir: Base directory for Chrome user data (e.g., ~/.config/google-chrome)
        :param chrome_profile: Profile name within Chrome (e.g., 'Default', 'Profile 1')
        """
        self.chrome_user_data_dir = chrome_user_data_dir
        self.chrome_profile = chrome_profile
        self.driver: Optional[webdriver.Chrome] = None

    def start_driver(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Start Chrome WebDriver and ensure LinkedIn login.
        Reuses existing session if already logged in; otherwise, logs in using credentials.
        """
        logger.info("Launching Chrome with profile reuse...")

        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={self.chrome_user_data_dir}")
        options.add_argument(f"--profile-directory={self.chrome_profile}")
        options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options
        )

        logger.info("Chrome WebDriver started.")
        self.driver.get("https://www.linkedin.com/feed/")
        time.sleep(3)

        # Check if we are already logged in
        if "login" in self.driver.current_url:
            logger.info("Not logged in — attempting login.")
            if not username or not password:
                raise ValueError("Login required but no credentials provided.")
            self.driver.get("https://www.linkedin.com/login")

            try:
                email_field = self.driver.find_element(By.ID, "username")
                password_field = self.driver.find_element(By.ID, "password")
                email_field.send_keys(username)
                password_field.send_keys(password)
                password_field.send_keys(Keys.RETURN)
                time.sleep(5)
                logger.info("Login attempt complete.")
            except NoSuchElementException:
                logger.error("Login page elements not found. Login failed.")
        else:
            logger.info("Already logged in — continuing session.")


    def fetch_contact_info(self, linkedin_url: str) -> Dict[str, Optional[str]]:
        """
        Extract contact info (email, phone, website, etc.) from a LinkedIn profile's contact-info overlay.
        """
        if not self.driver:
            raise RuntimeError("WebDriver is not started. Call start_driver() first.")

        logger.info(f"Visiting LinkedIn profile: {linkedin_url}")
        self.driver.get(linkedin_url)
        time.sleep(3)

        contact_info: Dict[str, Optional[str]] = {
            "email": None,
            "phone": None,
            "website": None,
            "twitter": None,
            "address": None,
            "birthday": None,
            "profile_url": None,
        }

        try:
            contact_info_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "top-card-text-details-contact-info"))
            )
            contact_info_button.click()
            logger.debug("Clicked on contact info button.")

            #     DEBUGGING ---  Kept for Evolution
            # logger.debug("Capture the HTML after clicking")
            # html = self.driver.page_source
            # with open("/tmp/linkedin_modal_debug.html", "w") as f:
            #      f.write(html)
            
            time.sleep(2)
        except Exception as e:
            logger.warning(f"Could not click contact info button: {e}")
            return contact_info

        # Parse visible contact fields
        try:
            modal = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "artdeco-modal__content"))
            )

            links = modal.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href") or ""
                text = link.text.strip()

                #
                # NOTYET
                # June 14, 2025 Only email extraction works for now.
                #
                
                if href.startswith("mailto:"):
                    contact_info["email"] = text
                elif href.startswith("tel:"):
                    contact_info["phone"] = text
                elif "twitter.com" in href:
                    contact_info["twitter"] = href
                elif "linkedin.com/in/" in href:
                    contact_info["profile_url"] = href
                elif href.startswith("http"):
                    contact_info["website"] = href

            # Extract text spans for address and birthday
            spans = modal.find_elements(By.TAG_NAME, "span")
            for span in spans:
                text = span.text.strip()
                if "Birthday" in text:
                    contact_info["birthday"] = text.replace("Birthday", "").strip()
                elif "Address" in text:
                    contact_info["address"] = text.replace("Address", "").strip()

            logger.debug(f"Extracted contact info: {contact_info}")

        except Exception as e:
            logger.warning(f"Error extracting contact info details: {e}")

        return contact_info

    def stop_driver(self) -> None:
        """
        Stop the Chrome WebDriver and close browser.
        """
        if self.driver:
            logger.info("Closing Chrome WebDriver.")
            self.driver.quit()
            self.driver = None

