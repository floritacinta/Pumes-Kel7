

# Import necessary libraries
from tkinter import *
from tkinter import messagebox

# Create chatbot window
chatbot = Tk()
chatbot.title("Chatbot")

# Set background color to purple
chatbot.configure(bg="purple")

# Create chat window
chat_window = Text(chatbot, height=20, width=50)
chat_window.pack()

# Create entry field for user input
user_input = Entry(chatbot, width=50)
user_input.pack()

# Function to send user input to chat window
def send():
    # Get user input
    message = user_input.get()

    # Clear entry field
    user_input.delete(0, END)

    # Display user input in chat window
    chat_window.insert(END, "You: " + message + "\n")

# Create button to send user input
send_button = Button(chatbot, text="Send", command=send)
send_button.pack()

# Start chatbot window
chatbot.mainloop()
