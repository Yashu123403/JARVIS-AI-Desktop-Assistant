"""
jarvis_chatgui.py
A simple desktop ChatGPT-like assistant (Tkinter GUI) using the OpenAI API.
Features:
 - Chat conversation with context (keeps history)
 - Sends user messages to OpenAI Chat Completions
 - Displays assistant replies in GUI and speaks them using pyttsx3
 - Non-blocking network calls (uses threading)
Requirements:
 - pip install openai pyttsx3 python-dotenv
 - Set OPENAI_API_KEY as environment variable or in a .env file
"""

import os
import threading
import queue
import time
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
try:
    # recommended new import pattern
    from openai import OpenAI
except Exception:
    # fallback to legacy package import name if older version
    import openai as legacy_openai

    class OpenAI:
        def __init__(self, api_key=None):
            self.client = legacy_openai
            if api_key:
                self.client.api_key = api_key

        def chat_completions(self):
            return self.client.ChatCompletion

import pyttsx3
from dotenv import load_dotenv

load_dotenv()  # load .env if present

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    # If no API key set, prompt the user (safe for local dev)
    root = tk.Tk()
    root.withdraw()
    key = simpledialog.askstring("API Key required", "Enter your OpenAI API key (sk-...):", show='*')
    if not key:
        messagebox.showerror("Missing key", "OpenAI API key is required to run the assistant.")
        raise SystemExit("OPENAI_API_KEY not provided")
    API_KEY = key

# Create OpenAI client
try:
    client = OpenAI(api_key=API_KEY)
    # new-style call wrapper we'll use later: client.chat.completions.create(...) OR compatibility path below
    use_new_client = True
except Exception:
    # fallback to legacy openai import
    import openai
    openai.api_key = API_KEY
    client = openai
    use_new_client = False

# TTS engine init
tts = pyttsx3.init()
tts.setProperty('rate', 160)

# Thread-safe queue for GUI updates
ui_queue = queue.Queue()

# Chat history maintained as list of {"role":..., "content":...}
chat_history = [
    {"role": "system", "content": "You are a helpful, friendly assistant. Keep answers concise and clear."}
]

# Helper: add message to GUI text area (thread-safe)
def add_message_to_textwidget(widget, sender, message):
    widget.configure(state='normal')
    widget.insert(tk.END, f"{sender}: {message}\n\n")
    widget.see(tk.END)
    widget.configure(state='disabled')

# Worker: call OpenAI API (run in background thread)
def call_openai_and_respond(user_text, gui_text_widget, speak=True):
    try:
        # append user message to history
        chat_history.append({"role": "user", "content": user_text})

        # Build API call using whichever client we have
        if use_new_client and hasattr(client, "chat"):
            # Some new OpenAI SDKs expose client.chat.completions.create(...) or client.chat.completions.create
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=chat_history,
                    max_tokens=700,
                    temperature=0.6,
                )
                assistant_text = response.choices[0].message["content"]
            except Exception:
                # try alternate path used in some client versions
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=chat_history
                )
                assistant_text = response.choices[0].message["content"]
        else:
            # Legacy openai package usage
            response = client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=chat_history,
                max_tokens=700,
                temperature=0.6,
            )
            assistant_text = response.choices[0].message['content'] if isinstance(response.choices[0].message, dict) else response.choices[0].text

        # append assistant reply to history
        chat_history.append({"role": "assistant", "content": assistant_text})

        # Queue GUI update
        ui_queue.put(("assistant", assistant_text))

        # Speak reply
        if speak:
            try:
                tts.say(assistant_text)
                tts.runAndWait()
            except Exception as e:
                # TTS error should not crash app
                ui_queue.put(("info", f"[TTS error] {e}"))
    except Exception as e:
        ui_queue.put(("error", str(e)))

# GUI send handler
def on_send(entry_widget, text_widget, speak_var):
    user_text = entry_widget.get().strip()
    if not user_text:
        return
    entry_widget.delete(0, tk.END)
    add_message_to_textwidget(text_widget, "You", user_text)
    # Start background thread to call OpenAI
    thread = threading.Thread(target=call_openai_and_respond, args=(user_text, text_widget, speak_var.get()), daemon=True)
    thread.start()

# Periodically check ui_queue to update GUI from background threads
def poll_ui_queue(text_widget):
    try:
        while True:
            item = ui_queue.get_nowait()
            kind, payload = item
            if kind == "assistant":
                add_message_to_textwidget(text_widget, "Assistant", payload)
            elif kind == "info":
                add_message_to_textwidget(text_widget, "Info", payload)
            elif kind == "error":
                add_message_to_textwidget(text_widget, "Error", payload)
    except queue.Empty:
        pass
    # schedule next poll
    text_widget.after(200, poll_ui_queue, text_widget)

# Build GUI
def build_and_run_gui():
    root = tk.Tk()
    root.title("Jarvis — Chat (local desktop)")
    root.geometry("700x600")

    chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Helvetica", 11))
    chat_display.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    bottom_frame = tk.Frame(root)
    bottom_frame.pack(fill=tk.X, padx=8, pady=6)

    speak_var = tk.BooleanVar(value=True)
    speak_check = tk.Checkbutton(bottom_frame, text="Speak replies", variable=speak_var)
    speak_check.pack(side=tk.LEFT, padx=(0,10))

    entry = tk.Entry(bottom_frame, font=("Helvetica", 12))
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,8))
    entry.focus()

    send_btn = tk.Button(bottom_frame, text="Send", width=10, command=lambda: on_send(entry, chat_display, speak_var))
    send_btn.pack(side=tk.RIGHT)

    # Bind Enter key
    root.bind('<Return>', lambda event: on_send(entry, chat_display, speak_var))

    # Start polling queue
    poll_ui_queue(chat_display)

    # Pre-populate with a short greeting from assistant (optional)
    ui_queue.put(("assistant", "Hello — I'm Jarvis. Ask me anything or type a command."))

    root.mainloop()

if __name__ == "__main__":
    build_and_run_gui()
