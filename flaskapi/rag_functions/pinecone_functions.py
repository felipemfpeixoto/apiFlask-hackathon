import os
import hashlib
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from typing import Dict, List
import time

load_dotenv()

# huggingface_hub login
from huggingface_hub import login
login(token=os.getenv('HUGGINGFACE_HUB_TOKEN'))

# Global variables for reuse
pc = None
index = None
model = None

def initialize_pinecone(api_key: str = None, index_name: str = "path-value-db"):
    """Initialize Pinecone connection and model"""
    global pc, index, model
    
    api_key = api_key or os.getenv('PINECONE_API_KEY')
    if not api_key:
        raise ValueError("Set PINECONE_API_KEY environment variable or pass api_key")
    
    # Initialize Pinecone
    pc = Pinecone(api_key=api_key)
    
    # Create index if it doesn't exist
    if index_name not in pc.list_indexes().names():
        print(f"Creating index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=384,  # all-MiniLM-L6-v2 dimension
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        time.sleep(10)  # Wait for index to be ready
    
    # Connect to index
    index = pc.Index(index_name)
    
    # Initialize embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"Connected to Pinecone index: {index_name}")

def upload_dict(data: Dict[str, str], api_key: str = None, index_name: str = "path-value-db"):
    """
    Upload a dictionary to Pinecone vector database
    
    Args:
        data: Dictionary with path as key and value as string
        api_key: Pinecone API key (optional if set in env)
        index_name: Name of the Pinecone index
    """
    global pc, index, model
    
    # Initialize if not already done
    if pc is None or index is None or model is None:
        initialize_pinecone(api_key, index_name)
    
    print(f"Uploading {len(data)} entries to vector database...")
    
    # Prepare vectors
    vectors = []
    for path, value in data.items():
        # Create embedding from combined path and value
        text = f"Path: {path} Content: {value}"
        embedding = model.encode([text])[0].tolist()
        
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
    global pc, index, model
    
    # Initialize if not already done
    if pc is None or index is None or model is None:
        initialize_pinecone(api_key, index_name)
    
    # Create query embedding
    query_embedding = model.encode([query])[0].tolist()
    
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