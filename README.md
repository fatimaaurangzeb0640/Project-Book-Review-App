# Book Review Application using Flask

Web Programming with Python and JavaScript

The project contains an application.py file which is the main flask application and contains all the functions to run 
the application. Another import.py file is also attached which is used to add all the data from books.csv to the database at heroku 
connected to the flask app. The database contains three tables namely, books, users and reviews. The books tables has columns
isbn (primary key), title, author and pubyear. The users table has columns username (primary key), password, name 
and email. The reviews table has comlums id (primary key), rate, reviews, isbn_rev (which references the isbn column in the book
table) and username_rev (which references username column in the users table). 

The first page that appears when user runs the application is index.html which is dealt by index() function in the flask app. 
On this page, users have two options: they can either login or sign up which are dealt by login() and signup() functions respectively. 
While signing up, users have to give all the credentials or they can't proceed. No two users can have same usernames. Same is the case with loging in. Users need to provide all credentials or else they can't proceed. 

After loging in, the user's info is stored in their session and users are taken to a page afterlogin.html where 
they can search the books. In order to prevent the web application from crashing users cannot go forward without 
providing the name of the book. If users make a get request to login/signup page (home page) while they are already 
logged in, they're are directly taken to the afterlogin.html page for convenience. 

After searching for a book all the matching results are displayed on search.html and user can choose from them
even if user types in only a part of book's title, author or isbn and if the book doesn't exist a message is returned.  
After choosing the book bookdetails.html page is opened where details of the book, review count and average rate 
from Goodreads website (using their api) and all the reviews from all the other users are displayed from the database. 
On this page user can also submit their review and their review will be displayed instantly with other reviews of the book.
No user is allowed to submit more than one reviews for the same book or submit any empty review.

The user can also make a get request with /api/<isbn> (where isbn is the book's isbn number) and a json file would be
returned to them contaning the required details of the book. If the isbn is not in the database, a 404 error is returned.

Different functions have been used in the flask app to carry the operations expalined above.

On every page, there's a logout button for users to logout by which their session is closed and their credentails
are removed.

RAW sql commands are used to select and insert data from the database.

Styling of the pages is done using css properties and bootstrap. An image is also added on the main page.
