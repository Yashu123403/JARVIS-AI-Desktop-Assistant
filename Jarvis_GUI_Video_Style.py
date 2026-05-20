"""
Jarvis_GUI_Video_Style.py
A unique, polished, and easy-to-run Jarvis-like desktop assistant with a GUI
inspired by tutorial/demo videos. Designed to be runnable immediately.

Features:
- Tkinter GUI with Start/Stop, Speak (voice input), Type & Send, and quick-action buttons
- Background speech recognition (if microphone & SpeechRecognition available)
- Text-to-speech via pyttsx3 (falls back to printing if unavailable)
- Open websites, play YouTube, search Wikipedia, fetch simple weather (requires OpenWeather API key only for full feature)
- Screenshot capture
- Non-blocking architecture (uses threads) so UI stays responsive
- Safe for sandboxed environments (__file__ fallback, guarded imports)
- Test mode: run `JARVIS_RUN_TESTS=1 python Jarvis_GUI_Video_Style.py` to exercise core functions

How to run (quick):
1) Install dependencies (recommended):
   pip install pyttsx3 SpeechRecognition wikipedia pywhatkit requests Pillow

2) Run:
   python Jarvis_GUI_Video_Style.py

If your environment lacks tkinter, the script will abort with a clear message.

"""

import os
import sys
import threading
import queue
import time
import webbrowser
import datetime
import platform
import subprocess
import traceback
from pathlib import Path

# Guarded imports for optional libraries
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
except Exception as e:
    print("Tkinter is required for the GUI but is not available in this environment.")
    print("Error: ", e)
    raise

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    import wikipedia
except Exception:
    wikipedia = None

try:
    import pywhatkit
except Exception:
    pywhatkit = None

try:
    import requests
except Exception:
    requests = None

try:
    from PIL import ImageGrab
except Exception:
    ImageGrab = None

# --------- Paths & Config (safe in sandbox) ----------
if '__file__' in globals():
    BASE_DIR = Path(__file__).parent
else:
    BASE_DIR = Path.cwd()

# optional config file location
CONFIG_PATH = BASE_DIR / 'jarvis_gui_config.json'
DEFAULT_CONFIG = {
    'wake_word': 'jarvis',
    'openweather_api_key': 'YOUR_OPENWEATHER_API_KEY'
}

if not CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH, 'w') as f:
            import json

            json.dump(DEFAULT_CONFIG, f, indent=2)
    except Exception:
        pass

# --------- Utilities ---------

def log(msg):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] {msg}")


# --------- TTS wrapper ---------
class TTS:
    def __init__(self):
        self.engine = None
        if pyttsx3 is None:
            log('pyttsx3 not available — falling back to text output for speech.')
            return
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)
        except Exception as e:
            log(f'Failed to init pyttsx3: {e}')
            self.engine = None

    def speak(self, text: str):
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                log(f'TTS error: {e}')
                print('(speak)', text)
        else:
            # Fallback: print so users without audio still see responses
            print('(speak)', text)


# --------- Listener (background) ---------
class Listener:
    def __init__(self, out_queue: queue.Queue):
        self.q = out_queue
        self.recognizer = None
        self.microphone = None
        self.running = False
        self.thread = None

        if sr is None:
            log('SpeechRecognition not installed; voice input disabled.')
            return
        try:
            self.recognizer = sr.Recognizer()
            try:
                self.microphone = sr.Microphone()
            except Exception:
                log('No accessible microphone; voice input disabled.')
                self.microphone = None
        except Exception as e:
            log('Failed to initialize speech recognizer: ' + str(e))
            self.recognizer = None

    def start(self):
        if not self.recognizer or not self.microphone:
            return False
        if self.running:
            return True
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.running = False

    def _loop(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        while self.running:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, phrase_time_limit=6)
                text = self.recognizer.recognize_google(audio)
                log('Heard: ' + text)
                self.q.put(text)
            except sr.UnknownValueError:
                continue
            except Exception as e:
                log('Listener error: ' + str(e))
                time.sleep(0.5)


