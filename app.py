from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_connection
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        phone = request.form["phone"]

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing = cursor.fetchone()

        if existing:

            flash("Email already registered")

            cursor.close()
            conn.close()

            return redirect(url_for("register"))

        cursor.execute(
            """
            INSERT INTO users(fullname,email,password,phone)
            VALUES(%s,%s,%s,%s)
            """,
            (
                fullname,
                email,
                password,
                phone
            )
        )

        cursor.close()
        conn.close()

        flash("Registration Successful")

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["fullname"] = user["fullname"]

            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        fullname=session["fullname"]
    )

@app.route("/pets")
def pets():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM pets
        WHERE user_id=%s
        ORDER BY id DESC
        """,
        (session["user_id"],)
    )

    pet_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "pets.html",
        pets=pet_list
    )

@app.route("/add_pet", methods=["GET", "POST"])
def add_pet():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        pet_name = request.form["pet_name"]
        species = request.form["species"]
        breed = request.form["breed"]
        age = request.form["age"]
        weight = request.form["weight"]
        medical_notes = request.form["medical_notes"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO pets
            (
                user_id,
                pet_name,
                species,
                breed,
                age,
                weight,
                medical_notes
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                session["user_id"],
                pet_name,
                species,
                breed,
                age,
                weight,
                medical_notes
            )
        )

        cursor.close()
        conn.close()

        flash("Pet Added Successfully")

        return redirect(url_for("pets"))

    return render_template("add_pet.html")

@app.route("/edit_pet/<int:pet_id>", methods=["GET", "POST"])
def edit_pet(pet_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        pet_name = request.form["pet_name"]
        species = request.form["species"]
        breed = request.form["breed"]
        age = request.form["age"]
        weight = request.form["weight"]
        medical_notes = request.form["medical_notes"]

        cursor.execute(
            """
            UPDATE pets
            SET
                pet_name=%s,
                species=%s,
                breed=%s,
                age=%s,
                weight=%s,
                medical_notes=%s
            WHERE id=%s
            AND user_id=%s
            """,
            (
                pet_name,
                species,
                breed,
                age,
                weight,
                medical_notes,
                pet_id,
                session["user_id"]
            )
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash("Pet updated successfully.")
        return redirect(url_for("pets"))

    cursor.execute(
        """
        SELECT *
        FROM pets
        WHERE id=%s
        AND user_id=%s
        """,
        (pet_id, session["user_id"])
    )

    pet = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit_pet.html", pet=pet)

@app.route("/delete_pet/<int:pet_id>")
def delete_pet(pet_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM pets
        WHERE id=%s
        AND user_id=%s
        """,
        (pet_id, session["user_id"])
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Pet deleted successfully.")

    return redirect(url_for("pets"))

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


@app.route("/health")
def health():

    return {
        "status": "running"
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

@app.route("/test")
def test():
    return {
        "host": Config.DB_HOST,
        "database": Config.DB_NAME,
        "region": Config.AWS_REGION
    }