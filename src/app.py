# src/chatbot_pysus/app.py
from agent import run_agent

if __name__ == "__main__":
    pergunta = input("Você: ")
    resposta = run_agent(pergunta)
    print("Chatbot:", resposta)
