import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2"


def ask_ai(prompt):

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data["response"].strip()

    except Exception as e:

        print("AI Error:", e)

        return "Sorry, I couldn't answer."