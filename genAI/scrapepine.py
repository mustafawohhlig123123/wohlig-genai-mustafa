import os
import re
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv


load_dotenv()
openai_api_key = os.getenv("openaiprem")
pinecone_api_key = os.getenv("pineconeapi")

# Initialize OpenAI and Pinecone
client = OpenAI(api_key=openai_api_key)
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index("new-index")

app = Flask(__name__)

URLS = [
    "https://www.wohlig.com/",
    "https://about.google/intl/ALL_in/",
    "https://python.langchain.com/docs/introduction/"
]

def scrape_website(url):
    """Scrapes a website using Selenium and extracts title + first 5000 characters of content."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)
        page_title = driver.title
        page_text = driver.find_element(By.TAG_NAME, "body").text  # Extract text from <body>

        driver.quit()  # Close browser

        print(f"Scraped data from {url}")

        return {"url": url, "title": page_title, "content": page_text[:5000]}  # Limit text length
    except Exception as e:
        return {"url": url, "error": str(e)}

def split_text_into_chunks(text, min_words=250):
    """Splits text into chunks based on full stops, ensuring each chunk has at least min_words."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    word_count = 0

    for sentence in sentences:
        words = sentence.split()
        word_count += len(words)
        current_chunk.append(sentence)

        if word_count >= min_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            word_count = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def get_text_embedding(text):
    """Generates an embedding from the input text using OpenAI."""
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        embedding = response.data[0].embedding
        print("Embedding generated successfully.")
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None

def store_website_embeddings(url, content):
    """Splits website content into chunks, generates embeddings, and stores them in Pinecone."""
    text_chunks = split_text_into_chunks(content)

    for idx, chunk in enumerate(text_chunks):
        embedding = get_text_embedding(chunk)

        if embedding:
            try:
                index.upsert(
                    vectors=[
                        {
                            "id": f"{url}_chunk_{idx}",
                            "values": embedding,
                            "metadata": {"url": url, "text": chunk}
                        }
                    ],
                    namespace="web_scraped_data"
                )
                print(f"Chunk {idx} from {url} stored in Pinecone.")
            except Exception as e:
                print(f"Error inserting embedding into Pinecone: {str(e)}")

@app.route("/scrape", methods=["GET"])
def scrape():
    """Scrapes multiple URLs, generates embeddings, and stores them in Pinecone."""
    results = []
    for url in URLS:
        data = scrape_website(url)
        if "content" in data:
            store_website_embeddings(url, data["content"])
        results.append(data)
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
