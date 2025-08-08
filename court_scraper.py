import time
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import cv2
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def fetch_case_details(case_types, case_number, case_year):
    brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    chrome_driver_path = "C:/WebDrivers/chromedriver-win64/chromedriver.exe"

    options = Options()
    options.binary_location = brave_path
    # options.add_argument('--headless')  # You can enable this if you don't want the browser window to open
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("Opening Delhi High Court website...")
        driver.get("https://delhihighcourt.nic.in/app/get-case-type-status")

        print("Waiting for dropdown...")
        dropdown = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, 'case_type'))
        )
        Select(dropdown).select_by_visible_text(case_types)

        driver.find_element(By.ID, 'case_number').send_keys(case_number)
        driver.find_element(By.ID, 'case_year').send_keys(case_year)

        print("⚠️ Solving CAPTCHA (2 seconds)")
        time.sleep(2)

        captcha_element = driver.find_element(By.ID, "captcha-code")
        captcha_element.screenshot("captcha.png")

        # Read and preprocess image
        img = cv2.imread("captcha.png")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Removed comma!
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # OCR configuration
        custom_config = r'--psm 8 -c tessedit_char_whitelist=0123456789'
        captcha_text = pytesseract.image_to_string(thresh, config=custom_config).strip()

        print("Extracted CAPTCHA:", captcha_text)

        # Input CAPTCHA
        driver.find_element(By.ID, "captchaInput").send_keys(captcha_text)

        # Click search
        driver.find_element(By.ID, 'search').click()

        # Wait for search results
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="caseTable"]/tbody/tr[1]/td[2]/a[2]'))
        )
        driver.find_element(By.XPATH, '//*[@id="caseTable"]/tbody/tr[1]/td[2]/a[2]').click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="caseTable"]/tbody/tr[1]/td[2]/a'))
        )

        pdf_link = driver.find_element(By.XPATH, '//*[@id="caseTable"]/tbody/tr[1]/td[2]/a').get_attribute('href')
        print(f"✅ PDF URL found: {pdf_link}")

        return pdf_link

    except Exception as e:
        print(f"❌ Error: {e}")
        return f"❌ An error occurred: {str(e)}"

    finally:
        driver.quit()
