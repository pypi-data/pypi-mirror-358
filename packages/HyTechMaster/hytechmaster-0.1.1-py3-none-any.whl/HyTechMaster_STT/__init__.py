# pip install selenium webdriver-manager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
# pip install webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager   
from os import getcwd



# setting up Chrome options with specific arguments
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--use-fake-ui-for-media-stream")   # allow mic without prompt :contentReference[oaicite:1]{index=1}
chrome_options.add_argument("--headless=new")  # uncomment if you need headless

# setting up the Chrome driver with WebDriverManager and options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)

# creati ng the URL for the website using the current working directory 
website = "https://allorizenproject1.netlify.app/"

# opening the website in the Chrome browser
driver.get(website)

rec_file = f"{getcwd()}\\input.txt"

def listen():
    try:
        start_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'startButton'))  # explicit wait pattern :contentReference[oaicite:2]{index=2}
        )
        start_button.click()
        print("Listening…")

        last_words = []

        while True:
            output_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'output'))
            )
            current_words = output_element.text.split()

            # if transcript changed, write to file (join first, then lower) :contentReference[oaicite:3]{index=3}
            if current_words and current_words != last_words:
                last_words = current_words
                line = " ".join(current_words).lower()
                with open(rec_file, "w", encoding="utf-8") as f:
                    f.write(line)
                print("Arman Rathore :", line)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("listen() error →", e)

print("Entering listening loop…")
listen()
