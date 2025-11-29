import chromadb
import pandas as pd
from chromadb.utils import embedding_functions
import logging
import os

# --- LOGGING SETUP ---
# Ensure logging is configured if this module is run standalone
logging.basicConfig(level=logging.INFO)

# Initialize ChromaDB client
# We use a persistent client so data is saved to disk
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Embedding function (same for both collections)
# This uses the default all-MiniLM-L6-v2 model which is small and runs locally
default_ef = embedding_functions.DefaultEmbeddingFunction()

# Two separate collections
# 1. For Company Policies (PDFs)
policy_collection = chroma_client.get_or_create_collection(
    name="company_policies",
    embedding_function=default_ef
)

# 2. For Framework Cross-Walk (CSV)
crosswalk_collection = chroma_client.get_or_create_collection(
    name="framework_crosswalk",
    embedding_function=default_ef
)

def load_crosswalk_db():
    """
    Load the framework crosswalk CSV into the vector database.
    This should be called once at app startup.
    """
    try:
        # Check if already loaded to avoid duplicates
        if crosswalk_collection.count() > 0:
            logging.info(f"✅ Crosswalk DB already loaded ({crosswalk_collection.count()} patterns)")
            return True
        
        # Load from CSV
        if not os.path.exists('framework_crosswalk.csv'):
            logging.warning("⚠️ framework_crosswalk.csv not found. Crosswalk features disabled.")
            return False

        df = pd.read_csv('framework_crosswalk.csv')
        
        # Add each risk pattern to the database
        ids = [str(i) for i in range(len(df))]
        documents = df['description'].tolist()
        metadatas = []
        
        for _, row in df.iterrows():
            metadatas.append({
                'pattern_name': row['risk_pattern'],
                'iso_27001': row['iso_27001'],
                'soc_2': row['soc_2'],
                'hipaa': row['hipaa'],
                'nist_csf': row['nist_csf']
            })

        crosswalk_collection.add(
            ids=ids,
            documents=documents,  # Searchable text
            metadatas=metadatas
        )
        
        logging.info(f"✅ Loaded {len(df)} risk patterns into crosswalk database")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error loading crosswalk DB: {e}")
        return False

def get_framework_mappings(finding_text, threshold=1.4):
    """
    Returns verified framework control IDs from the database.
    This eliminates LLM hallucinations by using ground truth.

    Args:
        finding_text: The audit finding to analyze
        threshold: Maximum distance (ChromaDB L2 distance) to accept a match.
                   Lower distance = better match. Default: 1.0

    Returns:
        Dictionary with control IDs or None if no match
    """
    try:
        if crosswalk_collection.count() == 0:
            return None

        results = crosswalk_collection.query(
            query_texts=[finding_text],
            n_results=1
        )

        if results['metadatas'] and len(results['metadatas'][0]) > 0:
            # Get the distance (lower is better)
            distance = results['distances'][0][0]

            logging.info(f"Crosswalk Match Distance: {distance}")

            if distance < threshold:
                mappings = results['metadatas'][0][0]
                logging.info(f"✅ Crosswalk match found: {mappings.get('pattern_name')}")
                return mappings
            else:
                logging.info(f"⚠️ Match found but distance too high ({distance} >= {threshold})")
                return None

        return None

    except Exception as e:
        logging.error(f"❌ Error querying crosswalk DB: {e}")
        return None

def ingest_policy(pdf_path):
    """
    Extract text from PDF and store in vector database.
    """
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        
        # Split into chunks (simple version)
        # Using double newline as paragraph separator
        chunks = text.split('\n\n')

        # Clear existing policy to avoid mixing documents (for this simple demo)
        # In a real app, we might want to keep them or use metadata to separate
        global policy_collection
        if policy_collection.count() > 0:
             # Chroma doesn't have a clear() method on collection, so we delete and recreate or just delete items
             # Simpler to just delete the collection and recreate in this context
             chroma_client.delete_collection("company_policies")
             policy_collection = chroma_client.get_or_create_collection(name="company_policies", embedding_function=default_ef)

        # Add to collection
        ids = []
        docs = []
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) > 50:  # Skip tiny chunks
                ids.append(f"policy_{i}")
                docs.append(chunk)
        
        if docs:
            policy_collection.add(
                ids=ids,
                documents=docs
            )
        
        return True, f"Ingested {len(docs)} policy sections"
        
    except Exception as e:
        return False, str(e)

def query_policy(question):
    """
    Retrieve relevant policy sections for a given question.
    """
    try:
        if policy_collection.count() == 0:
            return None
            
        results = policy_collection.query(
            query_texts=[question],
            n_results=3
        )
        
        if results['documents']:
            return "\n\n".join(results['documents'][0])
        return None
        
    except Exception as e:
        logging.error(f"Policy query error: {e}")
        return None
