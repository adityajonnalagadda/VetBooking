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

@app.route("/book_appointment", methods=["GET", "POST"])
def book_appointment():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        pet_id = request.form["pet_id"]
        vet_id = request.form["vet_id"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]
        service_type = request.form["service_type"]
        address = request.form["address"]
        notes = request.form["notes"]

        cursor.execute(
            """
            INSERT INTO appointments
            (
                user_id,
                pet_id,
                vet_id,
                appointment_date,
                appointment_time,
                service_type,
                address,
                notes
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                session["user_id"],
                pet_id,
                vet_id,
                appointment_date,
                appointment_time,
                service_type,
                address,
                notes
            )
        )

        conn.commit()

        flash("Appointment booked successfully.")

        cursor.close()
        conn.close()

        return redirect(url_for("appointments"))

    cursor.execute(
        """
        SELECT *
        FROM pets
        WHERE user_id=%s
        """,
        (session["user_id"],)
    )

    pets = cursor.fetchall()

    cursor.execute(
        """
        SELECT *
        FROM veterinarians
        ORDER BY fullname
        """
    )

    vets = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "book_appointment.html",
        pets=pets,
        vets=vets
    )

@app.route("/appointments")
def appointments():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            appointments.id,
            pets.pet_name,
            veterinarians.fullname,
            appointment_date,
            appointment_time,
            service_type,
            status
        FROM appointments
        JOIN pets
            ON appointments.pet_id = pets.id
        LEFT JOIN veterinarians
            ON appointments.vet_id = veterinarians.id
        WHERE appointments.user_id = %s
        ORDER BY appointment_date DESC,
                 appointment_time DESC
        """,
        (session["user_id"],)
    )

    appointments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "appointments.html",
        appointments=appointments
    )

@app.route("/cancel_appointment/<int:id>")
def cancel_appointment(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE appointments
        SET status='Cancelled'
        WHERE id=%s
        AND user_id=%s
        AND status='Pending'
        """,
        (
            id,
            session["user_id"]
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Appointment cancelled successfully.")

    return redirect(url_for("appointments"))

@app.route("/vet_dashboard")
def vet_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            appointments.id,
            pets.pet_name,
            users.fullname AS owner_name,
            veterinarians.fullname AS vet_name,
            appointment_date,
            appointment_time,
            service_type,
            status,
            notes
        FROM appointments
        JOIN pets
            ON appointments.pet_id = pets.id
        JOIN users
            ON appointments.user_id = users.id
        LEFT JOIN veterinarians
            ON appointments.vet_id = veterinarians.id
        ORDER BY appointment_date, appointment_time
    """)

    appointments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "vet_dashboard.html",
        appointments=appointments
    )

@app.route("/confirm_appointment/<int:id>")
def confirm_appointment(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE appointments
        SET status='Confirmed'
        WHERE id=%s
    """, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    flash("Appointment confirmed.")

    return redirect(url_for("vet_dashboard"))

@app.route("/complete_appointment/<int:id>")
def complete_appointment(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE appointments
        SET status='Completed'
        WHERE id=%s
    """, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    flash("Appointment completed.")

    return redirect(url_for("vet_dashboard"))

@app.route("/payment/<int:appointment_id>", methods=["GET", "POST"])
def payment(appointment_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            appointments.id,
            pets.pet_name,
            service_type
        FROM appointments
        JOIN pets
            ON appointments.pet_id = pets.id
        WHERE appointments.id=%s
    """, (appointment_id,))

    appointment = cursor.fetchone()

    amount = 500

    if request.method == "POST":

        payment_method = request.form["payment_method"]

        cursor.execute("""
            INSERT INTO payments
            (
                appointment_id,
                amount,
                payment_status,
                payment_method
            )
            VALUES
            (%s,%s,'Paid',%s)
        """,
        (
            appointment_id,
            amount,
            payment_method
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            url_for(
                "receipt",
                payment_id=appointment_id
            )
        )

    cursor.close()
    conn.close()

    return render_template(
        "payment.html",
        appointment=appointment,
        amount=amount
    )

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