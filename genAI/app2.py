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

def get_text_embedding(text):
    "Generates an embedding from the input text using OpenAI."
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"  
        )
        embedding = response.data[0].embedding
        print("Query embedding generated successfully.")
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None

def retrieve_similar_context(query, top_k=5):
    "Retrieves the top K most similar chunks from Pinecone."
    query_embedding = get_text_embedding(query)
    
    if not query_embedding:
        return []
    
    try:
        # Search Pinecone for similar vectors
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace="new_namespace"  # Ensure same namespace as storage
        )
        contexts = [match['metadata']['text'] for match in results['matches']]
        print(f"Retrieved {len(contexts)} relevant context chunks.")
        return contexts
    except Exception as e:
        print(f"Error retrieving context from Pinecone: {str(e)}")
        return []

def generate_answer(query):
    "Retrieves relevant context and generates an answer using OpenAI."
    contexts = retrieve_similar_context(query)
    
    if not contexts:
        return "I couldn't find relevant information in the document."

    # Combine context into a single string for the prompt
    context_text = "\n\n".join(contexts)
    
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the question based on the retrieved context."},
        {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion:\n{query}\n\nAnswer:"}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4",  
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        return "An error occurred while generating the answer."

query = "Where does Mustafa work?"

answer = generate_answer(query)
print("\nGenerated Answer:\n", answer)

