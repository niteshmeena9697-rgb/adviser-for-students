# adviser-for-students
it can  be use for study related tasks or also it can help to make better decision . 
# SearchMind AI

A simple hackathon-ready web research app using Flask + SerpAPI.

## 1. Create a virtual environment

Windows:

    py -m venv .venv
    .venv\Scripts\activate

## 2. Install dependencies

    pip install -r requirements.txt

## 3. Add your SerpAPI key

Copy `.env.example` to `.env` and set:

    SERPAPI_KEY=your_real_key

## 4. Run

    python app.py

Open:

    http://127.0.0.1:5000

## How it works

Browser -> Flask `/api/search` -> SerpAPI -> JSON -> Frontend cards

The API key stays on the backend and is never exposed to browser JavaScript.
