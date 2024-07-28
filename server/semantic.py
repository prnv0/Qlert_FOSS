from sentence_transformers import SentenceTransformer
from azuredb import addPrompt
import os
# Initialize Qdrant client
client = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"],
)
# Initialize SentenceTransformer encoder
encoder = SentenceTransformer("all-MiniLM-L6-v2")


import openai
import requests
import json

openai.api_key = os.environ["OPENAI_API_KEY"]
api_url = os.environ["OPENAI_API_URL"]
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai.api_key}",
}
messages = [{"role": "system", "content": "You are a intelligent assistant."}]


def simil_search(inputs):
    # Encode the input text into vectors
    # input_vectors = [encoder.encode(input_text).tolist() for input_text in inputs]

    # Search for similar vectors in the Qdrant index
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": inputs}],
        "temperature": 0.7,
    }

    hits = client.search(
        collection_name=os.environ["QDRANT_COLLECTION"],
        query_vector=encoder.encode(inputs).tolist(),
        limit=3,
    )
    result = 0
    outputs = ""
    for hit in hits:
        print(hit.payload, "score:", hit.score)
        search = hit.payload["description"]
        threshold = hit.payload["threshold"]
        print(threshold)
        if hit.score > threshold:
            result = 1
            print("Violation of rule:", hit.payload["description"])
            break
    if result == 1:
        outputs = "Sorry violation of rule: " + hit.payload["description"]
        print("Alert")
        addPrompt("user420", inputs, "High", hit.payload["description"])
    else:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            outputs = response.json()["choices"][0]["message"]["content"]
        else:
            print("Error:", response.status_code)
            outputs = response.json().status_code
        if(hit.score*0.95>threshold):
            addPrompt("user420", inputs, "Medium", "May violate rule"+hit.payload["description"])
        else:
            addPrompt("user420", inputs, "Low", "No significant risks.")
    # Extract payload from hits
    print(outputs)
    # Return a list of outputs (one for each input)
    return outputs
