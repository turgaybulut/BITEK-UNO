import tkinter as tk


class ChatBox:
    @staticmethod
    def create_chat_area(container):
        """
        Creates the chat area in the game room.
        """
        # Chat Display
        chat_display = tk.Text(container, height=20, width=30, state=tk.DISABLED)
        chat_display.pack(pady=10)

        # Chat Input
        chat_input = tk.Entry(container, width=25)
        chat_input.pack(pady=5)

        # Send Button
        tk.Button(
            container,
            text="Send",
            command=lambda: ChatBox.send_chat_message(chat_input, chat_display),
            bg="#27AE60",
            fg="white"
        ).pack()

    @staticmethod
    def send_chat_message(input_widget, display_widget):
        """
        Sends a message to the chat area.
        """
        message = input_widget.get()
        if message.strip():
            display_widget.config(state=tk.NORMAL)
            display_widget.insert(tk.END, f"You: {message}\n")
            display_widget.config(state=tk.DISABLED)
            input_widget.delete(0, tk.END)
