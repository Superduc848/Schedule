from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from datetime import datetime

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# testing solution from stackoverflow
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///sr.db")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE user_name = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "POST":

        #insure username is entered
        if not request.form.get("username"):
            return apology("must enter username")
        if request.form.get("password") != request.form.get("passwordchk"):
            return apology("passwords do not match")

        # check if username already exists in db
        rows = db.execute("SELECT * FROM users WHERE user_name = :username", username=request.form.get("username"))
        for row in rows:
            if len(rows) != 0:
                return apology("username taken, please try again")

        # store new username and hashed password in database
        db.execute("INSERT INTO users (user_name, hash) VALUES(:username, :pword)",
        username = request.form["username"],
        pword = pwd_context.hash(request.form["password"]))

        # direct user to login page
        return render_template("login.html")

    # should move to home page after login
    else:
        return render_template("register.html")

@app.route("/rigs", methods=["GET", "POST"])
@login_required
def rigs():

    if request.method =="GET":
        # get data from table for rigs
        riglist = db.execute("SELECT * FROM rigs ORDER BY rig_name")

        # render rigs
        return render_template("rigs.html",
        riglist = riglist)

    if request.method =="POST":
        # get data from table for rigs
        riglist = db.execute("SELECT * FROM rigs ORDER BY rig_name")

        # render rigs
        return render_template("rigs.html",
        riglist = riglist)


@app.route("/editrig", methods=["GET", "POST"])
@login_required
def editrig():

    if request.method =="GET":
        # get rig name from rigs table
        rig_id = request.args.get("rig")

        # get existing info from db to fill editrig form
        riginfo = db.execute("SELECT * FROM rigs WHERE rig_id = :rig_id",
        rig_id = rig_id)

        # render editrig
        return render_template("editrig.html",
        riginfo = riginfo)

    if request.method =="POST":
        # print(request.form) # for testing purposes
        if request.form["submit"] == "remove":
            db.execute("DELETE FROM rigs WHERE rig_id=:rig_id",
            rig_id = rig_id) # fix this - need to get rig name from somewhere
        #elif request.form["submit"] == "update": this statement works but doesnt provide rig ID
        else:
            rig_id = request.form["submit"] # get the rig_id from the value of the submit button in editrig.html
            # update rigs db with info from editrig form
            db.execute("UPDATE rigs SET num_techs=:num_techs, latitude=:latitude, longitude=:longitude WHERE rig_id=:rig_id",
            rig_id = rig_id,
            num_techs = request.form.get("num_techs"),
            latitude = request.form.get("lat"),
            longitude = request.form.get("long"))

        return redirect("/rigs")

@app.route("/addrig", methods=["GET", "POST"])
@login_required
def addrig():

    if request.method =="GET":
        return render_template("addrig.html")

    if request.method =="POST":
        # add new rig info to the rigs db
        db.execute("INSERT INTO rigs (rig_name, num_techs, latitude, longitude) VALUES (:rigname, :num_techs, :latitude, :longitude)",
        rigname = request.form.get("rigname"),
        num_techs = request.form.get("numtechs"),
        latitude = request.form.get("lat"),
        longitude = request.form.get("long"))

        return redirect("/rigs")

@app.route("/techs", methods=["GET", "POST"])
@login_required
def techs():

    if request.method =="GET":
        # get data from techs table and users table
        techdetail = db.execute("SELECT * FROM users ORDER BY last_name")

        # render
        return render_template("techs.html",
        techdetail = techdetail)

    if request.method =="POST":
        techdetail = db.execute("SELECT * FROM users ORDER BY last_name")

        return render_template("techs.html",
        techdetail = techdetail)


@app.route("/edit_tech", methods=["GET", "POST"])
@login_required
def edit_tech():

    if request.method =="GET":
        # get rig name from rigs table
        user_id = request.args.get("id")

        # get existing info from db to fill editrig form
        techinfo = db.execute("SELECT * FROM users INNER JOIN rigs ON rigs.rig_name = users.rig_name WHERE user_id=:user_id",
        user_id = user_id)

        rignames = db.execute("SELECT rig_name FROM rigs")

        # render editrig
        return render_template("edit_tech.html",
        techinfo = techinfo,
        rignames = rignames)

    if request.method =="POST":
        if request.form["submit"] == "remove":
            db.execute("DELETE FROM users WHERE user_id=:user_id",
            user_id = request.form.get("user_id"))
        else:
            user_id = request.form["submit"]
            # update rigs db with info from editrig form
            db.execute("UPDATE users SET phone=:phone, email=:email, rig_name=:rig_name, rotation=:rotation, pro_lvl=:pro_lvl WHERE user_id=:user_id",
            phone = request.form.get("phone"),
            email = request.form.get("email"),
            rig_name = request.form.get("rig_name"),
            rotation = request.form.get("rotation"),
            pro_lvl = request.form.get("pro_lvl"),
            user_id = user_id)

        return redirect("/techs")

@app.route("/addtech", methods=["GET", "POST"])
@login_required
def addtech():

    if request.method =="GET":
        rignames = db.execute("SELECT rig_name FROM rigs") # get rig names for select element
        return render_template("addtech.html",
        rignames = rignames)

    if request.method =="POST":
        # add new rig info to the rigs db
        db.execute("INSERT INTO users (first_name, last_name, phone, email, rotation, rig_name, pro_lvl) VALUES (:fname, :lname, :phone, :email, :rotation, :rig_name, :pro_lvl)",
        fname = request.form.get("first_name"),
        lname = request.form.get("last_name"),
        phone = request.form.get("phone"),
        email = request.form.get("email"),
        rotation = request.form.get("rotation"),
        rig_name = request.form.get("rig_name"),
        pro_lvl = request.form.get("pro_lvl"))

        return redirect("/techs")

@app.route("/schedule", methods=["GET", "POST"])
@login_required
def schedule():

    if request.method =="GET":
        # get data from tables: users, techs, rigs
        sched = db.execute("SELECT * FROM users INNER JOIN rigs ON rigs.rig_id = users.rigid ORDER BY last_name")

        # render
        return render_template("schedule.html",
        sched = sched)

    if request.method =="POST":

        return redirect("/rigs")