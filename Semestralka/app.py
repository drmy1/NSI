from api_routes import creds, data_manipulation, dash, terminal_bp
from extensions import limiter
from flask import Flask, redirect, request, jsonify
import os
import logging
import threading
from utills import mqtt_client_handler

ssl_context = ("./cert/certificate.pem", "./cert/key.pem")


class Config:
    # SCHEDULER_API_ENABLED = True
    debug = True
    host = "127.0.0.1"
    port = 5000
    use_reloader = False
    ssl_context = ssl_context


app = Flask(__name__, static_url_path="/static", static_folder="static")
app.config.from_object(Config())
limiter.init_app(app)
app.secret_key = os.urandom(1)
app.register_blueprint(creds, url_prefix="/api")
app.register_blueprint(data_manipulation, url_prefix="/api")
app.register_blueprint(dash, url_prefix="/api")
app.register_blueprint(terminal_bp, url_prefix="/api")


logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    # Define the format of log messages
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a",
    encoding="utf8",
)


@app.route("/", methods=["GET", "POST"])
def main():
    return redirect("/api/login")


@app.before_request
def redirect_to_https():
    if not request.is_secure:
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Překročen limit požadavků"), 429


if __name__ == "__main__":
    logging.info("App started")
    threads = [
        threading.Thread(target=mqtt_client_handler.connect),
        threading.Thread(
            target=app.run,
            kwargs={
                "host": Config.host,
                "port": Config.port,
                "debug": Config.debug,
                "use_reloader": Config.use_reloader,
                "ssl_context": Config.ssl_context,
            },
        ),
    ]
    for thread in threads:
        thread.start()
        logging.debug(f"Thread {thread.name} started")
    for thread in threads:
        thread.join()
        logging.debug(f"Thread {thread.name} joined")
