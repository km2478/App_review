from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import os

# OPEN BROWSER
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# SAFE ANALYSIS FUNCTION
def analyze_reviews(reviews):
    if len(reviews) == 0:
        return {
            "Quality Related": 0,
            "Common Reviews": 0,
            "Average Sentiment": 0
        }

    quality_words = ["quality", "build", "material", "durable", "strong"]
    quality_count = 0
    sentiment = 0

    for r in reviews:
        text = r["review"].lower()
        sentiment += TextBlob(text).sentiment.polarity
        if any(w in text for w in quality_words):
            quality_count += 1

    return {
        "Quality Related": quality_count,
        "Common Reviews": len(reviews) - quality_count,
        "Average Sentiment": sentiment / len(reviews)
    }

# LOAD PRODUCT PAGE
product_url = input("Enter Flipkart Product Link: ")
driver.get(product_url)

time.sleep(15)  #

driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
time.sleep(5)

# Try to open reviews page
elements = driver.find_elements(By.XPATH, "//span | //a | //button")
for e in elements:
    try:
        if "review" in e.text.lower():
            driver.execute_script("arguments[0].click();", e)
            time.sleep(6)
            break
    except:
        pass

# SCRAPE REVIEWS
reviews = []

for page in range(2):  # scrape 2 pages
    time.sleep(5)
    review_blocks = driver.find_elements(By.XPATH, "//div[contains(@class,'_27M')]")

    for block in review_blocks:
        try:
            rating = block.find_element(By.XPATH, ".//div[contains(@class,'_3LWZlK')]").text
            text = block.find_element(By.XPATH, ".//div[contains(@class,'t-ZTKy')]").text

            reviews.append({
                "rating": rating,
                "review": text
            })
        except:
            continue

    try:
        next_btn = driver.find_element(By.XPATH, "//span[text()='Next']")
        next_btn.click()
    except:
        break

driver.quit()

print(f"Fetched {len(reviews)} reviews")

# ANALYSIS

result = analyze_reviews(reviews)

# PLOT PIE CHART

if len(reviews) > 0:
    plt.figure()
    plt.pie(
        [result["Quality Related"], result["Common Reviews"]],
        labels=["Quality Related", "Common Reviews"],
        autopct="%1.1f%%"
    )
    plt.title("Flipkart Review Distribution")
    plt.show()
else:
    print("No reviews found to plot.")

# SAVE TO EXCEL

if len(reviews) == 0:
    print("No reviews to save.")
else:
    # Folder path
    folder_path = r"C:/Users/siroy/Downloads/Kunal/review project/"
    os.makedirs(folder_path, exist_ok=True)

    # File path
    file_path = os.path.join(folder_path, "flipkart_reviews.xlsx")

    # Save Excel
    df = pd.DataFrame(reviews)
    df.to_excel(file_path, index=False)
    print(f"Saved to {file_path}")
