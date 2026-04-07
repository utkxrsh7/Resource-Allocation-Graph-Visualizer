from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Resource Allocation Graph Visualizer</h1><p>Website is running 🚀</p>"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)