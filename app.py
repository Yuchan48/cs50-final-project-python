import os
import sqlite3
from tempfile import mkdtemp
from flask import Flask, flash, request, session, render_template, redirect
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app= Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

## database
con = sqlite3.connect("issue.db", check_same_thread=False)
cursor = con.cursor()
#cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, hash TEXT )""")
#cursor.execute("""CREATE TABLE IF NOT EXISTS issues (id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT, created_date DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

@app.route("/")
@login_required
def index():
    titles = cursor.execute("SELECT * FROM titles")
    print("titles: ", titles)
    return render_template("index.html", titles= titles)

# title 
@app.route("/tcreate", methods=["POST"])
def title_create():
    new_title = request.form.get('title')
    if not new_title:
        flash("Missing new title")
        return render_template("index.html")
    else:
        cursor.execute("""INSERT INTO titles (title) VALUES (?)""", (new_title,))
        con.commit()
        return redirect("/")

@app.route("/tdelete/<int:id>")
def title_delete(id):
    try:
        cursor.execute("""DELETE FROM titles WHERE id = ?""", (id,))
        con.commit()
        return redirect("/")
    except:
        return render_template("error.html", message="There was an error deleting the title")

# issue
@app.route("/issues/<int:id>")
@login_required
def issues(id):
    cursor.execute("""SELECT * FROM issues JOIN titles ON issues.title_id = titles.id WHERE titles.id = ?""", (id,))
    temp = cursor.fetchall()
    cursor.execute("""SELECT * FROM titles WHERE id = ?""", (id,))
    temp2 = cursor.fetchone()
    
    return render_template("issues.html",  issues=temp, title=temp2)
    
@app.route("/create/<int:id>", methods=["POST"])
def issue_create(id):
    new_issue = request.form.get('issue')
    name = request.form.get("name")
    user_id = session["user_id"]
    if not new_issue or not name:
        return redirect("/issues/" + str(id))
    else:
        cursor.execute("""INSERT INTO issues (name, message, title_id, user_id) VALUES (?, ?, ?, ?)""", (name, new_issue, id, user_id,))
        con.commit()
        return redirect("/issues/" + str(id))

@app.route("/update/<int:id>", methods=["POST"])
def issue_update(id):
    issue_id = request.form.get('issue_id')
    message = request.form.get("message")
    state = request.form.get("state")
    if not issue_id:
        return redirect("/issues/" + str(id))
    elif not message:
        cursor.execute("""UPDATE issues SET state = ?, updated_at = DATETIME('now') WHERE id = ?""", ( state, issue_id,))
        con.commit()
    elif not state:
        cursor.execute("""UPDATE issues SET message = ?, updated_at = DATETIME('now') WHERE id = ?""", ( message, issue_id,))
        con.commit()
    else:
        cursor.execute("""UPDATE issues SET message = ?, state = ?, updated_at = DATETIME('now') WHERE id = ?""", (message, state, issue_id,))
        con.commit()  
    return redirect("/issues/" + str(id))

@app.route("/delete/<int:id>/<int:title_id>")
def issue_delete(id, title_id):
    try:
        cursor.execute("""DELETE FROM issues WHERE id = ?""", (id,))
        con.commit()
        return redirect("/issues/" + str(title_id))
    except:
        return render_template("error.html", message="There was an error deleting the issue")

# my page
@app.route("/mypage")
@login_required
def mypage():
    user_id = session["user_id"]
    cursor.execute("""SELECT issues.* FROM issues JOIN users ON issues.user_id = users.id WHERE users.id = ?""", (user_id,))
    temp = cursor.fetchall()
    return render_template("mypage.html",  issues=temp)

@app.route("/mupdate", methods=["POST"])
def mypage_update():
    issue_id = request.form.get('issue_id')
    message = request.form.get("message")
    state = request.form.get("state")
    if not issue_id:
        return redirect("/mypage")
    elif not message:
        cursor.execute("""UPDATE issues SET state = ?, updated_at = DATETIME('now') WHERE id = ?""", ( state, issue_id,))
        con.commit()
    elif not state:
        cursor.execute("""UPDATE issues SET message = ?, updated_at = DATETIME('now') WHERE id = ?""", ( message, issue_id,))
        con.commit()
    else:
        cursor.execute("""UPDATE issues SET message = ?, state = ?, updated_at = DATETIME('now') WHERE id = ?""", (message, state, issue_id,))
        con.commit()  
    return redirect("/mypage")

@app.route("/mdelete/<int:id>")
def mypage_delete(id):
    try:
        cursor.execute("""DELETE FROM issues WHERE id = ?""", (id,))
        con.commit()
        return redirect("/mypage")
    except:
        return render_template("error.html", message="There was an error deleting the issue")

# all issues
@app.route("/allissues")
@login_required
def all_issues():
    cursor.execute("""SELECT issues.* FROM issues""")
    temp = cursor.fetchall()
    return render_template("all_issues.html",  issues=temp)

@app.route("/alldelete/<int:id>")
def all_delete(id):
    try:
        cursor.execute("""DELETE FROM issues WHERE id = ?""", (id,))
        con.commit()
        return redirect("/allissues")
    except:
        return render_template("error.html", message="There was an error deleting the issue")

# signin
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            flash("Missing username")
            return render_template("login.html")

        elif not request.form.get("password"):
            flash("Missing password")
            return render_template("login.html")

        
        cursor.execute("""SELECT * FROM users wHERE username = ?""", (request.form.get("username"),))
        rows = cursor.fetchall()
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            flash("Invalid username or password")
            return render_template("login.html")


        session["user_id"] = rows[0][0]
        return redirect("/")
 
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")
        if not username or not password or not confirmPassword:
            flash("Missing required field")
            return render_template("register.html")
        elif len(password) < 8:
            flash("Password must be at least 8 characters")
            return render_template("register.html")
        elif not password == confirmPassword:
            flash("Password and confirm password does not match")
            return render_template("register.html")

        cursor.execute("""SELECT * FROM users WHERE username = ?""", (username,))
        namerow = cursor.fetchall()
        
        if len(namerow) != 0:
            flash("Username is already taken")
            return render_template("register.html")
        else:
            hashedPassword = generate_password_hash(password)
            cursor.execute("""INSERT INTO users (username, hash) VALUES (?, ?)""", (username, hashedPassword,))
            con.commit()

            item = cursor.execute("""SELECT * FROM users WHERE username = ?""", (username,))            
            for row in item:
                session["user_id"] = row[0]

            cursor.close()
            return redirect("/")
    else:
        return render_template("register.html")



if __name__ == "__main__":
      app.run(debug=True)      