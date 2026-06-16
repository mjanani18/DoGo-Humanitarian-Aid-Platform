from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "dogo_secret_key"


# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- HOME ----------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/behind_dogo')
def behind_dogo():
    return render_template('behind_dogo.html')


# ---------------- DONATION FORM ----------------
@app.route('/donate', methods=['GET', 'POST'])
def donate():

    if request.method == 'POST':

        name = request.form['name']
        donation_type = request.form['type']
        quantity = request.form['quantity']
        location = request.form['location']
        date = request.form['date']
        time = request.form['time']
        phone = request.form['phone']
        description = request.form['description']

        # NEW DONOR VERIFICATION FIELDS
        verification_type = request.form['verification_type']
        verification_number = request.form['verification_number']

        if (
            not name or
            not donation_type or
            not quantity or
            not location or
            not date or
            not time or
            not phone or
            not verification_type or
            not verification_number or
            not description
        ):
            return "All fields are mandatory"

        if int(quantity) < 10:
            return "Minimum donation quantity should be 10"

        status = "Pending"

        item = f"""
Donation Type: {donation_type}
Quantity: {quantity}

Verification Type: {verification_type}
Verification ID Number: {verification_number}

Address: {location}

Pickup Date: {date}
Pickup Time: {time}

Phone: {phone}

Description: {description}
"""

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

         
        c.execute("""
        INSERT INTO donations (
            name,
            item,
            status,
            proof_link
        )
        VALUES (?, ?, ?, ?)
        """, (
            name,
            item,
            status,
            ""
        ))

        donation_id = c.lastrowid

        conn.commit()
        conn.close()

        # MODERN SUCCESS PAGE
        return render_template(
    "success.html",
    phone=phone,
    donation_id=donation_id
)


    return render_template('donate.html')
# ---------------- NGO REGISTER ----------------
@app.route('/ngo_register', methods=['GET', 'POST'])
def ngo_register():

    if request.method == 'POST':
        
        person_name = request.form['person_name']
        ngo_name = request.form['ngo_name']
        password = request.form['password']
        ngo_id = request.form['ngo_id']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        verification_type = request.form['verification_type']
        verification_number = request.form['verification_number']

        if (
            not person_name or
            not ngo_name or
            not ngo_id or
            not email or
            not phone or
            not address or
            not verification_type or
            not verification_number or
            not password
           ):
            return "All fields are mandatory"

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        try:

            c.execute("""
            INSERT INTO ngo (
                person_name,      
                ngo_name,
                password,
                ngo_id,
                email,
                phone,
                address,
                verification_type,
                verification_number
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                person_name,
                ngo_name,
                password,
                ngo_id,
                email,
                phone,
                address,
                verification_type,
                verification_number
            ))

            conn.commit()
            conn.close()

            return """
            <h2 style='color:green;text-align:center;margin-top:50px;'>
            NGO Registered Successfully 🎉
            </h2>

            <p style='text-align:center;'>
            <a href='/ngo_login'>Go to Login</a>
            </p>
            """

        except sqlite3.IntegrityError:

            conn.close()

            return """
            <h2 style='color:red;text-align:center;margin-top:50px;'>
            NGO ID already exists ❌
            </h2>
            """

    return render_template('ngo_register.html')

# ---------------- NGO LOGIN ----------------
@app.route('/ngo_login', methods=['GET', 'POST'])
def ngo_login():

    if request.method == 'POST':

        ngo_id = request.form['ngo_id'].strip()
        password = request.form['password'].strip()

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute(
            "SELECT * FROM ngo WHERE ngo_id=? AND password=?",
            (ngo_id, password)
        )

        user = c.fetchone()

        print(user)

        conn.close()

        if user:

            session['ngo'] = True
            session['person_name'] = user[1]
            session['ngo_name'] = user[2]
            session['ngo_id'] = user[4]
            session['ngo_email'] = user[5]
            session['ngo_phone'] = user[6]

            return redirect('/dashboard')

        else:

            return """
            <h2 style='color:red;text-align:center;margin-top:50px;'>
            Invalid NGO ID or Password ❌
            </h2> 
            """

    return render_template('ngo_login.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():

    if not session.get('ngo'):
        return redirect('/ngo_login')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM donations")

    data = c.fetchall()

    conn.close()

    return render_template('dashboard.html', data=data)
# ---------------- UPDATE STATUS ----------------
@app.route('/update/<int:id>/<action>')
def update_status(id, action):

    if not session.get("ngo"):
        return redirect('/ngo_login')

    conn = get_db()
    c = conn.cursor()
    
    ngo_person_name = session.get("person_name")
    ngo_name = session.get("ngo_name")
    ngo_id = session.get("ngo_id")
    ngo_email = session.get("ngo_email")
    ngo_phone = session.get("ngo_phone")

    # ACCEPT
    if action == "accept":

        c.execute("""

        UPDATE donations

        SET

        status=?,
        ngo_person_name=?,
        ngo_name=?,
        ngo_id=?,
        ngo_email=?,
        ngo_phone=?

        WHERE id=?

        """,

        (
            "Accepted",
            ngo_person_name,
            ngo_name,
            ngo_id,
            ngo_email,
            ngo_phone,
            id
        ))

    # COMPLETE
    elif action == "complete":

        print("PERSON:", ngo_person_name)
        print("ORG:", ngo_name)
        print("ID:", ngo_id)
        print("EMAIL:", ngo_email)
        print("PHONE:", ngo_phone)

        c.execute("""

        UPDATE donations

        SET status=?

        WHERE id=?

        """,

        (
            "Completed",
            id
        ))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ---------------- ADD PROOF ----------------
@app.route('/add_proof/<int:id>', methods=['POST'])
def add_proof(id):

    if not session.get('ngo'):
        return redirect('/ngo_login')

    proof_link = request.form['proof_link']

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    UPDATE donations
    SET proof_link=?
    WHERE id=?
    """, (

        proof_link,
        id

    ))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ---------------- HISTORY ----------------
@app.route('/history')
def history():

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    SELECT * FROM donations
    """)

    data = c.fetchall()

    conn.close()

    return render_template('history.html', data=data)


# ---------------- TRACKING ----------------
@app.route('/track/<int:donation_id>')
def track(donation_id):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM donations
    WHERE id=?
    """, (donation_id,))

    data = c.fetchall()

    conn.close()

    return render_template('tracking.html', data=data)
   
   
@app.route('/track_search', methods=['GET', 'POST'])
def track_search():

    if request.method == 'POST':

        donation_id = request.form['donation_id']

        return redirect(f'/track/{donation_id}')

    return render_template('track_search.html')
# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/ngo_login')


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)