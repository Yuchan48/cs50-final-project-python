# Issue Tracker

#### Video Demo:  <URL HERE>

#### Description:
Simple issue tracker created with Python Flask, SQL, sqlite3.

- Login, register functions with hashed password stored in the SQL and login data stored in the session storage.
- In the home screen, you can see the titles of the issues with create/delete titles functions.
- If you press details on the title in the home screen, you can see all the corresponding issues. You can also create/delete/update issues.
- In the issue screen, you can see all the existing issues with delete function.
- In the mypage screen, you can see all the issues which you created, with delete/update funtions.

#### how to run

- run `.\env\Scripts\activate` to activate the virtual server.
- run `python app.py` to run the server, then go to localhost 5000 

#### issues.db

- CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, hash TEXT )

- CREATE TABLE "titles" (
	"id"	INTEGER NOT NULL,
	"title"	TEXT NOT NULL,
	PRIMARY KEY("id")
)

- CREATE TABLE "issues" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"message"	TEXT NOT NULL,
	"created_date"	DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"updated_at"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"title_id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"state"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id")
)