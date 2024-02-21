import os

from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    """Show calculator"""

    # show calculator
    if request.method == "GET":
        rows_w = db.execute("SELECT weather FROM sunny_16")
        weather = [row["weather"] for row in rows_w]
        rows_p = db.execute("SELECT purpose FROM shutter_speed")
        purpose = [row["purpose"] for row in rows_p]
        return render_template("calculator.html", weather=weather, purpose=purpose)

    else:
        phototype = request.form.get("phototype")
        weather = request.form.get("weather")
        purpose = request.form.get("purpose")
        condition = request.form.get("condition")
        iso = request.form.get("iso")

        if phototype == None:
            flash("Must provide type of the photo!")
            return redirect(url_for("index"))
        elif weather == None:
            flash("Must provide lighting conditions!")
            return redirect(url_for("index"))
        elif purpose == None and condition == None:
            flash("Must provide effect or condition!")
            return redirect(url_for("index"))
        elif iso == None:
            flash("Must provide film speed (ISO)!")
            return redirect(url_for("index"))

        if phototype == "Street":
            row_a = db.execute("SELECT aperture FROM sunny_16 WHERE weather = ?", weather)
            aperture = row_a[0]["aperture"]
        elif phototype == "Landscape":
            row_id = db.execute("SELECT aperture_id FROM sunny_16 WHERE weather = ?", weather)
            id = int(row_id[0]["aperture_id"]) - 2
            if id < 1:
                id = 1
                row_a = db.execute("SELECT aperture FROM sunny_16 WHERE aperture_id = ?", id)
                aperture = row_a[0]["aperture"]
            else:
                row_a = db.execute("SELECT aperture FROM sunny_16 WHERE aperture_id = ?", id)
                aperture = row_a[0]["aperture"]
        elif phototype == "Portrait":
            row_id = db.execute("SELECT aperture_id FROM sunny_16 WHERE weather = ?", weather)
            id = int(row_id[0]["aperture_id"]) + 3
            if id > 7:
                id = 7
                row_a = db.execute("SELECT aperture FROM sunny_16 WHERE aperture_id = ?", id)
                aperture = row_a[0]["aperture"]
            else:
                row_a = db.execute("SELECT aperture FROM sunny_16 WHERE aperture_id = ?", id)
                aperture = row_a[0]["aperture"]

        if phototype == "Street":
            row_s = db.execute("SELECT speed FROM shutter_speed WHERE purpose = ?", purpose)
            speed = row_s[0]["speed"]
        else:
            if condition == "Freeze mooving objects":
                speed = "Use 1/250 for freezing walkers, 1/500 for runners"
            elif condition == "Motion blur or artistic lights":
                speed = """If you want to add motion blur or artistic lights (in low light environment)
                use 1/15 and slower shutter speed but tripod is required to eliminate shaking effect"""
            elif condition == "Low light or sunset without shadows":
                speed = "Use 60(minimal) and 30 if posing for portrait"
            else:
                speed = "Use 1/125"

        if iso == "400" and phototype == "Street":
            row_s_id = db.execute("SELECT shutter_id FROM shutter_speed WHERE speed = ?", speed)
            id = int(row_s_id[0]["shutter_id"]) + 1
            row_s = db.execute("SELECT speed FROM shutter_speed WHERE shutter_id = ?", id)
            speed = row_s[0]["speed"]

        return redirect(url_for("save", phototype=phototype, weather=weather, purpose=purpose, aperture=aperture, speed=speed, condition=condition))



