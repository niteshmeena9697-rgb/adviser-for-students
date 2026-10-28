import os
from urllib.parse import urlparse
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
load_dotenv()

app = Flask(__name__)

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
def generate_summary(query, results):
    if not GEMINI_API_KEY:
        return "Gemini API key is missing."

    source_text = "\n\n".join(
        f"Title: {item.get('title', '')}\n"
        f"Snippet: {item.get('snippet', '')}"
        for item in results[:8]
    )

    prompt = f"""
You are an AI research assistant.

User searched for:
{query}

Here are web search results:
{source_text}

Create a concise research summary based ONLY on these search results.

Give:
1. A short answer
2. 3-5 key points
3. Mention important differences if relevant

Do not invent information that is not supported by the results.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI summary failed: {str(e)}"
def clean_url(url):
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return url

@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please enter a search query."}), 400

    if not SERPAPI_KEY:

        return jsonify({
            "error": "SERPAPI_KEY is missing. Add it to the .env file."
        }), 500
     
    

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 10,
        "hl": "en",
        "gl": "in"
    }

    try:
        response = requests.get(
            "https://serpapi.com/search.json",
            params=params,
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return jsonify({"error": f"Search request failed: {exc}"}), 502

    if data.get("error"):
        return jsonify({"error": data["error"]}), 502

    results = []
    for item in data.get("organic_results", []):
        results.append({
            "position": item.get("position"),
            "title": item.get("title", "Untitled"),
            "link": item.get("link", ""),
            "displayed_link": item.get("displayed_link", ""),
            "snippet": item.get("snippet", ""),
            "source": clean_url(item.get("link", ""))
        })
    ai_summary = generate_summary(query, results)
    return jsonify({
        "query": query,
        "total_results": len(results),
        "answer_box": data.get("answer_box"),
        "knowledge_graph": data.get("knowledge_graph"),
        "ai_summary": ai_summary,
        "results": results
    })


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
