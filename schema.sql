-- DROP TABLE IF EXISTS "users" CASCADE;
-- DROP TABLE IF EXISTS "books" CASCADE;
-- DROP TABLE IF EXISTS "comments" CASCADE;

-- CREATE TABLE users (
--     user_id serial PRIMARY KEY NOT NULL,
--     username TEXT NOT NULL,
--     password TEXT NOT NULL
-- );

-- CREATE TABLE comments (
--     comment_id serial PRIMARY KEY NOT NULL,
--     user_id INTEGER NOT NULL,
--     body TEXT NOT NULL,
--     FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
-- );

-- CREATE TABLE books (
--     book_id serial PRIMARY KEY NOT NULL,
--     isbn TEXT NOT NULL,
--     author TEXT NOT NULL,
--     title TEXT NOT NULL,
--     year INTEGER NOT NULL,
--     comment INTEGER,
--     FOREIGN KEY (comment) REFERENCES comments (comment_id) ON DELETE CASCADE ON UPDATE CASCADE
-- );

-- INSERT INTO users (username, password) VALUES (j, j);
-- INSERT INTO comments (user_id, body) VALUES (1, 'comment by J');
-- UPDATE books SET comment=1 WHERE book_id=4;

-- CREATE TABLE post (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   author_id INTEGER NOT NULL,
--   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   title TEXT NOT NULL,
--   body TEXT NOT NULL,
--   FOREIGN KEY (author_id) REFERENCES user (id)
-- );