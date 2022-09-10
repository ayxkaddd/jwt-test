import os
from flask import Flask, jsonify, request, session, make_response, render_template, url_for
from functools import wraps
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "randomkey"


def check_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.args.get("token")
        print(token)
        if not token:
            return jsonify({"message": "missing token"}), 403
        try:
            date = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            return jsonify({"date": f"{date}"})
        except jwt.ExpiredSignatureError:
            return render_template("login.html")
        except Exception as e:
            return jsonify({"exception": f"wrong token"}), 403
    return wrapped


@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("logged_in"):
        return render_template("login.html")
    else:
        return "logged_in"


@app.route("/public")
def public():
    return "public page"


@app.route("/auth", methods=["GET"])
@check_token
def private():
    return "null"

@app.route("/login", methods=["POST"])
def login():
    if request.form['username'] and request.form['password'] == "password":
        session["logged_in"] = True
        token = jwt.encode({
            'user': request.form["username"],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=600)
        },
        app.config['SECRET_KEY'])
        return jsonify({'token': token})
    else:
        return make_response("Unable to verify", 403, {"WWW-Authenticate": "Basic realms : 'login bruh idk'"})


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
