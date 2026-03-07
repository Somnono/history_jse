from flask import Flask
from jse_project.main import run_analysis

app = Flask(__name__)

@app.route("/")
def home():
    return run_analysis()