from api_routes import creds, data_manipulation, dash
from flask import Flask, redirect
import os
app = Flask(__name__, static_url_path="/static", static_folder="static")


class Config:
    SCHEDULER_API_ENABLED = True
    debug = True


app = Flask(__name__, static_url_path="/static", static_folder="static")
app.secret_key = os.urandom(1)
app.config.from_object(Config())
app.register_blueprint(creds, url_prefix="/api")
app.register_blueprint(data_manipulation, url_prefix="/api")
app.register_blueprint(dash, url_prefix="/api")


@app.route("/", methods=["GET", "POST"])
def main():#1: CPU utilization

    return redirect("/api/login")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
