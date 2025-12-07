import os
import sqlite3
from uuid import uuid4
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, g, flash
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# -----------------------------------------------
# ENVIRONMENT SETUP
# -----------------------------------------------
load_dotenv()
app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "app.db")
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


# -----------------------------------------------
# DATABASE CONNECTION
# -----------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            name TEXT,
            bio TEXT,
            avatar TEXT,
            instagram TEXT,
            twitter TEXT,
            youtube TEXT,
            linkedin TEXT,
            github TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS custom_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            label TEXT,
            url TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)
    db.commit()


@app.before_request
def before_request():
    init_db()
    g.user = None
    user_id = session.get("user_id")
    if user_id is not None:
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        g.user = user


# -----------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_profile_for_user(user_id):
    db = get_db()
    row = db.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def get_custom_links(user_id):
    db = get_db()
    rows = db.execute("SELECT * FROM custom_links WHERE user_id = ?", (user_id,)).fetchall()
    return [dict(r) for r in rows]


def save_profile_for_user(user_id, data):
    db = get_db()
    existing = get_profile_for_user(user_id)
    if existing:
        db.execute("""
            UPDATE profiles
            SET name=?, bio=?, avatar=?, instagram=?, twitter=?, youtube=?, linkedin=?, github=?
            WHERE user_id=?
        """, (
            data.get("name"), data.get("bio"), data.get("avatar"),
            data.get("instagram"), data.get("twitter"),
            data.get("youtube"), data.get("linkedin"),
            data.get("github"), user_id
        ))
    else:
        db.execute("""
            INSERT INTO profiles (user_id, name, bio, avatar, instagram, twitter, youtube, linkedin, github)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, data.get("name"), data.get("bio"), data.get("avatar"),
            data.get("instagram"), data.get("twitter"), data.get("youtube"),
            data.get("linkedin"), data.get("github")
        ))
    db.commit()


# -----------------------------------------------
# AUTH ROUTES
# -----------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not username or not password:
            flash("Username and password are required.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
                flash("Account created! You can sign in now.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Username already taken. Try another one.", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            flash("Signed in successfully.", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


# -----------------------------------------------
# DASHBOARD / PROFILE EDIT
# -----------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if not g.user:
        return redirect(url_for("login"))

    user_id = g.user["id"]
    db = get_db()
    profile = get_profile_for_user(user_id)
    custom_links = get_custom_links(user_id)

    if request.method == "POST":
        avatar_path = profile["avatar"] if profile and profile.get("avatar") else ""
        file = request.files.get("avatar")
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            filename = f"user{user_id}_{uuid4().hex}.{ext}"
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            avatar_path = f"uploads/{filename}"

        profile_data = {
            "name": request.form.get("name", "").strip(),
            "bio": request.form.get("bio", "").strip(),
            "avatar": avatar_path,
            "instagram": request.form.get("instagram", "").strip(),
            "twitter": request.form.get("twitter", "").strip(),
            "youtube": request.form.get("youtube", "").strip(),
            "linkedin": request.form.get("linkedin", "").strip(),
            "github": request.form.get("github", "").strip(),
        }

        save_profile_for_user(user_id, profile_data)

        # custom links
        db.execute("DELETE FROM custom_links WHERE user_id = ?", (user_id,))
        labels = request.form.getlist("customLabel[]")
        urls = request.form.getlist("customUrl[]")
        for label, url in zip(labels, urls):
            if url.strip():
                db.execute(
                    "INSERT INTO custom_links (user_id, label, url) VALUES (?, ?, ?)",
                    (user_id, label.strip(), url.strip())
                )
        db.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for("index"))

    return render_template("index.html", profile=profile or {}, custom_links=custom_links)


# -----------------------------------------------
# PUBLIC PROFILE
# -----------------------------------------------
@app.route("/u/<username>")
def public_profile(username):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user:
        return render_template("public_profile.html", profile=None, username=username)

    profile = get_profile_for_user(user["id"])
    custom_links = get_custom_links(user["id"])
    return render_template("public_profile.html", profile=profile, username=username, custom_links=custom_links)


# -----------------------------------------------
# MAIN
# -----------------------------------------------
if __name__ == "__main__":
    # For Render, use Gunicorn in production
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
