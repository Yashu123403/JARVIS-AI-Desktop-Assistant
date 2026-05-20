from pathlib import Path
import re

p = Path(r'c:\Users\Admin\Desktop\sun\Jarvis_IronMan_GUI.py')
s = p.read_text(encoding='utf-8')

# 1. Upgrade greeting label with larger, more authentic styling
old_greet = """        # Greeting label (centered top)
        greeting_text = '⚙️ J.A.R.V.I.S. ⚙️\\n🔷 Holographic Interface Online 🔷'
        self.greet_lbl = tk.Label(self, text=greeting_text, font=('Courier New', 22, 'bold'), 
                                   fg='#00B4E6', bg='#0f2d55', justify='center')
        self.greet_lbl.place(x=w // 2 - 200, y=40, width=400)"""

new_greet = """        # Greeting label (centered top) - enhanced
        greeting_text = '⚙️ J.A.R.V.I.S. ⚙️'
        self.greet_lbl = tk.Label(self, text=greeting_text, font=('Courier New', 32, 'bold'), 
                                   fg='#00FF00', bg='#0f2d55', justify='center')
        self.greet_lbl.place(x=w // 2 - 250, y=30, width=500)
        
        # Subtext
        subtitle = tk.Label(self, text='⚡ 3D Holographic AI Interface ⚡', 
                           font=('Courier New', 12), fg='#00B4E6', bg='#0f2d55', justify='center')
        subtitle.place(x=w // 2 - 250, y=75, width=500)"""

s = s.replace(old_greet, new_greet)

# 2. Enhance panel styling with better visual hierarchy
old_panel = """        # Right-side chat panel - dark with neon border effect
        panel_w = int(w * 0.35)
        panel_h = int(h * 0.85)
        panel_x = w - panel_w - 30
        panel_y = 120
        panel_frame = tk.Frame(self, width=panel_w, height=panel_h, bg='#1a3a52', relief='solid', bd=2)
        panel_frame.place(x=panel_x, y=panel_y)"""

new_panel = """        # Right-side chat panel - enhanced with gradient feel
        panel_w = int(w * 0.36)
        panel_h = int(h * 0.82)
        panel_x = w - panel_w - 25
        panel_y = 125
        panel_frame = tk.Frame(self, width=panel_w, height=panel_h, bg='#0d2438', relief='flat', bd=0, highlightthickness=3, highlightbackground='#00B4E6', highlightcolor='#00FF00')
        panel_frame.place(x=panel_x, y=panel_y)
        
        # Inner panel for better spacing
        inner_frame = tk.Frame(panel_frame, bg='#0d2438')
        inner_frame.pack(fill='both', expand=True, padx=1, pady=1)"""

s = s.replace(old_panel, new_panel)

# 3. Update chat and entry styling with better visuals
old_chat = """        # Chat log - dark background with cyan text
        self.chat = scrolledtext.ScrolledText(panel_frame, wrap='word', width=50, height=25, 
                                              bg='#0a1f35', fg='#00D4FF', insertbackground='#00D4FF',
                                              font=('Courier New', 10))
        self.chat.pack(padx=12, pady=(12, 6), fill='both', expand=True)
        self.chat.insert('end', '> J.A.R.V.I.S. ONLINE\\n> Awaiting input...\\n')
        self.chat.configure(state='disabled')

        # Entry and send
        bottom_frame = tk.Frame(panel_frame, bg='#1a3a52')
        bottom_frame.pack(fill='x', padx=12, pady=(0, 12))
        self.entry = tk.Entry(bottom_frame, font=('Courier New', 11), bg='#0a1f35', 
                              fg='#00FF00', insertbackground='#00FF00')
        self.entry.pack(side='left', fill='x', expand=True, padx=(0, 8))
        self.entry.bind('<Return>', lambda e: self._on_send())
        send_btn = tk.Button(bottom_frame, text='SEND', command=self._on_send, 
                             bg='#00B4E6', fg='#0f2d55', font=('Courier New', 10, 'bold'))
        send_btn.pack(side='left')

        # Quick action buttons - neon style (wired)
        actions = tk.Frame(panel_frame, bg='#1a3a52')
        actions.pack(fill='x', padx=12, pady=(0, 12))"""

