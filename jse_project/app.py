from flask import Flask
from main import run_analysis

app = Flask(__name__)

@app.route("/")
def home():
    result = run_analysis()
    return result