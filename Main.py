from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import Chatbot
import RecommendationEngine
import Vectorization
import SaveChat
import os
app = Flask(__name__)

class Main:
    def __init__(self):
        self.client = OpenAI()
        self.recommendation_engine = RecommendationEngine.RecommendationEngine(self.client)
        self.chatbot = Chatbot.Chatbot(self.client, self.recommendation_engine)
        self.save = SaveChat.SaveChat()
        self.vectorization = Vectorization.Vectorization(self.client)
        if not os.path.exists("data/products.csv"):
                with open("products.txt", "r", encoding="utf-8") as f:
                    text = f.read()
                    print("File loaded")
                self.vectorization.create_df(text)
                print("vectorization completed")

    def process_input(self, user_input):
        self.save.save_conversation(self.save.file, user_input + "\n")
        output = self.chatbot.process_dialogue(user_input)
        self.save.save_conversation(self.save.file, output + "\n")
        return output

main = Main()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['user_input']
    output = main.process_input(user_input)
    return jsonify({'output': output})

if __name__ == "__main__":
    app.run(debug=True)
