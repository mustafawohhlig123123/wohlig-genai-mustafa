import pinecone
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("pineconeapi")  
ENVIRONMENT = "us-west1"  
INDEX_NAME = "my-vector-index" 

if not API_KEY:
    raise ValueError("pineconeapi is missing. Make sure it's in the .env file and loaded correctly.")

def initialize_pinecone():
    # Create an instance of Pinecone with the API key
    pc = pinecone.Pinecone(api_key=API_KEY)
    print("Pinecone initialized.")
    return pc

# Create index if it doesn’t exist
def create_pinecone_index(pc):
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating index: {INDEX_NAME}")
        # Create index specification with ServerlessSpec
        spec = pinecone.ServerlessSpec(
            cloud="aws",  # Specify the cloud provider (e.g., AWS)
            region="us-east-1"  # Update to the region that works for your setup 
        )
        # Create the index using the spec
        pc.create_index(
            name=INDEX_NAME,
            dimension=2,  # Replace with your actual model dimension
            metric="cosine",  # Replace with your model metric
            spec=spec
        )
        time.sleep(10)  # Wait for index to be created
    else:
        print(f"Index {INDEX_NAME} already exists.")

# Check if the index exists
def check_if_index_exists(pc):
    indexes = pc.list_indexes().names()
    if INDEX_NAME in indexes:
        print(f"Index {INDEX_NAME} was successfully created.")
    else:
        print(f"Index {INDEX_NAME} was not found.")

# Initialize Pinecone and create index
pc = initialize_pinecone()
create_pinecone_index(pc)

# Verify if the index exists
check_if_index_exists(pc)
