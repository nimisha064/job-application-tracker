from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            date_applied TEXT,
            status TEXT,
            job_url TEXT,
            notes TEXT,
            follow_up_date TEXT,
            priority TEXT
        )
    """)

    conn.commit()
    conn.close()


def migrate_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    columns = [
        ("job_url", "TEXT"),
        ("notes", "TEXT"),
        ("follow_up_date", "TEXT"),
        ("priority", "TEXT")
    ]

    for column, datatype in columns:
        try:
            cursor.execute(
                f"ALTER TABLE applications ADD COLUMN {column} {datatype}"
            )
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()


@app.route("/")
def home():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM applications
        ORDER BY id DESC
    """)

    applications = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM applications
        WHERE status = 'Applied'
    """)
    applied = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM applications
        WHERE status = 'Interview'
    """)
    interview = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM applications
        WHERE status = 'Selected'
    """)
    selected = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM applications
        WHERE status = 'Rejected'
    """)
    rejected = cursor.fetchone()[0]

    conn.close()

    if total > 0:
        interview_percentage = round((interview / total) * 100)
        selected_percentage = round((selected / total) * 100)
        rejected_percentage = round((rejected / total) * 100)
    else:
        interview_percentage = 0
        selected_percentage = 0
        rejected_percentage = 0

    return render_template(
        "index.html",
        applications=applications,
        total=total,
        applied=applied,
        interview=interview,
        selected=selected,
        rejected=rejected,
        interview_percentage=interview_percentage,
        selected_percentage=selected_percentage,
        rejected_percentage=rejected_percentage
    )


@app.route("/add", methods=["GET", "POST"])
def add_application():

    if request.method == "POST":

        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        date_applied = request.form["date_applied"]
        status = request.form["status"]
        job_url = request.form["job_url"]
        notes = request.form["notes"]
        follow_up_date = request.form["follow_up_date"]
        priority = request.form["priority"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO applications
            (
                company,
                role,
                location,
                date_applied,
                status,
                job_url,
                notes,
                follow_up_date,
                priority
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company,
            role,
            location,
            date_applied,
            status,
            job_url,
            notes,
            follow_up_date,
            priority
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_application(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        date_applied = request.form["date_applied"]
        status = request.form["status"]
        job_url = request.form["job_url"]
        notes = request.form["notes"]
        follow_up_date = request.form["follow_up_date"]
        priority = request.form["priority"]

        cursor.execute("""
            UPDATE applications
            SET
                company = ?,
                role = ?,
                location = ?,
                date_applied = ?,
                status = ?,
                job_url = ?,
                notes = ?,
                follow_up_date = ?,
                priority = ?
            WHERE id = ?
        """, (
            company,
            role,
            location,
            date_applied,
            status,
            job_url,
            notes,
            follow_up_date,
            priority,
            id
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM applications WHERE id = ?",
        (id,)
    )

    application = cursor.fetchone()

    conn.close()

    return render_template(
        "edit.html",
        application=application
    )


@app.route("/delete/<int:id>")
def delete_application(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM applications WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":

    init_db()
    migrate_db()

    app.run(debug=True)