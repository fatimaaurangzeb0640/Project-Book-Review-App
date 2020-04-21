import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://oyreyefiwsxxwi:0c317cdbec9462fdb367c60dcfab3a7e7aab8441696ad54fca9e8b0aaab37e8b@ec2-34-204-22-76.compute-1.amazonaws.com:5432/ddaeuhj6fc0uci")
db = scoped_session(sessionmaker(bind=engine))

def main():
    b = open("books.csv")
    reader = csv.reader(b)
    for isbn, title, author, pubyear in reader:
        db.execute("INSERT INTO books (isbn, title, author, pubyear) VALUES (:isbn, :title, :author, :pubyear)",
                  {"isbn":isbn, "title":title, "author":author, "pubyear":pubyear})
        print(f"Added book: {title} by {author} published in year {pubyear} with an isbn: {isbn}.")  

    db.commit()

if __name__=="__main__":
    main()
