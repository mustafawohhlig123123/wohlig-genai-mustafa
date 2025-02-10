import os
import fitz  # PyMuPDF for extracting text from PDFs
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
import re

load_dotenv()
openai_api_key = os.getenv("openaiprem")
pinecone_api_key = os.getenv("pineconeapi")

# Initialize OpenAI and Pinecone
client = OpenAI(api_key=openai_api_key)
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index("new-index")  

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + " "
        print("PDF text extracted successfully.")
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
    return text

def split_text_into_chunks(text, min_words=250):
    """Splits text into chunks based on full stops, ensuring each chunk has at least min_words."""
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Split at full stops, exclamation, and question marks
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

def store_pdf_embeddings(pdf_path):
    """Extracts text from a PDF, generates embeddings, and stores them in Pinecone."""
    text = extract_text_from_pdf(pdf_path)
    text_chunks = split_text_into_chunks(text)

    for idx, chunk in enumerate(text_chunks):
        embedding = get_text_embedding(chunk)
        
        if embedding:
            try:
                index.upsert(
                    vectors=[
                        {
                            "id": f"pdf_chunk_{idx}",  # Unique ID for each chunk
                            "values": embedding,
                            "metadata": {"text": chunk}
                        }
                    ],
                    namespace="new_namespace"
                )
                print(f"Chunk {idx} inserted into Pinecone successfully.")
            except Exception as e:
                print(f"Error inserting embedding into Pinecone: {str(e)}")

pdf_file_path = "pdfforvector.pdf"

if os.path.exists(pdf_file_path):
    store_pdf_embeddings(pdf_file_path)
else:
    print(f"Error: File '{pdf_file_path}' not found!")
