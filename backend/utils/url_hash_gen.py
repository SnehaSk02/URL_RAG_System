from backend.utils.url_hash import generate_url_hash

url = "https://www.geeksforgeeks.org/nlp/what-is-retrieval-augmented-generation-rag/"

url_hash = generate_url_hash(url)

print(url_hash)