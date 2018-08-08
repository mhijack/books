import os
import requests

from flask import Flask, session, render_template, redirect, request, flash, jsonify
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


@app.route("/")
def index():
    res = requests.get("https://www.goodreads.com/book/review_counts.json?\
                        key=SUTQdylXbDve371krE4Qtg",
                       params={"title": "Harry Potter", "isbns": "9781632168146"})
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if (request.method == "GET"):
        return render_template("register.html")
    elif (request.method == "POST"):
        username = request.form.get("username")
        password = request.form.get("password")
        error = None

        if (len(username) > 0) and (len(password) > 0):
            user = db.execute("SELECT * FROM \"users\" WHERE username=:username",
                              {"username": username}).fetchone()
            if (user == None):
                db.execute("INSERT INTO \"users\" (username, password) VALUES (:username, :password)",           {
                           "username": username, "password": password})
                db.commit()
                session["username"] = username
                flash("Registered.")
                return redirect("/search")
            else:
                error = "Username already exist."
        else:
            error = "Please provide both username and password."
        flash(error)
        db.close()
        return redirect("/register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method == "GET"):
        try:
            if (globals()["session"]["username"]):
                return redirect("/search")
            else:
                render_template("login.html")
        except:
            return render_template("login.html")

    elif (request.method == "POST"):
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT username, password FROM \"users\" WHERE username=:username", {
                          "username": username}).fetchone()
        db.close()
        error = None

        if (user != None):
            if (user.username == username) and (user.password == password):
                session["username"] = username
                flash("Successfully logged in.")
                return redirect("/search")
            else:
                error = "Incorrect password."
        else:
            error = "Username not found."
        flash(error)
        return redirect("/login")


@app.route("/search", methods=["GET", "POST"])
def search():
    if (request.method == "GET"):
        try:
            if (globals()["session"]["username"]):
                return render_template("search.html")
        except:
            return redirect("/login")
    elif (request.method == "POST"):
        isbn = request.form.get("isbn") if (request.form.get("isbn") != "") else None
        title = request.form.get("title") if (request.form.get("title") != "") else None
        author = request.form.get("author") if (request.form.get("author") != "") else None

        book_by_title = db.execute("""SELECT * FROM "books" WHERE title ILIKE :title""",
                           {"title": f"%{title}%"}).fetchall() if title else []
        book_by_author = db.execute("""SELECT * FROM "books" WHERE author ILIKE :author""", {"author": f"%{author}%"}).fetchall() if author else []
        book_by_isbn = db.execute("""SELECT * FROM "books" WHERE isbn=:isbn""", {"isbn": isbn}).fetchall() if isbn else []
        books = book_by_author + book_by_title + book_by_isbn
        # db.commit()
        db.close()
        return render_template("book.html", books=books)


@app.route("/logout", methods=["GET"])
def logout():
    globals()["session"].clear()
    return redirect("/")


@app.route("/book/<isbn>")
def book(isbn):
    book = db.execute("""SELECT * FROM "books" WHERE isbn=:isbn""", {"isbn": isbn}).fetchone()
    if (book.comment):
        comment = db.execute("""SELECT username, body FROM "users" INNER JOIN "comments" ON comment_id=:comment AND comments.user_id=users.user_id""", {"comment": book.comment}).fetchone()
    else:
        comment = None

    db.close()
    return render_template("detail.html", book=book, comment=comment)


@app.route("/book/<isbn>/comment", methods=["POST"])
def comment(isbn):
    comment_body = request.form.get("comment")
    if (len(comment_body) > 0):
        # Fetch user_id
        user_id = db.execute("""SELECT user_id FROM "users" WHERE username=:username""", {"username": globals()["session"]["username"]}).fetchone()[0]

        # Create new comment and relate user_id to that comment
        db.execute("""INSERT INTO "comments" (user_id, body) VALUES (:user_id, :body)""", {"user_id": user_id, "body": comment_body})

        # Extract comment_id
        comment_id = db.execute("""SELECT comment_id FROM "comments" WHERE body=:comment_body""", {"comment_body": comment_body}).fetchone()[0]

        # Update "books"
        db.execute("""UPDATE books SET comment=:comment_id WHERE isbn=:isbn""", {"comment_id": comment_id, "isbn": isbn})

        db.commit()
        db.close()
    return redirect("/book/" + isbn)


@app.route("/api/<isbn>")
def api(isbn):
    goodreads_api_key = "SUTQdylXbDve371krE4Qtg"
    url = f"https://www.goodreads.com/book/review_counts.json?key={goodreads_api_key}&isbns={isbn}"
    response = requests.get(url)
    # TEST isbn: 0441172717

    if (response.status_code == 200):
        response = response.json()
        review_count = response["books"][0]["reviews_count"]
        average_score = response["books"][0]["average_rating"]
        try:
            (title, author, year) = db.execute("""SELECT title, author, year FROM "books" WHERE isbn=:isbn""", {"isbn":isbn}).fetchone()
        except:
            return jsonify({"error": "Book not found."})

        result = {
            "title": title,
            "author": author,
            "year": str(year),
            "isbn": isbn,
            "review_count": str(review_count),
            "average_score": str(average_score)
        }
        return jsonify(result)
    else:
        error = "Server did not respond correctly."
        flash(error)
        return redirect("/search")
