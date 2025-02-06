import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()
pinecone_api_key = os.getenv("pineconeapi")
pc = Pinecone(api_key=pinecone_api_key)


index = pc.Index("my-vector-index")  # Use your index name here

# Insert vectors into the index
index.upsert(
    vectors=[
        {
            "id": "vec1", 
            "values": [1.0, 1.5], 
            "metadata": {"genre": "drama"}
        }, {
            "id": "vec2", 
            "values": [2.0, 1.0], 
            "metadata": {"genre": "action"}
        }, {
            "id": "vec3", 
            "values": [0.1, 0.3], 
            "metadata": {"genre": "drama"}
        }, {
            "id": "vec4", 
            "values": [1.0, -2.5], 
            "metadata": {"genre": "action"}
        }
    ],
    namespace="ns1"
)

# Query the index with a vector and filter by genre
response = index.query(
    namespace="ns1", 
    vector=[0.1, 0.3], 
    top_k=3,  
    include_values=True,  
    include_metadata=True,  
    filter={"genre": {"$eq": "action"}},  
)
print(response)
