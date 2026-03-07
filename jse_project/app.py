from flask import Flask
from jse_project.main import run_analysis

app = Flask(__name__)

# Fetch the data immediately at startup
html_cache = run_analysis()

@app.route("/")
def home():
    return html_cache

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)