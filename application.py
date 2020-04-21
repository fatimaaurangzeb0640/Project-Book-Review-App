import os
import copy
import requests
import json
from flask import Flask, session, render_template, request, redirect, jsonify, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = 'project1'

# Check for environment variable
if not "postgres://oyreyefiwsxxwi:0c317cdbec9462fdb367c60dcfab3a7e7aab8441696ad54fca9e8b0aaab37e8b@ec2-34-204-22-76.compute-1.amazonaws.com:5432/ddaeuhj6fc0uci":
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://oyreyefiwsxxwi:0c317cdbec9462fdb367c60dcfab3a7e7aab8441696ad54fca9e8b0aaab37e8b@ec2-34-204-22-76.compute-1.amazonaws.com:5432/ddaeuhj6fc0uci")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if "user_name" in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        if "user_name" in session:
            return redirect(url_for("login"))

        return render_template("index.html") 

    #Signing up and adding record to the database
    else:
       name = request.form.get("name")
       username = request.form.get("username")
       password = request.form.get("password")
       email = request.form.get("email")
       if (name == "" or username == "" or password == "" or email == ""):
           return "<h1>Please provide complete credentials to sign up."
       else:  
          if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
             db.execute("INSERT INTO users (username, password, name, email) VALUES (:username, :password, :name, :email)",
                  {"username": username, "password": password, "name": name, "email": email})
             db.commit()
             return render_template("success.html", name=name)
          else:
               return "<h1> This username already exists, go back and try again!<h1>"

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        session.permanent = True
        username = request.form.get("username")
        name = (db.execute("SELECT name FROM users WHERE username = :username", {"username": username}).fetchone())[0]

       #Make sure the user exists
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
            return "<h1>No such user. Try again!<h1>"
       
        elif username == "":
            return "<h1>Please provide complete credentials to login."   
        #Now log the user in
        password = (db.execute("SELECT password FROM users WHERE username = :username", {"username": username}).fetchone())[0]
        passwordf =request.form.get("password")
        if password == passwordf:
            session["user_name"] = username
            return render_template("afterlogin.html", name=name)
        elif passwordf == "":
            return "<h1>Please provide complete credentials to login."
        else:
            return "<h1>Incorrect password, try again.<h1>"

    else:
        if "user_name" in session:
            loginname = (db.execute("SELECT name FROM users WHERE username = :username", {"username": session["user_name"]}).fetchone())[0]
            return render_template("afterlogin.html", name = loginname)
        
        return render_template("index.html")
             
@app.route("/search", methods=["GET", "POST"])
def search(): 
    if request.method == "GET":
        return "<h1>Please go back and search for a book first<h1>"
    book = request.form.get("book")
    query= "SELECT * FROM books WHERE isbn LIKE '%"+book+"%' OR title LIKE '%"+book+"%' OR author LIKE '%"+book+"%'"

    if db.execute(query).rowcount != 0:
        books = db.execute(query).fetchall()
        return render_template("search.html", books=books)
    else:
        return "<h1>No such book exists. Try again.<h1>"

@app.route("/search/<string:isbn>", methods=["GET", "POST"])
def book(isbn):
    
    #Making sure the book exists
    if db.execute("SELECT * FROM books where isbn = :isbn", {"isbn":isbn}).rowcount == 0:
        return "<h1> No such book exists. Try again.<h1>"

    if request.method == "GET":
      book = db.execute("SELECT * FROM books where isbn = :isbn", {"isbn": isbn}).fetchone()
      reviews = db.execute("SELECT * FROM reviews WHERE isbn_rev = :isbn", {"isbn": isbn}).fetchall()
      if reviews is None:
        reviews = []

    if request.method == "POST":
        if "user_name" in session:
          book = db.execute("SELECT * FROM books where isbn = :isbn", {"isbn": isbn}).fetchone()
          username = session["user_name"]
          if db.execute("SELECT * FROM reviews WHERE isbn_rev = :isbn AND username_rev = :username", {"username": username, "isbn": isbn}).rowcount == 0:
            rate = request.form.get("rate")
            review = request.form.get("review")
            isbn = isbn
            if rate != "" and review != "":
                db.execute("INSERT INTO reviews (rate, review, isbn_rev, username_rev) VALUES (:rate, :review, :isbn_rev, :username_rev)",
                      {"rate": rate, "review": review, "isbn_rev": isbn, "username_rev": username})
                db.commit()
            else:
                return "<h1>Please do no submit an empty review!"
          else:
              return "<h1>You can't submit more than one reviews for the same book.<h1>"  
        else:
            return "<h1>Please login first to submit review.<h1>"
            
        reviews = db.execute("SELECT * FROM reviews WHERE isbn_rev = :isbn", {"isbn": isbn}).fetchall()
    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "03tcuspnBymFPsQ5aN9TA", "isbns": isbn})    
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = res.json()
    ratecount = data["books"][0]["work_ratings_count"]
    averagerating = data["books"][0]["average_rating"]


    return render_template("bookdetails.html", book = book, reviews = reviews, ratecount = ratecount, averagerating = averagerating )

@app.route("/api/<string:isbn>", methods = ["GET"])
def book_api(isbn):
    if db.execute("SELECT * FROM books where isbn = :isbn", {"isbn": isbn}).rowcount == 0:
        return jsonify({"error": "Book not found"}), 404

    book = db.execute("SELECT * FROM books where isbn = :isbn", {"isbn": isbn}).fetchone()
    review_count = db.execute("SELECT * FROM reviews WHERE isbn_rev = :isbn", {"isbn" : isbn}).rowcount
    rates = db.execute("SELECT rate FROM reviews WHERE isbn_rev = :isbn", {"isbn" : isbn}).fetchall()
    totalrate = 0
    average_score = 0
    if review_count != 0:
    
       for rate in rates:
           totalrate = totalrate + rate[0]

       average_score = totalrate / review_count
    

    return jsonify({
           "title": book.title,
            "author": book.author,
            "year": book.pubyear,
            "isbn": book.isbn,
            "review_count": review_count,
            "average_score": average_score
        })


@app.route("/logout")
def logout():
    session.pop("user_name", None)
    return render_template("index.html")




