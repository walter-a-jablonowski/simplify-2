import os
import json
import faiss
import numpy as np
from   http.server  import HTTPServer, SimpleHTTPRequestHandler
from   urllib.parse import parse_qs, urlparse
from   sentence_transformers import SentenceTransformer
import webbrowser
from   pathlib import Path

class SimilaritySearch:

  def __init__(self, chunk_size=1000):

    self.model  = SentenceTransformer("all-MiniLM-L6-v2")
    self.chunk_size = chunk_size
    self.index  = None
    self.chunks = []
    self.file_paths = []
    self.chunk_positions = []

  def chunk_text(self, text):

    words  = text.split()
    chunks = []
    for i in range(0, len(words), self.chunk_size):
      chunk = " ".join(words[i:i + self.chunk_size])
      chunks.append(chunk)
    return chunks

  def index_files(self, directory):

    self.chunks = []
    self.file_paths = []
    self.chunk_positions = []
    
    for base, _, files in os.walk(directory):
      for file in files:
        if file.endswith((".txt", ".md", ".json", ".py", ".js", ".html", ".css")):
          path = os.path.join(base, file)
          try:
            with open(path, "r", encoding="utf-8") as f:
              content = f.read()
              text_chunks = self.chunk_text(content)
              for pos, chunk in enumerate(text_chunks):
                self.chunks.append(chunk)
                self.file_paths.append(path)
                self.chunk_positions.append(pos * self.chunk_size)
          except Exception as e:
            print(f"Error reading {path}: {e}")

    if not self.chunks:
      return

    vectors    = self.model.encode(self.chunks, convert_to_numpy=True)
    dimension  = vectors.shape[1]
    self.index = faiss.IndexFlatL2(dimension)
    self.index.add(vectors)

  def search(self, query, top_k=5):

    if not self.index:
      return []
      
    query_vector       = self.model.encode([query], convert_to_numpy=True)
    distances, indices = self.index.search(query_vector, top_k)
    
    results = []
    for idx in indices[0]:
      if idx >= 0 and idx < len(self.chunks):
        results.append({
          "file_path": self.file_paths[idx],
          "content":   self.chunks[idx],
          "position":  self.chunk_positions[idx],
          "relative_path": os.path.relpath(self.file_paths[idx], search_engine.root_dir)
        })

    return results


class RequestHandler(SimpleHTTPRequestHandler):

  def do_GET(self):

    if self.path == "/":
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      with open("index.html", "rb") as f:
        self.wfile.write(f.read())
    else:
      super().do_GET()

  def do_POST(self):

    content_length = int(self.headers["Content-Length"])
    post_data      = self.rfile.read(content_length)
    data           = json.loads(post_data)

    if self.path == "/api/search":
      query   = data.get("query", "")
      results = search_engine.search(query)
      
      self.send_response(200)
      self.send_header("Content-type", "application/json")
      self.end_headers()
      self.wfile.write(json.dumps(results).encode())

    elif self.path == "/api/save":
      
      file_path = data.get("file_path", "")
      content   = data.get("content", "")
      
      try:
        with open(file_path, "w", encoding="utf-8") as f:
          f.write(content)
        search_engine.index_files(search_engine.root_dir)  # Reindex after save
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success"}).encode())
      except Exception as e:
        self.send_response(500)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": str(e)}).encode())

    elif self.path == "/api/update_base":
      new_base = data.get("base_dir", "")
      if os.path.exists(new_base):
        search_engine.root_dir = new_base
        search_engine.index_files(new_base)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success"}).encode())
      else:
        self.send_response(400)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Dir missing"}).encode())


if __name__ == "__main__":

  search_engine = SimilaritySearch()
  search_engine.root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug")
  search_engine.index_files(search_engine.root_dir)
  
  server = HTTPServer(("localhost", 8000), RequestHandler)
  print("Server started at http://localhost:8000")
  webbrowser.open("http://localhost:8000")
  server.serve_forever()
