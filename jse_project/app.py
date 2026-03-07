from flask import Flask
from jse_project.main import run_analysis
import threading

app = Flask(__name__)

# Simple cache for HTML output
html_cache = "<h2>Loading data... please refresh in a few seconds.</h2>"

def fetch_data():
    global html_cache
    html_cache = run_analysis()

# Fetch data in a separate thread at startup
threading.Thread(target=fetch_data).start()

@app.route("/")
def home():
    return html_cache

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)