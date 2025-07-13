import os
import hashlib
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List
import time

load_dotenv()

# Global variables for reuse
pc = None
index = None
openai_client = None

def initialize_pinecone(api_key: str = None, index_name: str = "path-value-db"):
    """Initialize Pinecone connection and OpenAI client"""
    global pc, index, openai_client
    
    api_key = api_key or os.getenv('PINECONE_API_KEY')
    if not api_key:
        raise ValueError("Set PINECONE_API_KEY environment variable or pass api_key")
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("Set OPENAI_API_KEY environment variable")
    
    # Initialize Pinecone
    pc = Pinecone(api_key=api_key)

    print("\n\nindex list:", pc.list_indexes().names())
    
    # Create index if it doesn't exist
    if index_name not in pc.list_indexes().names():
        print(f"Creating index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=3072,  # text-embedding-3-large dimension
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        time.sleep(10)  # Wait for index to be ready
    
    # Connect to index
    index = pc.Index(index_name)
    
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=openai_api_key)
    
    print(f"Connected to Pinecone index: {index_name}")

def get_embedding(text: str) -> List[float]:
    """Get embedding from OpenAI text-embedding-3-large model"""
    global openai_client
    
    if openai_client is None:
        raise ValueError("OpenAI client not initialized. Call initialize_pinecone() first.")
    
    response = openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding

def upload_dict(data: Dict[str, str], api_key: str = None, index_name: str = "path-value-db"):
    """
    Upload a dictionary to Pinecone vector database
    
    Args:
        data: Dictionary with path as key and value as string
        api_key: Pinecone API key (optional if set in env)
        index_name: Name of the Pinecone index
    """
    global pc, index, openai_client
    
    # Initialize if not already done
    if pc is None or index is None or openai_client is None:
        initialize_pinecone(api_key, index_name)
    
    print(f"Uploading {len(data)} entries to vector database...")
    
    # Prepare vectors
    vectors = []
    for path, value in data.items():
        # Create embedding from combined path and value
        text = f"Path: {path} Content: {value}"
        embedding = get_embedding(text)
        
        # Create unique ID from path
        vector_id = hashlib.md5(path.encode()).hexdigest()
        
        vectors.append({
            'id': vector_id,
            'values': embedding,
            'metadata': {
                'path': path,
                'value': value
            }
        })
    
    # Upload in batches of 100
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Uploaded batch {i//batch_size + 1}/{(len(vectors) + batch_size - 1)//batch_size}")
    
    print(f"Successfully uploaded {len(vectors)} entries!")
    
    # Show stats
    stats = index.describe_index_stats()
    print(f"Total vectors in database: {stats['total_vector_count']}")

def query_db(query: str, k: int = 5, api_key: str = None, index_name: str = "path-value-db") -> List[Dict]:
    """
    Query the vector database
    
    Args:
        query: Search query string
        k: Number of results to return
        api_key: Pinecone API key (optional if set in env)
        index_name: Name of the Pinecone index
    
    Returns:
        List of dictionaries with path, value, and similarity score
    """
    global pc, index, openai_client
    
    # Initialize if not already done
    if pc is None or index is None or openai_client is None:
        initialize_pinecone(api_key, index_name)
    
    # Create query embedding
    query_embedding = get_embedding(query)
    
    # Search
    results = index.query(
        vector=query_embedding,
        top_k=k,
        include_metadata=True
    )
    
    # Format results
    formatted_results = []
    for match in results['matches']:
        formatted_results.append({
            'path': match['metadata']['path'],
            'value': match['metadata']['value'],
            'score': match['score']
        })
    
    return formatted_results