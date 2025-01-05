import tkinter as tk


class ChatBox:
    @staticmethod
    def create_chat_area(container):
        """
        Creates the chat area in the game room with a vertical scrollbar.
        """
        # Frame to hold the chat display and scrollbar
        chat_frame = tk.Frame(container, bg="#2C3E50")
        chat_frame.pack(fill="both", expand=True, pady=10)

        # Chat Display (Text widget) with vertical Scrollbar
        chat_scrollbar = tk.Scrollbar(chat_frame, orient=tk.VERTICAL)
        chat_display = tk.Text(
            chat_frame,
            height=20,
            width=30,
            state=tk.DISABLED,
            wrap=tk.WORD,
            bg="#34495E",
            fg="white",
            yscrollcommand=chat_scrollbar.set
        )
        chat_display.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        # Attach the scrollbar to the Text widget
        chat_scrollbar.config(command=chat_display.yview)
        chat_scrollbar.pack(side=tk.RIGHT, fill="y")

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
            # Enable writing to the chat display
            display_widget.config(state=tk.NORMAL)

            # Add the message and scroll to the bottom
            display_widget.insert(tk.END, f"You: {message}\n")
            display_widget.config(state=tk.DISABLED)  # Disable editing again
            display_widget.see(tk.END)  # Auto-scroll to the latest message

            # Clear the input field
            input_widget.delete(0, tk.END)
