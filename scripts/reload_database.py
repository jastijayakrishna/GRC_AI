"""
Script to force reload the crosswalk database from CSV
"""
import chromadb
import shutil
import os

# Delete the entire ChromaDB directory
if os.path.exists('./chroma_db'):
    print("Deleting old ChromaDB data...")
    shutil.rmtree('./chroma_db')
    print("Old database deleted")

# Now import and load fresh
import rag_engine

print("\nLoading crosswalk database from CSV...")
success = rag_engine.load_crosswalk_db()

if success:
    count = rag_engine.crosswalk_collection.count()
    print(f"Successfully loaded {count} patterns!")

    # Show first 5 patterns
    results = rag_engine.crosswalk_collection.get(limit=5)
    print("\nSample patterns:")
    for i, meta in enumerate(results['metadatas'], 1):
        print(f"  {i}. {meta['pattern_name']}")
else:
    print("Failed to load crosswalk database")
