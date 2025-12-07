import os
import sqlite3
from uuid import uuid4

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    g,
    flash,
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# CHANGE THIS IN REAL DEPLOYMENTS
app.secret_key = "change-this-to-a-random-secret-key"

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "app.db")
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ========== DB helpers ==========

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
    db.executescript(
        """
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
            customLabel TEXT,
            customUrl TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """
    )
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


# ========== Utils ==========

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_profile_for_user(user_id: int):
    db = get_db()
    row = db.execute(
        "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
    ).fetchone()
    return dict(row) if row else None


def save_profile_for_user(user_id: int, data: dict):
    db = get_db()
    existing = get_profile_for_user(user_id)
    if existing:
        db.execute(
            """
            UPDATE profiles
            SET name = ?, bio = ?, avatar = ?, instagram = ?, twitter = ?,
                youtube = ?, linkedin = ?, github = ?, customLabel = ?, customUrl = ?
            WHERE user_id = ?
            """,
            (
                data.get("name"),
                data.get("bio"),
                data.get("avatar"),
                data.get("instagram"),
                data.get("twitter"),
                data.get("youtube"),
                data.get("linkedin"),
                data.get("github"),
                data.get("customLabel"),
                data.get("customUrl"),
                user_id,
            ),
        )
    else:
        db.execute(
            """
            INSERT INTO profiles (
                user_id, name, bio, avatar, instagram, twitter,
                youtube, linkedin, github, customLabel, customUrl
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                data.get("name"),
                data.get("bio"),
                data.get("avatar"),
                data.get("instagram"),
                data.get("twitter"),
                data.get("youtube"),
                data.get("linkedin"),
                data.get("github"),
                data.get("customLabel"),
                data.get("customUrl"),
            ),
        )
    db.commit()


# ========== Auth routes ==========

@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        error = None

        if not username or not password:
            error = "Username and password are required."
        elif password != confirm:
            error = "Passwords do not match."

        if error is None:
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
                error = "Username already taken. Try another one."

        flash(error, "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        error = None
        if user is None:
            error = "No account with that username."
        elif not check_password_hash(user["password_hash"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            flash("Signed in successfully.", "success")
            return redirect(url_for("index"))

        flash(error, "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


# ========== Profile dashboard ==========

@app.route("/", methods=["GET", "POST"])
def index():
    if not g.user:
        return redirect(url_for("login"))

    user_id = g.user["id"]
    error = None
    profile = get_profile_for_user(user_id)

    if request.method == "POST":
        try:
            # start with existing avatar (if any)
            avatar_path = profile["avatar"] if profile and profile.get("avatar") else ""

            file = request.files.get("avatar")
            if file and file.filename and allowed_file(file.filename):
                # generate a completely unique filename every time
                ext = file.filename.rsplit(".", 1)[1].lower()
                filename = f"user{user_id}_{uuid4().hex}.{ext}"
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)
                avatar_path = f"uploads/{filename}"
                print("🖼 Saved new avatar:", avatar_path)

            profile_data = {
                "name": request.form.get("name", "").strip(),
                "bio": request.form.get("bio", "").strip(),
                "avatar": avatar_path,
                "instagram": request.form.get("instagram", "").strip(),
                "twitter": request.form.get("twitter", "").strip(),
                "youtube": request.form.get("youtube", "").strip(),
                "linkedin": request.form.get("linkedin", "").strip(),
                "github": request.form.get("github", "").strip(),
                "customLabel": request.form.get("customLabel", "").strip(),
                "customUrl": request.form.get("customUrl", "").strip(),
            }

            save_profile_for_user(user_id, profile_data)
            flash("Profile saved ✨", "success")
            return redirect(url_for("index"))
        except Exception as e:
            error = f"Something went wrong while saving: {e}"
            flash(error, "error")
            print("❌ Error while saving profile:", e)

    profile = get_profile_for_user(user_id)
    return render_template("index.html", profile=profile or {})


# ========== Public profile view ==========

@app.route("/u/<username>")
def public_profile(username):
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    if not user:
        return render_template("public_profile.html", profile=None, username=username)

    row = db.execute(
        "SELECT * FROM profiles WHERE user_id = ?", (user["id"],)
    ).fetchone()
    profile = dict(row) if row else None

    return render_template("public_profile.html", profile=profile, username=username)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