new_chat = """        # Chat log - enhanced with better styling
        self.chat = scrolledtext.ScrolledText(inner_frame, wrap='word', width=50, height=24, 
                                              bg='#051220', fg='#00FF00', insertbackground='#00B4E6',
                                              font=('Courier New', 10), relief='flat', bd=0, padx=8, pady=6)
        self.chat.pack(padx=0, pady=(8, 8), fill='both', expand=True)
        self.chat.insert('end', '>>> J.A.R.V.I.S. SYSTEM ONLINE\\n>>> Awaiting voice or text input...\\n\\n')
        self.chat.configure(state='disabled')

        # Entry and send - enhanced
        bottom_frame = tk.Frame(inner_frame, bg='#0d2438')
        bottom_frame.pack(fill='x', padx=0, pady=(0, 8))
        self.entry = tk.Entry(bottom_frame, font=('Courier New', 11), bg='#051220', 
                              fg='#00FF00', insertbackground='#00B4E6', relief='flat', bd=0, highlightthickness=1, highlightbackground='#00B4E6', highlightcolor='#00FF00')
        self.entry.pack(side='left', fill='x', expand=True, padx=(8, 8), pady=6)
        self.entry.bind('<Return>', lambda e: self._on_send())
        send_btn = tk.Button(bottom_frame, text='⚡ SEND', command=self._on_send, 
                             bg='#00FF00', fg='#051220', font=('Courier New', 10, 'bold'), relief='flat', bd=0, 
                             padx=12, pady=4, activebackground='#00DD00', activeforeground='#000000', cursor='hand2')
        send_btn.pack(side='left', padx=(0, 8))

        # Quick action buttons - enhanced with better spacing
        actions = tk.Frame(inner_frame, bg='#0d2438')
        actions.pack(fill='x', padx=0, pady=(0, 8))"""

s = s.replace(old_chat, new_chat)

# 4. Enhance button styling
old_buttons = """        web_btn = tk.Button(actions, text='🌐 WEB', bg='#00FF88', fg='#0f2d55', font=('Courier New', 9, 'bold'), command=self._open_web)
        web_btn.pack(side='left', padx=4)
        yt_btn = tk.Button(actions, text='▶ YT', bg='#00B4E6', fg='#0f2d55', font=('Courier New', 9, 'bold'), command=self._open_youtube)
        yt_btn.pack(side='left', padx=4)
        weather_btn = tk.Button(actions, text='⛅ WEATHER', bg='#00D4FF', fg='#0f2d55', font=('Courier New', 9, 'bold'), command=self._ask_weather)
        weather_btn.pack(side='left', padx=4)
        snap_btn = tk.Button(actions, text='📸 SNAP', bg='#ffcc00', fg='#0f2d55', font=('Courier New', 9, 'bold'), command=self._take_screenshot)
        snap_btn.pack(side='left', padx=4)
        open_btn = tk.Button(actions, text='Open App', bg='#8866ff', fg='white', font=('Courier New', 9), command=lambda: self._quick_open_prompt())
        open_btn.pack(side='left', padx=4)
        close_btn = tk.Button(actions, text='Close App', bg='#ff4466', fg='white', font=('Courier New', 9), command=lambda: self._quick_close_prompt())
        close_btn.pack(side='left', padx=4)"""

