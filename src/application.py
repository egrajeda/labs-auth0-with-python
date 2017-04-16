import json
import os
import requests
from flask import Flask, request, redirect, session, render_template

app = Flask(__name__)
app.secret_key = "not_a_secret"

AUTH0_HOST = os.environ["AUTH0_HOST"]
AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]

@app.route("/")
def index():
    login_url = "https://{host}/authorize?response_type=code&scope=openid%20profile&client_id={client_id}&redirect_uri=http://localhost:5000/callback&connection=Username-Password-Authentication".format(
            host=AUTH0_HOST, client_id=AUTH0_CLIENT_ID)

    return render_template("index.html", login_url=login_url)

@app.route("/profile")
def profile():
    if "user_info" not in session:
        return redirect("/")

    return render_template("profile.html")

@app.route("/callback")
def callback():
    token_info = requests.post("https://{host}/oauth/token".format(host=AUTH0_HOST),
            headers={'content-type': 'application/json'},
            data=json.dumps({
                "client_id": AUTH0_CLIENT_ID,
                "client_secret": AUTH0_CLIENT_SECRET,
                "redirect_uri": "http://localhost:5000/callback",
                "code": request.args.get("code"),
                "grant_type": 'authorization_code'
                })).json()

    user_info = requests.get("https://{host}/userinfo?access_token={access_token}".format(host=AUTH0_HOST, access_token=token_info["access_token"])).json()

    session["user_info"] = user_info

    return redirect("/profile")

@app.route("/logout")
def logout():
    if "user_info" not in session:
        return redirect("/")
    session.pop("user_info")

    return redirect("https://{host}/v2/logout?client_id={client_id}&returnTo=http://localhost:5000".format(host=AUTH0_HOST, client_id=AUTH0_CLIENT_ID))

if __name__ == "__main__":
    app.run()
