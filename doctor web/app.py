import sqlite3
import asyncio
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_socketio import SocketIO
from datetime import datetime

# Initialisation
app = Flask(__name__)
app.debug = True
app.secret_key = "supersecretkey"
socketio = SocketIO(app)

# Fonctions utilitaires
def init_db():
    """Initialise la base de données SQLite."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            specialty TEXT
        )
    ''')

    # Table des disponibilités
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS availabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

async def async_query(db_path, query, params=()):
    """Exécute une requête SQLite de manière asynchrone."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: execute_query(db_path, query, params)
    )

def execute_query(db_path, query, params):
    """Fonction synchrone pour exécuter une requête SQLite."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Exécution de la requête : {query}, Paramètres : {params}")
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
        print("Résultat de la requête :", result)
        return result
    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête SQL : {e}")
    finally:
        conn.close()


def is_valid_availability(date):
    """Vérifie si une date est dans le futur."""
    from datetime import datetime
    try:
        # Vérifiez avec le format attendu par SQLite
        availability_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        return availability_date > datetime.now()
    except ValueError as e:
        print(f"Erreur de validation de la date : {e}")
        return False



async def simulate_long_task(task_name):
    """Simule une tâche longue avec asyncio."""
    print(f"Début de la tâche {task_name}...")
    await asyncio.sleep(5)
    print(f"Tâche {task_name} terminée.")
    return f"Résultat de {task_name}"

# Routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
async def register():
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        specialty = request.form.get('specialty', None)

        query = '''
            INSERT INTO users (first_name, last_name, email, password, role, specialty)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        try:
            await async_query('database.db', query, (first_name, last_name, email, password, role, specialty))
            flash("Inscription réussie !", "success")
            # Redirection vers le profil
            return redirect(url_for("doctor_dashboard" if role == "doctor" else "patient_dashboard"))
        except Exception as e:
            flash(f"Erreur lors de l'inscription : {e}", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
async def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        # Exécuter la requête avec await
        query = 'SELECT * FROM users WHERE email = ? AND password = ?'
        user = await async_query('database.db', query, (email, password))
        
        if user:  # Vérifier si l'utilisateur existe
            user = user[0]  # Obtenir la première ligne du résultat
            flash("Connexion réussie!", "success")
            session['user_id'] = user[0]  # Stocker l'ID de l'utilisateur dans la session
            return redirect(url_for("doctor_dashboard" if user[4] == "doctor" else "patient_dashboard"))
        else:
            flash("Identifiants incorrects.", "danger")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    # Supprime l'utilisateur de la session
    session.pop('user_id', None)
    flash("Déconnexion réussie !", "success")
    return redirect(url_for("login"))


@app.route("/doctor", methods=["GET", "POST"])
async def doctor_dashboard():
    # Vérifiez que l'utilisateur est connecté
    user_id = session.get('user_id')
    print(f"ID utilisateur connecté (session): {user_id}")
    if user_id is None:
        return redirect(url_for("login"))

    # Vérifiez que l'utilisateur existe
    query = 'SELECT * FROM users WHERE id = ?'
    user = await async_query('database.db', query, (user_id,))
    if not user:
        print(f"Utilisateur introuvable pour ID: {user_id}")
        flash("Erreur : utilisateur non trouvé.", "danger")
        return redirect(url_for("doctor_dashboard"))

    if request.method == "POST":
        doctor_id = user_id
        date = request.form['date']  # Récupérez la date brute

        print(f"Données reçues du formulaire - Doctor ID: {doctor_id}, Date brute: {date}")

        # Normalisez la date
        try:
            # Remplacez 'T' par un espace et ajoutez les secondes pour SQLite
            date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M")
            date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            print(f"Date formatée pour SQLite : {date}")
        except ValueError as e:
            print(f"Erreur de formatage de la date : {e}")
            flash("Format de date invalide.", "danger")
            return redirect(url_for("doctor_dashboard"))

        # Vérifiez si la date est valide
        if not is_valid_availability(date):
            flash("Date invalide ou passée.", "danger")
            return redirect(url_for("doctor_dashboard"))

        # Insérez la disponibilité
        try:
            query = 'INSERT INTO availabilities (doctor_id, date) VALUES (?, ?)'
            await async_query('database.db', query, (doctor_id, date))
            flash("Disponibilité ajoutée avec succès !", "success")
        except Exception as e:
            print(f"Erreur lors de l'ajout de la disponibilité : {e}")
            flash(f"Erreur lors de l'ajout : {e}", "danger")

    # Récupérez les disponibilités pour cet utilisateur
    query = 'SELECT * FROM availabilities WHERE doctor_id = ?'
    availabilities = await async_query('database.db', query, (user_id,))
    print(f"Disponibilités récupérées : {availabilities}")
    return render_template("doctor_dashboard.html", availabilities=availabilities)


@app.route("/doctor/edit/<int:availability_id>", methods=["GET", "POST"])
async def edit_availability(availability_id):
    # Vérification de session
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for("login"))

    # Récupérer la disponibilité existante
    query = 'SELECT * FROM availabilities WHERE id = ?'
    availability = await async_query('database.db', query, (availability_id,))
    if not availability:
        flash("Disponibilité non trouvée.", "danger")
        return redirect(url_for("doctor_dashboard"))

    if request.method == "POST":
        new_date = request.form['date']
        try:
            # Normaliser la date
            new_date_obj = datetime.strptime(new_date, "%Y-%m-%dT%H:%M")
            new_date = new_date_obj.strftime("%Y-%m-%d %H:%M:%S")

            if not is_valid_availability(new_date):
                flash("Date invalide ou passée.", "danger")
                return redirect(url_for("doctor_dashboard"))

            # Mettre à jour la disponibilité
            update_query = 'UPDATE availabilities SET date = ? WHERE id = ?'
            await async_query('database.db', update_query, (new_date, availability_id))
            flash("Disponibilité mise à jour avec succès !", "success")
        except Exception as e:
            flash(f"Erreur lors de la mise à jour : {e}", "danger")
        return redirect(url_for("doctor_dashboard"))

    return render_template("edit_availability.html", availability=availability[0])


@app.route("/doctor/delete/<int:availability_id>", methods=["POST"])
async def delete_availability(availability_id):
    # Vérification de session
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for("login"))

    try:
        delete_query = 'DELETE FROM availabilities WHERE id = ?'
        await async_query('database.db', delete_query, (availability_id,))
        flash("Disponibilité supprimée avec succès !", "success")
    except Exception as e:
        flash(f"Erreur lors de la suppression : {e}", "danger")

    return redirect(url_for("doctor_dashboard"))


# @app.route("/doctor/test-insert")
# async def test_insert():
#     doctor_id = 1  # ID d'un utilisateur existant
#     date = "2024-12-20 00:10:00"  # Date valide

#     try:
#         query = 'INSERT INTO availabilities (doctor_id, date) VALUES (?, ?)'
#         await async_query('database.db', query, (doctor_id, date))
#         return "Insertion réussie", 200
#     except Exception as e:
#         print(f"Erreur lors de l'insertion test : {e}")
#         return f"Erreur : {e}", 500


@app.route("/patient")
async def patient_dashboard():
    query = '''
        SELECT availabilities.date, users.first_name, users.last_name, users.specialty
        FROM availabilities
        JOIN users ON availabilities.doctor_id = users.id
    '''
    availabilities = await async_query('database.db', query)
    return render_template("patient_dashboard.html", availabilities=availabilities)

async def notify_clients():
    """Notifie les clients sans bloquer l'application."""
    await asyncio.sleep(1)
    socketio.emit('background_notification', {'message': "Nouvelle disponibilité ajoutée"})

if __name__ == "__main__":
    init_db()
    socketio.run(app, debug=True)
