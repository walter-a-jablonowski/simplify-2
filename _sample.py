
# sample by chat gpt

import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load a sentence-transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Function to read text from .txt and .md files
def read_files(directory):
  docs, file_paths = [], []
  for base, _, files in os.walk(directory):
    for file in files:
      if file.endswith(".txt") or file.endswith(".md"):
        path = os.path.join(base, file)
        try:
          with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            docs.append(content)
            file_paths.append(path)
        except Exception as e:
          print(f"Skipping {path}: {e}")
  return docs, file_paths

# Function to create FAISS index
def build_faiss_index(texts):
  vectors = model.encode(texts, convert_to_numpy=True)
  dimension = vectors.shape[1]
  index = faiss.IndexFlatL2(dimension)
  index.add(vectors)
  return index, vectors

# Function to search FAISS index
def search(query, index, texts, file_paths, top_k=5):
  query_vector = model.encode([query], convert_to_numpy=True)
  distances, indices = index.search(query_vector, top_k)
  results = [(file_paths[i], texts[i][:200]) for i in indices[0] if i < len(texts)]
  return results

# Main execution
if __name__ == "__main__":
  DIRECTORY = "/path/to/your/files"  # Change this

  print("Indexing files...")
  texts, file_paths = read_files(DIRECTORY)
  faiss_index, vectors = build_faiss_index(texts)

  while True:
    query = input("\nEnter search query (or 'exit' to quit): ")
    if query.lower() == "exit":
      break
    results = search(query, faiss_index, texts, file_paths)
    for path, snippet in results:
      print(f"\n📄 {path}\n➡ {snippet}...\n")
