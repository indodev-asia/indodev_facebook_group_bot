#!/usr/bin/env python3

import time, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
)


LOGIN_FILE = "login.txt"
GROUPS_FILE = "groups.txt"
POST_FILE = "post.txt"

custom_user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
DRIVER_SERVICE = webdriver.chrome.service.Service()
OPTIONS = webdriver.ChromeOptions()

OPTIONS.add_argument("--disable-notifications")
OPTIONS.add_argument("--incognito") 
OPTIONS.add_argument(f"user-agent={custom_user_agent}")

def bot_banner():
    try:
        print("""
        \tIndoDev Facebook Bot 2025 
        \tDeveloped by Anton (Indodev - www.indodev.asia)
        \tDeveloped June 30 2025
        \tAutomatic posts to multiple groups to promote everything you want\n\n
        """)
    except Exception as e:
        raise e

def read_config_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please create it.")
        return None
    except Exception as e:
        print(f"Error reading '{file_path}': {e}")
        return None

def login_facebook(driver, email, password):
    print("Navigating to Facebook login page...")
    driver.get("https://www.facebook.com/")

    try:
        try:
            accept_cookies_button = WebDriverWait(driver, 7).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@data-testid='cookie-policy-dialog-accept-button']")
                )
            )
            accept_cookies_button.click()
            print("Accepted cookies.")
            time.sleep(2) 
        except TimeoutException:
            print("No cookie dialog found or already accepted.")

        email_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_input.send_keys(email)
        print("Entered email.")

        password_input = driver.find_element(By.ID, "pass")
        password_input.send_keys(password)
        print("Entered password.")

        login_button = driver.find_element(By.NAME, "login")
        login_button.click()
        print("Clicked login button.")
        time.sleep(2)
        WebDriverWait(driver, 10).until(
            EC.url_contains("facebook.com")
        )
        print("Login attempt completed.")
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Facebook']"))
            )
            print("Successfully logged into Facebook.")
            return True
        except TimeoutException:
            print("Login failed: Could not find home page elements. Check credentials or manual intervention needed.")
            return False

    except NoSuchElementException as e:
        print(f"Login Error: Element not found - {e}")
        return False
    except TimeoutException as e:
        print(f"Login Error: Timed out waiting for element - {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during login: {e}")
        return False

def post_to_group(driver, group_url, post_content):
    print(f"\n--- Attempting to post to group: {group_url} ---")
    try:
        driver.get(group_url)
        WebDriverWait(driver, 30).until(
            EC.url_contains(group_url.split('/')[-2]) 
        )
        print("Group page loaded.")

        try:
            post_area = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(), 'Write something') or contains(text(), 'Tulis sesuatu')]")
                )
            )
            post_area.click()
            print("Clicked 'Write something...' area.")
        except TimeoutException:
            print("Could not find 'Write something...' area directly. Trying alternative (e.g., 'What's on your mind?')...")
            try:
                post_area = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//div[@role='button' and @aria-label=\"Create a public post\" or @aria-label=\"Apa yang Anda pikirkan?\"]")
                    )
                )
                post_area.click()
                print("Clicked 'Create a public post' area.")
            except TimeoutException:
                print("Could not find any post creation area. Skipping this group.")
                return False

        try:
            time.sleep(3)
            wait = WebDriverWait(driver, 10)
            post_composer_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-lexical-editor='true']")))
            
            print("Post composer modal appeared.")
        except Exception as e:
            print("[-] failed to locate post composer")
            raise e
        try:
            try:
                post_composer_input.send_keys(post_content)
            except:
                post_composer_input.send_keys(post_content)
                pass
            print("Entered post content.")
        except Exception as e:
            print("[-] failed to post")
            raise e
        time.sleep(4) 
        try:
            post_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@role='button' and contains(@aria-label, 'Post') or contains(text(), 'Post')]")
                )
            )
            post_button.click()
            print("Clicked 'Post' button.")
            time.sleep(4) 
            print(f"Successfully attempted to post to {group_url}")
            return True
        except TimeoutException:
            print("Post button not found or not clickable within the modal. Skipping this group.")
            return False
        except ElementNotInteractableException:
            print("Post button found but not interactable. It might be disabled or covered. Skipping this group.")
            return False

    except TimeoutException as e:
        print(f"Timeout while loading group {group_url} or finding elements: {e}")
        raise e
        
    except NoSuchElementException as e:
        print(f"Element not found on group {group_url} page: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while posting to {group_url}: {e}")
        return False

def main():
    bot_banner()
    time.sleep(4)
    print("[+] reading login credentials")
    login_credentials = read_config_file(LOGIN_FILE)
    if not login_credentials or len(login_credentials) < 2:
        print(f"Please ensure '{LOGIN_FILE}' contains your Facebook email on the first line and password on the second line.")
        return

    email = login_credentials[0]
    password = login_credentials[1]

    group_urls = read_config_file(GROUPS_FILE)
    if not group_urls:
        print(f"Please ensure '{GROUPS_FILE}' contains a list of Facebook group URLs, one per line.")
        return

    post_content_lines = read_config_file(POST_FILE)
    if not post_content_lines:
        print(f"Please ensure '{POST_FILE}' contains the content you want to post.")
        return
    post_content = "\n".join(post_content_lines)

    driver = None
    try:
        driver = webdriver.Chrome(service=DRIVER_SERVICE, options=OPTIONS)
        driver.maximize_window() 
        print("[+] login to facebook")
        if not login_facebook(driver, email, password):
            try:
                login_facebook(driver, email, password)
            except:
                print("Failed to log in to Facebook. Exiting.")
                return

        for url in group_urls:
            post_to_group(driver, url, post_content)
            time.sleep(5) 

    except Exception as e:
        print(f"An unhandled error occurred: {e}")
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    main()
