from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from datetime import date

app = Flask(__name__)
app.secret_key = "change-this-demo-secret"

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",  # Change this to your MySQL password
        database="blood_bank_db"
    )

def query_db(sql, params=(), fetch=False, commit=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        result = cursor.fetchall() if fetch else None
        if commit:
            conn.commit()
        return result
    finally:
        cursor.close()
        conn.close()

@app.route("/")
def dashboard():
    stats = {
        "donors": query_db("SELECT COUNT(*) AS n FROM donors", fetch=True)[0]["n"],
        "donations": query_db("SELECT COUNT(*) AS n FROM donations", fetch=True)[0]["n"],
        "requests": query_db("SELECT COUNT(*) AS n FROM blood_requests WHERE status='Pending'", fetch=True)[0]["n"],
        "units": query_db("SELECT COALESCE(SUM(units_available),0) AS n FROM blood_stock", fetch=True)[0]["n"]
    }
    stock = query_db("SELECT blood_group, units_available FROM blood_stock ORDER BY blood_group", fetch=True)
    recent = query_db("""
        SELECT d.donation_date, d.units, donors.full_name, donors.blood_group
        FROM donations d JOIN donors ON donors.donor_id=d.donor_id
        ORDER BY d.donation_date DESC, d.donation_id DESC LIMIT 5
    """, fetch=True)
    return render_template("dashboard.html", stats=stats, stock=stock, recent=recent)

@app.route("/donors")
def donors():
    rows = query_db("SELECT * FROM donors ORDER BY donor_id DESC", fetch=True)
    return render_template("donors.html", donors=rows)

@app.route("/donors/add", methods=["GET", "POST"])
def add_donor():
    if request.method == "POST":
        data = (
            request.form["full_name"].strip(), request.form["age"], request.form["gender"],
            request.form["blood_group"], request.form["phone"].strip(),
            request.form["city"].strip(), request.form.get("email", "").strip()
        )
        try:
            query_db("""INSERT INTO donors
                (full_name, age, gender, blood_group, phone, city, email)
                VALUES (%s,%s,%s,%s,%s,%s,%s)""", data, commit=True)
            flash("Donor registered successfully.", "success")
            return redirect(url_for("donors"))
        except Error as e:
            flash(f"Could not save donor. Check that the phone number is not already registered. Details: {e}", "error")
    return render_template("donor_form.html")

@app.route("/donors/<int:donor_id>/delete", methods=["POST"])
def delete_donor(donor_id):
    try:
        query_db("DELETE FROM donors WHERE donor_id=%s", (donor_id,), commit=True)
        flash("Donor deleted.", "success")
    except Error:
        flash("This donor has donation records and cannot be deleted. Keep the history or remove related demo records first.", "error")
    return redirect(url_for("donors"))

@app.route("/donations", methods=["GET", "POST"])
def donations():
    if request.method == "POST":
        donor_id = request.form["donor_id"]
        units = int(request.form["units"])
        donation_date = request.form["donation_date"]
        try:
            # Update donation history and stock together in one transaction.
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT blood_group FROM donors WHERE donor_id=%s", (donor_id,))
            donor = cur.fetchone()
            if not donor:
                raise ValueError("Choose a valid donor.")
            cur.execute("INSERT INTO donations (donor_id, donation_date, units) VALUES (%s,%s,%s)",
                        (donor_id, donation_date, units))
            cur.execute("""UPDATE blood_stock SET units_available=units_available+%s
                           WHERE blood_group=%s""", (units, donor["blood_group"]))
            conn.commit()
            cur.close()
            conn.close()
            flash("Donation recorded and stock updated.", "success")
            return redirect(url_for("donations"))
        except Exception as e:
            try:
                conn.rollback()
                cur.close()
                conn.close()
            except Exception:
                pass
            flash(f"Could not record donation: {e}", "error")
    donor_rows = query_db("SELECT donor_id, full_name, blood_group FROM donors ORDER BY full_name", fetch=True)
    rows = query_db("""SELECT d.donation_id, d.donation_date, d.units, donors.full_name, donors.blood_group
                       FROM donations d JOIN donors ON donors.donor_id=d.donor_id
                       ORDER BY d.donation_date DESC, d.donation_id DESC""", fetch=True)
    return render_template("donations.html", donors=donor_rows, donations=rows, today=date.today().isoformat())

@app.route("/requests", methods=["GET", "POST"])
def requests_page():
    if request.method == "POST":
        data = (
            request.form["requester_name"].strip(), request.form["contact_phone"].strip(),
            request.form["blood_group"], int(request.form["units_needed"]),
            request.form.get("hospital", "").strip(), request.form.get("notes", "").strip()
        )
        query_db("""INSERT INTO blood_requests
            (requester_name, contact_phone, blood_group, units_needed, hospital, notes)
            VALUES (%s,%s,%s,%s,%s,%s)""", data, commit=True)
        flash("Blood request submitted.", "success")
        return redirect(url_for("requests_page"))
    rows = query_db("SELECT * FROM blood_requests ORDER BY request_id DESC", fetch=True)
    return render_template("requests.html", requests=rows)

@app.route("/requests/<int:request_id>/status", methods=["POST"])
def update_request_status(request_id):
    status = request.form["status"]
    if status not in ("Pending", "Approved", "Fulfilled", "Rejected"):
        flash("Invalid status.", "error")
    else:
        query_db("UPDATE blood_requests SET status=%s WHERE request_id=%s", (status, request_id), commit=True)
        flash("Request status updated.", "success")
    return redirect(url_for("requests_page"))

@app.route("/stock")
def stock_page():
    rows = query_db("SELECT * FROM blood_stock ORDER BY blood_group", fetch=True)
    return render_template("stock.html", stock=rows)

if __name__ == "__main__":
    app.run(debug=True)
