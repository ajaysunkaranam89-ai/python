from flask import Flask
import os

app = Flask(__name__)

APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

@app.route("/")
def home():
    return {
        "message": "Hello from Python Kubernetes!",
        "environment": APP_ENV,
        "version": APP_VERSION
    }

@app.route("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
