import os
from pinecone import Pinecone
from dotenv import load_dotenv

# Load API keys from environment variables
load_dotenv()
pinecone_api_key = os.getenv("pineconeapi")

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index("new-index")

def delete_all_records():
    """Deletes all records from the Pinecone index."""
    try:
        index.delete(delete_all=True, namespace="new_namespace")
        print("All records deleted successfully from Pinecone.")
    except Exception as e:
        print(f"Error deleting records from Pinecone: {str(e)}")

# Run the deletion function
delete_all_records()