@app.route("/save", methods=["GET", "POST"])
@login_required
def save():
    """Save preset of settings"""

    if request.method == "GET":

        phototype = request.args.get('phototype')
        weather = request.args.get('weather')
        purpose = request.args.get('purpose')
        aperture = request.args.get('aperture')
        speed = request.args.get('speed')
        condition = request.args.get('condition')

        rows_a = db.execute("SELECT aperture FROM sunny_16")
        aperture_table = [row["aperture"] for row in rows_a]
        rows_s = db.execute("SELECT speed FROM shutter_speed")
        speed_table = [row["speed"] for row in rows_s]
        return render_template("save_preset.html", aperture_table=aperture_table, speed_table=speed_table, phototype=phototype, weather=weather,
                               purpose=purpose, aperture=aperture, speed=speed, condition=condition)
    else:

        phototype = request.form.get("phototype")
        weather = request.form.get("weather")
        purpose = request.form.get("purpose")
        condition = request.form.get("condition")
        aperture = request.form.get("aperture")
        speed = request.form.get("speed")
        user_id = session["user_id"]
        notes = request.form.get("notes")

        # create new database table for presets
        db.execute("""INSERT INTO presets (user_id, phototype, weather, purpose, condition, aperture, speed, notes, date, time)
                   VALUES (?, ?, ?, ?, ?, ?, ? ,?, ?, ?)""",
                    user_id, phototype, weather, purpose, condition, aperture, speed, notes, datetime.now().date(), datetime.now().time())

        return redirect(url_for("list"))


@app.route("/list", methods=['GET', 'POST'])
@login_required
def list():
    """Show list of all saved presets"""
    if request.method == "GET":
        rows = db.execute("""SELECT phototype, weather, purpose, condition, aperture, speed, notes, date, time
                        FROM presets WHERE user_id = ?""", session["user_id"])

        phototype = [row["phototype"] for row in rows]
        weather = [row["weather"] for row in rows]
        purpose = [row["purpose"] for row in rows]
        condition = [row["condition"] for row in rows]
        aperture = [row["aperture"] for row in rows]
        speed = [row["speed"] for row in rows]
        notes = [row["notes"] for row in rows]
        date = [row["date"] for row in rows]
        time = [row["time"] for row in rows]

        return render_template("list.html", phototype=phototype, weather=weather, purpose=purpose, condition=condition,
                            aperture=aperture, speed=speed, notes=notes, date=date, time=time)
    else:
        phototype = request.form.get("phototype")
        if phototype != "all":
            return redirect(url_for("listselect", phototype=phototype))
        else:
            return redirect(url_for("list"))

@app.route("/listselect", methods=['GET', 'POST'])
@login_required
def listselect():
    """Show list of specific phototype saved presets"""

    if request.method == "GET":

        phototype = request.args.get('phototype')

        rows = db.execute("""SELECT phototype, weather, purpose, condition, aperture, speed, notes, date, time
                        FROM presets WHERE user_id = ? AND phototype = ?""", session["user_id"], phototype)

        phototype = [row["phototype"] for row in rows]
        weather = [row["weather"] for row in rows]
        purpose = [row["purpose"] for row in rows]
        condition = [row["condition"] for row in rows]
        aperture = [row["aperture"] for row in rows]
        speed = [row["speed"] for row in rows]
        notes = [row["notes"] for row in rows]
        date = [row["date"] for row in rows]
        time = [row["time"] for row in rows]

        return render_template("list.html", phototype=phototype, weather=weather, purpose=purpose, condition=condition,
                            aperture=aperture, speed=speed, notes=notes, date=date, time=time)
    else:
        phototype = request.form.get("phototype")
        if phototype != "all":
            return redirect(url_for("listselect", phototype=phototype))
        else:
            return render_template("list.html", phototype=phototype, weather=weather, purpose=purpose, condition=condition,
                            aperture=aperture, speed=speed, notes=notes, date=date, time=time)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username!")
            return redirect(url_for("login"))

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password!")
            return redirect(url_for("login"))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username or password")
            return redirect(url_for("login"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # When user submit form
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username!")
            return redirect(url_for("register"))

        # Ensure email was submitted
        elif not request.form.get("email"):
            flash("Must provide email!")
            return redirect(url_for("register"))

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password!")
            return redirect(url_for("register"))

        # Ensure password was confirmed
        elif not request.form.get("confirmation"):
            flash("Must confirm the password!")
            return redirect(url_for("register"))

        elif request.form.get("confirmation") != request.form.get("password"):
            flash("Passwords must match!")
            return redirect(url_for("register"))

        # Query database to ensure username is unique
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) > 0:
            flash("sorry, but this username is already taken")
            return redirect(url_for("register"))

        # Generate password hash
        hash = generate_password_hash(request.form.get("password"))

        # Insert password hash into table
        db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", request.form.get("username"), request.form.get("email"), hash)

        # Remember which user has registered and lodes in
        user_id =  db.execute("SELECT id FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = user_id[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


