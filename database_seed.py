import os
import requests
from import_books import import_books

from flask import Flask, session, render_template, redirect, request, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__, static_url_path='')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
db = scoped_session(sessionmaker(bind=engine))


# SEEDING "schema.sql"
with open("schema.sql") as f:
    db.execute(f.read())
    db.commit()
    db.close()

# # IMPORTING books
# import_books(db)

# books = db.execute("SELECT * FROM books").fetchall()
# print(len(books))