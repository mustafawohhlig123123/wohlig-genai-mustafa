import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()
openai_api_key = os.getenv("openaiprem")
pinecone_api_key = os.getenv("pineconeapi")

client = OpenAI(api_key=openai_api_key)
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index("new-index")  

def get_text_embedding(text):
    try:
        # Request embedding from OpenAI API
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"  
        )
        embedding = response.data[0].embedding
        print("Embedding generated successfully.")
        # print(embedding)
        return embedding
    
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None

sample_text = "I am currently studying"
embedding = get_text_embedding(sample_text)

# Insert generated embedding into Pinecone if embedding was successful
if embedding:
    try:
        index.upsert(
            vectors=[
                {
                    "id": "sample_text_vec",  # Unique ID for the embedding
                    "values": embedding,  # The embedding vector
                    "metadata": {"text": sample_text}  # Metadata (e.g., original text)
                }
            ],
            namespace="new_namespace"  
        )
        print(" Embedding inserted into Pinecone successfully.")
    except Exception as e:
        print(f" Error inserting embedding into Pinecone: {str(e)}")

response = index.query(
    namespace="new_namespace",  # Query the newly inserted namespace
    vector=embedding,  # Use the generated embedding vector
    top_k=3,  # Retrieve top 3 closest vectors
    include_values=True,  # Include vector values in the response
    include_metadata=True,  # Include metadata in the response
)

print("Query Results:", response)