# --------- Core Assistant Logic ---------
class JarvisCore:
    def __init__(self, gui_log_callable):
        self.q = queue.Queue()
        self.listener = Listener(self.q)
        self.tts = TTS()
        self.gui_log = gui_log_callable
        self.running = False
        self.worker = None

    def start(self):
        if self.running:
            return
        self.running = True
        # start listener (if available)
        self.listener.start()
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()
        self.say('Jarvis at your service.')

    def stop(self):
        self.running = False
        try:
            self.listener.stop()
        except Exception:
            pass
        self.say('Going to standby mode.')

    def say(self, text: str):
        self.gui_log('Jarvis: ' + text)
        self.tts.speak(text)

    def submit_text(self, text: str):
        # Called by GUI to submit a user command (no wake word required)
        # We emulate wake word internally for simplicity
        self.q.put(DEFAULT_CONFIG.get('wake_word', 'jarvis') + ' ' + text)

    def _worker_loop(self):
        while self.running:
            try:
                phrase = self.q.get(timeout=1)
            except queue.Empty:
                continue
            # simple wake-word handling
            phrase_l = phrase.lower()
            wake = DEFAULT_CONFIG.get('wake_word', 'jarvis')
            if wake in phrase_l:
                cmd = phrase_l.replace(wake, '').strip()
                if not cmd:
                    self.say('Yes?')
                    continue
                self.gui_log('Command: ' + cmd)
                try:
                    self._handle(cmd)
                except Exception as e:
                    log('Error handling command: ' + str(e))
                    log(traceback.format_exc())
                    self.say('I encountered an error while processing that command.')
            else:
                # if no wake word present, treat as direct command
                self._handle(phrase_l)

    def _handle(self, cmd: str):
        # time
        if 'time' in cmd:
            t = datetime.datetime.now().strftime('%I:%M %p')
            self.say(f'The time is {t}')
            return

        # open website or app
        if cmd.startswith('open '):
            target = cmd.replace('open ', '').strip()
            # URL?
            if '.' in target or 'www' in target:
                if not target.startswith('http'):
                    target = 'https://' + target
                webbrowser.open(target)
                self.say('Opening ' + target)
                return
            # else try app mapping (basic)
            try:
                system = platform.system().lower()
                if system == 'windows' and target == 'notepad':
                    subprocess.Popen(['notepad.exe'])
                    self.say('Opening notepad')
                    return
                self.say('Could not find app mapping for ' + target)
            except Exception as e:
                self.say('Failed to open: ' + str(e))
            return

        # wikipedia
        if 'wikipedia' in cmd or cmd.startswith('search '):
            # extract query
            q = cmd.replace('wikipedia', '').replace('search', '').replace('for', '').strip()
            if not q:
                self.say('What should I search on Wikipedia?')
                return
            if wikipedia is None:
                self.say('Wikipedia package not installed. Install with: pip install wikipedia')
                return
            try:
                summary = wikipedia.summary(q, sentences=2)
                self.say(summary)
            except Exception as e:
                self.say('Could not fetch Wikipedia summary: ' + str(e))
            return

        # play on youtube
        if cmd.startswith('play '):
            q = cmd.replace('play', '').strip()
            if pywhatkit is None:
                self.say('pywhatkit not installed. Install with: pip install pywhatkit')
                return
            try:
                self.say('Playing ' + q + ' on YouTube')
                pywhatkit.playonyt(q)
            except Exception as e:
                self.say('Could not play on YouTube: ' + str(e))
            return

        # weather (very simple parsing: last word is city)
        if 'weather' in cmd:
            pieces = cmd.split()
            city = pieces[-1]
            api_key = DEFAULT_CONFIG.get('openweather_api_key')
            if not api_key or api_key == 'YOUR_OPENWEATHER_API_KEY':
                self.say('OpenWeather API key not configured. Skipping real fetch. Try: weather in London')
                return
            if requests is None:
                self.say('Requests library not installed. Install with: pip install requests')
                return
            try:
                url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
                res = requests.get(url, timeout=6).json()
                desc = res['weather'][0]['description']
                temp = res['main']['temp']
                self.say(f'Weather in {city}: {desc}, {temp}°C')
            except Exception as e:
                self.say('Could not fetch weather: ' + str(e))
            return

        # screenshot
        if 'screenshot' in cmd or 'take screenshot' in cmd:
            if ImageGrab is None:
                self.say('Pillow not installed — screenshot not available. Install with: pip install Pillow')
                return
            try:
                now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                out = BASE_DIR / f'screenshot_{now}.png'
                img = ImageGrab.grab()
                img.save(out)
                self.say('Screenshot saved to ' + str(out))
            except Exception as e:
                self.say('Screenshot failed: ' + str(e))
            return

        # greetings / info
        if 'hello' in cmd or 'hi' in cmd or 'hey' in cmd:
            self.say('Hello! I am your Jarvis assistant. Ask me to open websites, play music, check the time, or search Wikipedia.')
            return

        # fallback
        self.say("I didn't understand that. Try: 'play <song>', 'open example.com', 'search <topic>', 'what's the time', or 'take screenshot'.")


