import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Coroutine
import asyncio
from datetime import datetime


class ChatBox:
    def __init__(self, parent: tk.Widget, styles: dict):
        self.parent = parent
        self.styles = styles
        self.on_message_sent: Optional[Callable[[str], Coroutine]] = None
        self._create_widgets()

    def _create_widgets(self):
        self.frame = tk.Frame(self.parent, bg=self.styles["frame_bg"])
        self.frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Messages area
        messages_frame = tk.Frame(self.frame, bg=self.styles["frame_bg"])
        messages_frame.pack(fill="both", expand=True)

        self.messages_text = tk.Text(
            messages_frame,
            bg=self.styles["bg_color"],
            fg=self.styles["fg_color"],
            wrap=tk.WORD,
            state="disabled",
            height=20,
            font=("Arial", 10),
        )
        self.messages_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(messages_frame, command=self.messages_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.messages_text.configure(yscrollcommand=scrollbar.set)

        # Input area
        input_frame = tk.Frame(self.frame, bg=self.styles["frame_bg"])
        input_frame.pack(fill="x", pady=(5, 0))

        self.message_entry = tk.Entry(
            input_frame,
            bg=self.styles["bg_color"],
            fg=self.styles["fg_color"],
            insertbackground=self.styles["fg_color"],
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        send_button = tk.Button(
            input_frame,
            text="Send",
            command=lambda: asyncio.create_task(self._send_message()),
            bg=self.styles["button_bg"],
            fg=self.styles["button_fg"],
        )
        send_button.pack(side="right")

        # Bind Enter key to send message
        self.message_entry.bind(
            "<Return>", lambda e: asyncio.create_task(self._send_message())
        )

    async def _send_message(self):
        message = self.message_entry.get().strip()
        if message and self.on_message_sent:
            await self.on_message_sent(message)
            self.message_entry.delete(0, tk.END)
        self.message_entry.focus_set()

    def add_message(self, player_name: str, message: str, timestamp: float = None):
        self.messages_text.configure(state="normal")

        # Format timestamp
        time_str = (
            datetime.fromtimestamp(timestamp).strftime("%H:%M")
            if timestamp
            else datetime.now().strftime("%H:%M")
        )

        # Format message
        formatted_message = f"[{time_str}] {player_name}: {message}\n"

        self.messages_text.insert(tk.END, formatted_message)
        self.messages_text.see(tk.END)  # Auto-scroll to bottom
        self.messages_text.configure(state="disabled")

    def add_system_message(self, message: str):
        self.messages_text.configure(state="normal")
        formatted_message = f"*** {message} ***\n"
        self.messages_text.insert(tk.END, formatted_message)
        self.messages_text.see(tk.END)
        self.messages_text.configure(state="disabled")

    def clear(self):
        self.messages_text.configure(state="normal")
        self.messages_text.delete(1.0, tk.END)
        self.messages_text.configure(state="disabled")
