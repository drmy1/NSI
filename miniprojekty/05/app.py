from api_routes import creds, data_manipulation, dash

from extensions import limiter


from flask import Flask, redirect, request, jsonify
import os
import logging

app = Flask(__name__, static_url_path="/static", static_folder="static")


class Config:
    SCHEDULER_API_ENABLED = True
    debug = True


logging.basicConfig(
    level=logging.INFO,  # Set the logging level to DEBUG
    # level=logging.DEBUG,
    # Define the format of log messages
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",  # Specify the file to write logs to
    # Specify the file writing mode ('w' for overwrite, 'a' for append)
    filemode="a",
    encoding="utf8",
)


app = Flask(__name__, static_url_path="/static", static_folder="static")
limiter.init_app(app)
app.secret_key = os.urandom(1)
app.config.from_object(Config())
app.register_blueprint(creds, url_prefix="/api")
app.register_blueprint(data_manipulation, url_prefix="/api")
app.register_blueprint(dash, url_prefix="/api")


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
    ssl_context = ("./cert/certificate.pem", "./cert/key.pem")
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False,
        ssl_context=ssl_context,
    )