# --------- GUI ---------
class JarvisGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Jarvis — Desktop Assistant')
        self.geometry('760x520')
        self.configure(bg='#0f1724')

        # Styles
        style = ttk.Style(self)
        style.theme_use('default')

        # Top frame (controls)
        top = ttk.Frame(self)
        top.pack(fill='x', padx=12, pady=10)

        self.start_btn = ttk.Button(top, text='Start', command=self.on_start)
        self.start_btn.pack(side='left', padx=(0, 6))
        self.stop_btn = ttk.Button(top, text='Stop', command=self.on_stop, state='disabled')
        self.stop_btn.pack(side='left')

        self.entry = ttk.Entry(top, width=60)
        self.entry.pack(side='left', padx=8)
        self.entry.bind('<Return>', lambda e: self.on_send())

        self.send_btn = ttk.Button(top, text='Send', command=self.on_send)
        self.send_btn.pack(side='left', padx=6)

        # Middle: log
        self.log = scrolledtext.ScrolledText(self, wrap='word', height=20, bg='#0b1020', fg='#e6eef8')
        self.log.pack(fill='both', expand=True, padx=12, pady=(0, 8))
        self.log.insert('end', 'Welcome to Jarvis - GUI mode. Click Start to begin.\n')
        self.log.configure(state='disabled')

        # Bottom quick actions
        bottom = ttk.Frame(self)
        bottom.pack(fill='x', padx=12, pady=(0, 12))

        ttk.Button(bottom, text='Open Website', command=self.quick_open).pack(side='left', padx=6)
        ttk.Button(bottom, text='Play on YouTube', command=self.quick_play).pack(side='left', padx=6)
        ttk.Button(bottom, text='Wikipedia', command=self.quick_wiki).pack(side='left', padx=6)
        ttk.Button(bottom, text='Screenshot', command=self.quick_screenshot).pack(side='left', padx=6)
        ttk.Button(bottom, text='System Info', command=self.quick_sysinfo).pack(side='right', padx=6)

        # Core
        self.core = JarvisCore(self.gui_log)

        # If tests requested, run after short delay
        if os.environ.get('JARVIS_RUN_TESTS') == '1' or os.environ.get('JARVIS_RUN_TESTS', '').lower() == 'true':
            self.after(800, self.run_tests)

    def gui_log(self, message: str):
        # append to scrolled text safely from any thread
        def _append():
            self.log.configure(state='normal')
            self.log.insert('end', message + '\n')
            self.log.see('end')
            self.log.configure(state='disabled')

        try:
            self.after(0, _append)
        except Exception:
            print(message)

    def on_start(self):
        self.core.start()
        self.start_btn.configure(state='disabled')
        self.stop_btn.configure(state='normal')

    def on_stop(self):
        self.core.stop()
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')

    def on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.gui_log('You: ' + text)
        self.entry.delete(0, 'end')
        # Submit to core
        self.core.submit_text(text)

    # Quick action dialogs
    def quick_open(self):
        url = self.simple_prompt('Open website', 'Enter website or URL (example.com):')
        if url:
            self.gui_log('You (quick): open ' + url)
            self.core.submit_text('open ' + url)

    def quick_play(self):
        song = self.simple_prompt('Play on YouTube', 'Enter song or video name:')
        if song:
            self.gui_log('You (quick): play ' + song)
            self.core.submit_text('play ' + song)

    def quick_wiki(self):
        q = self.simple_prompt('Wikipedia', 'Search Wikipedia for:')
        if q:
            self.gui_log('You (quick): wikipedia ' + q)
            self.core.submit_text('wikipedia ' + q)

    def quick_screenshot(self):
        self.gui_log('You (quick): take screenshot')
        self.core.submit_text('take screenshot')

    def quick_sysinfo(self):
        info = f"Platform: {platform.system()} {platform.release()} | Python: {platform.python_version()}"
        self.gui_log(info)
        self.core.say(info)

    def simple_prompt(self, title, prompt):
        # small modal dialog
        return simple_input_dialog(self, title, prompt)

    def run_tests(self):
        # Run through a sequence of commands to exercise the UI & core
        self.gui_log('Running builtin GUI smoke tests...')
        test_cmds = [
            'what time is it',
            'open example.com',
            'search wikipedia for Python programming language',
            'play imagine dragons on youtube',
            'take screenshot',
            'hello'
        ]
        for c in test_cmds:
            self.gui_log('TEST -> ' + c)
            self.core.submit_text(c)
            time.sleep(1.0)
        self.gui_log('GUI tests finished.')


# ------- Simple modal input dialog (synchronous) -------
class SimpleDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.resizable(False, False)
        self.value = None

        lbl = ttk.Label(self, text=prompt)
        lbl.pack(padx=12, pady=(12, 6))
        self.entry = ttk.Entry(self, width=60)
        self.entry.pack(padx=12, pady=(0, 12))
        self.entry.focus_set()

        btns = ttk.Frame(self)
        btns.pack(padx=12, pady=(0, 12))
        ttk.Button(btns, text='OK', command=self.on_ok).pack(side='left', padx=6)
        ttk.Button(btns, text='Cancel', command=self.on_cancel).pack(side='left')

        self.bind('<Return>', lambda e: self.on_ok())
        self.bind('<Escape>', lambda e: self.on_cancel())
        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self.on_cancel)
        self.wait_window()

    def on_ok(self):
        self.value = self.entry.get().strip()
        self.destroy()

    def on_cancel(self):
        self.value = None
        self.destroy()


def simple_input_dialog(parent, title, prompt):
    d = SimpleDialog(parent, title, prompt)
    return d.value


# --------- Main ---------
if __name__ == '__main__':
    app = JarvisGUI()
    app.mainloop()
