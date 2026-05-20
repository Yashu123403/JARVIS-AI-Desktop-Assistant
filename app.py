from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# Make sure you set OPENAI_API_KEY in .env or environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chat_history = [{"role": "system", "content": "You are a helpful assistant."}]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json["message"]
    chat_history.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat_history
    )
    answer = response.choices[0].message["content"]
    chat_history.append({"role": "assistant", "content": answer})
    
    return jsonify({"reply": answer})

if __name__ == "__main__":
    app.run(debug=True)
