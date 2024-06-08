
import streamlit as st 

# Create a function for the home page
def home():
    st.title("Home")
    st.write("Welcome to our website!")
    st.write("Here, you can find information about the menstrual cycle, pumes, a chatbot, consultation with doctors, and articles related to women's health.")

# Create a function for the menstrual cycle page
def menstrual_cycle():
    st.title("Siklus Haid")
    st.write("Learn about the stages and duration of the menstrual cycle, as well as common symptoms and how to track your cycle.")

# Create a function for the pumes page
def pumes():
    st.title("Apa itu PUMES?")
    st.write("PUMES stands for Perawatan dan Upaya Mencegah Endometriosis Sejak Dini (Prevention and Treatment of Endometriosis from an Early Age). Learn more about this program and how it can help prevent endometriosis.")

# Create a function for the chatbot page
def chatbot():
    st.title("Chatbot")
    st.write("Have a question? Our chatbot is here to help! Simply type in your question and our chatbot will provide you with the best answer.")

# Create a function for the consultation with doctors page
def consultation():
    st.title("Konsultasi Dokter")
    st.write("Need to speak with a doctor? Our website offers virtual consultations with gynecologists who specialize in women's health.")

# Create a function for the articles page
def articles():
    st.title("Artikel")
    st.write("Read informative articles about women's health, including topics such as menstrual health, fertility, and menopause.")

# Create a list of options for the sidebar
options = ["Home", "Siklus Haid", "Apa itu PUMES?", "Chatbot", "Konsultasi Dokter", "Artikel"]

# Create a function to handle the sidebar navigation
def navigation():
    choice = st.sidebar.selectbox("Navigation", options)
    if choice == "Home":
        home()
    elif choice == "Siklus Haid":
        menstrual_cycle()
    elif choice == "Apa itu PUMES?":
        pumes()
    elif choice == "Chatbot":
        chatbot()
    elif choice == "Konsultasi Dokter":
        consultation()
    elif choice == "Artikel":
        articles()

# Call the navigation function to display the sidebar and content
navigation()