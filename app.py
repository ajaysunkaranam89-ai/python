from flask import Flask, render_template, jsonify
import os
import socket
import time

app = Flask(__name__)

APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
START_TIME = time.time()


@app.route("/")
def home():
    return render_template(
        "index.html",
        env=APP_ENV,
        version=APP_VERSION,
        hostname=socket.gethostname(),
    )


@app.route("/api/info")
def info():
    return jsonify({
        "message": "Hello from Python Kubernetes!",
        "environment": APP_ENV,
        "version": APP_VERSION,
        "hostname": socket.gethostname(),
        "uptime_seconds": round(time.time() - START_TIME, 1),
    })


@app.route("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
