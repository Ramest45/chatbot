import random
import json

import random
import json
import torch
from flask import Flask, request, jsonify, render_template
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Giats"

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('chatt.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    sentence = data.get("message")
    if not sentence:
        return jsonify({"response": "I do not understand..."}), 400

    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                response = random.choice(intent['responses'])
                return jsonify({"response": response})
    else:
        return jsonify({"response": "I do not understand..."}), 200

if __name__ == '__main__':
    app.run(debug=True)