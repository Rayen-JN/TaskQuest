from flask import render_template , Blueprint, redirect

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "log in "

@main.route("/home")
def home():
    return "home "


@main.route("user")
def user():
    return "user"

