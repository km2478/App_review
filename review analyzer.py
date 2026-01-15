import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1"
}


def fetch_amazon_reviews(product_url, pages=2):
    reviews = []

    if "/dp/" in product_url:
        product_id = product_url.split("/dp/")[1].split("/")[0]
    else:
        print("Invalid Amazon URL")
        return []

    for page in range(1, pages + 1):
        review_url = f"https://www.amazon.in/product-reviews/{product_id}?pageNumber={page}"
        response = requests.get(review_url, headers=HEADERS, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        review_blocks = soup.select("div[data-hook='review']")

        for block in review_blocks:
            review_text = block.select_one("span[data-hook='review-body']")
            rating = block.select_one("i[data-hook='review-star-rating']")

            if review_text and rating:
                reviews.append({
                    "review": review_text.text.strip(),
                    "rating": float(rating.text.split()[0])
                })

    return reviews


def analyze_reviews(reviews):
    quality_keywords = ["quality", "build", "material", "durable", "finish"]
    quality_count = 0
    sentiment_score = 0

    for r in reviews:
        text = r["review"].lower()
        sentiment_score += TextBlob(text).sentiment.polarity

        if any(word in text for word in quality_keywords):
            quality_count += 1

    common_count = len(reviews) - quality_count

    return {
        "Quality Related": quality_count,
        "Common Reviews": common_count,
        "Average Sentiment": sentiment_score / len(reviews)
    }


def plot_pie(result):
    labels = ["Quality Related", "Common Reviews"]
    sizes = [result["Quality Related"], result["Common Reviews"]]

    plt.figure()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title("Review Distribution")
    plt.show()

def save_to_excel(reviews):
    df = pd.DataFrame(reviews)
    df.to_excel("reviews.xlsx", index=False)
    print("✔ Reviews saved to reviews.xlsx")
    
def fetch_flipkart_reviews(product_url, pages=2):
    reviews = []

    for page in range(1, pages + 1):
        review_url = product_url + f"?page={page}"
        response = requests.get(review_url, headers=HEADERS, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        blocks = soup.find_all("div", class_="_27M-vq")

        for block in blocks:
            rating = block.find("div", class_="_3LWZlK")
            review_text = block.find("div", class_="t-ZTKy")

            if rating and review_text:
                reviews.append({
                    "review": review_text.text.strip(),
                    "rating": float(rating.text.strip())
                })

    return reviews

if __name__ == "__main__":
    product_link = input("Enter Product Link: ")

    if "amazon" in product_link.lower():
        reviews = fetch_amazon_reviews(product_link)

    elif "flipkart" in product_link.lower():
        reviews = fetch_flipkart_reviews(product_link)

    else:
        print("❌ Website not supported yet")
        exit()
        
    if len(reviews) == 0:
        print("No reviews found.")
        exit()

    result = analyze_reviews(reviews)

    print("\n📊 Review Summary")
    for k, v in result.items():
        print(f"{k}: {v}")

    plot_pie(result)
    save_to_excel(reviews)