import pandas as pd


def import_books(db):
    f = pd.read_csv("books.csv")
    isbns = f["isbn"]
    titles = f["title"]
    authors = f["author"]
    years = f["year"]

    for i in range(len(isbns)):
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)"\
        , {"isbn": isbns[i], "title": titles[i], "author": authors[i], "year": int(years[i])})
    db.commit()