new_buttons = """        web_btn = tk.Button(actions, text='🌐 WEB', bg='#00FF88', fg='#000000', font=('Courier New', 8, 'bold'), command=self._open_web, relief='flat', bd=0, padx=8, pady=3, activebackground='#00FF00', activeforeground='#000000', cursor='hand2')
        web_btn.pack(side='left', padx=2)
        yt_btn = tk.Button(actions, text='▶ YT', bg='#00B4E6', fg='#000000', font=('Courier New', 8, 'bold'), command=self._open_youtube, relief='flat', bd=0, padx=8, pady=3, activebackground='#00D4FF', cursor='hand2')
        yt_btn.pack(side='left', padx=2)
        weather_btn = tk.Button(actions, text='⛅ WEATHER', bg='#00D4FF', fg='#000000', font=('Courier New', 8, 'bold'), command=self._ask_weather, relief='flat', bd=0, padx=6, pady=3, activebackground='#00FFFF', cursor='hand2')
        weather_btn.pack(side='left', padx=2)
        snap_btn = tk.Button(actions, text='📸 SNAP', bg='#ffcc00', fg='#000000', font=('Courier New', 8, 'bold'), command=self._take_screenshot, relief='flat', bd=0, padx=8, pady=3, activebackground='#ffdd00', cursor='hand2')
        snap_btn.pack(side='left', padx=2)
        open_btn = tk.Button(actions, text='↗ OPEN', bg='#8866ff', fg='#ffffff', font=('Courier New', 8, 'bold'), command=lambda: self._quick_open_prompt(), relief='flat', bd=0, padx=8, pady=3, activebackground='#aa88ff', cursor='hand2')
        open_btn.pack(side='left', padx=2)
        close_btn = tk.Button(actions, text='✕ CLOSE', bg='#ff4466', fg='#ffffff', font=('Courier New', 8, 'bold'), command=lambda: self._quick_close_prompt(), relief='flat', bd=0, padx=6, pady=3, activebackground='#ff6688', cursor='hand2')
        close_btn.pack(side='left', padx=2)"""

s = s.replace(old_buttons, new_buttons)

# 5. Enhance mic button styling
old_mic = """        # Small cute mic toggle (top-right)
        self.small_mic_btn = tk.Button(self, text='🎤', command=self.toggle_mic, 
                                       bg='#00B4E6', fg='#0f2d55', font=('Segoe UI', 16), 
                                       relief='flat', bd=0, activebackground='#0ff')
        self.small_mic_btn.place(x=w - 70, y=20, width=50, height=50)"""

new_mic = """        # Mic toggle - enhanced
        self.small_mic_btn = tk.Button(self, text='🎤', command=self.toggle_mic, 
                                       bg='#00B4E6', fg='#000000', font=('Segoe UI', 18, 'bold'), 
                                       relief='flat', bd=2, activebackground='#00FF00', highlightthickness=2, highlightbackground='#00B4E6', cursor='hand2')
        self.small_mic_btn.place(x=w - 80, y=15, width=60, height=60)"""

s = s.replace(old_mic, new_mic)

# 6. Enhance close button styling
old_close = """        # Close button (top-left)
        self.close_btn = tk.Button(self, text='✕', command=self._on_escape, 
                                   bg='#ff0055', fg='white', font=('Segoe UI', 14), 
                                   relief='flat', bd=0, activebackground='#ff3366')
        self.close_btn.place(x=20, y=20, width=50, height=50)"""

new_close = """        # Close button - enhanced
        self.close_btn = tk.Button(self, text='✕', command=self._on_escape, 
                                   bg='#ff0055', fg='white', font=('Segoe UI', 16, 'bold'), 
                                   relief='flat', bd=2, activebackground='#ff3366', highlightthickness=2, highlightbackground='#ff0055', cursor='hand2')
        self.close_btn.place(x=15, y=15, width=60, height=60)"""

s = s.replace(old_close, new_close)

# 7. Update system info styling
old_info = """        # System info - neon green
        info = tk.Label(self, text=f'[{platform.system()} | {platform.node()} | Python {platform.python_version()}]', 
                       font=('Courier New', 8), fg='#00FF88', bg='#0f2d55')
        info.place(x=30, y=h - 40)"""

new_info = """        # System info - enhanced
        info_text = f'[ {platform.system()} | {platform.node()} | Python {platform.python_version()} ]'
        info = tk.Label(self, text=info_text, 
                       font=('Courier New', 9, 'bold'), fg='#00FF88', bg='#0f2d55')
        info.place(x=30, y=h - 35)
        
        # Status indicator
        status = tk.Label(self, text='● ONLINE', 
                         font=('Courier New', 9, 'bold'), fg='#00FF00', bg='#0f2d55')
        status.place(x=30, y=h - 55)"""

s = s.replace(old_info, new_info)

p.write_text(s, encoding='utf-8')
print("✓ Enhanced GUI with authentic, polished styling")
print("✓ Better typography, visual hierarchy, and glow effects")
print("✓ Improved button interactions with hover effects")
print("✓ More professional, modern appearance")
