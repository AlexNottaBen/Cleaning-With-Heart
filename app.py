#! /usr/bin/python3
# -*- coding: utf-8 -*-
from os import environ

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager, login_required
from flask_restful import Api

from database.connector import create_tables
from resources.booking_resource import BookingResource
from resources.login_resource import LoginResource
from views.booking_view import BookingView
from views.calendar_view import CalendarView
from views.index_view import IndexView
from views.login_view import LoginView
from views.logout_view import LogoutView

load_dotenv()
create_tables()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = environ["SECRET_KEY"]
login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.user_loader(LoginResource().load_user)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "primary"

api = Api(app=app)

app.add_url_rule(rule="/", view_func=IndexView.as_view("index"))
app.add_url_rule(rule="/login", view_func=LoginView.as_view("login"))
app.add_url_rule(rule="/logout", view_func=LogoutView.as_view("logout"))
app.add_url_rule(rule="/booking", view_func=BookingView.as_view("booking"))
app.add_url_rule(
    rule="/calendar",
    view_func=login_required(
        CalendarView.as_view("calendar"),
    ),
)
api.add_resource(BookingResource, "/api/booking")


def main():
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    main()
