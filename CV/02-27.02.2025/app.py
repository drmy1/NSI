from flask import Flask, render_template

app = Flask(__name__)  # Creating an instance of the Flask class


@app.route("/")  # View function for endpoint '/'
def hello():
    return render_template("index.html")


# Starting a web application at 0.0.0.0.0:5000 with debug mode enabled
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
