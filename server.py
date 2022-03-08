from flask import Flask,render_template,url_for,redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = "Don't Care"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user-data-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

username = ""

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    tot_tickets = db.Column(db.Integer, nullable = False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable = False)
    tickets_tot = db.Column(db.Integer, nullable = False)

class Tickets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    no_of_tickets = db.Column(db.Integer, nullable = False)

db.create_all()

@app.route("/")
def home():
    return redirect(url_for('login'))


@app.route("/login",methods=["POST","GET"])
def login():
    global username
    if not current_user.is_authenticated:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username = username).first()
            if user:
                if password == user.password:
                    login_user(user)
                    return redirect(url_for('user_page'))
                return redirect(url_for('login'))
            return redirect(url_for('login'))
        return render_template("login.html")
    return redirect(url_for('user_page'))

@app.route("/register", methods=["POST","GET"])
def register():
    global username
    if not current_user.is_authenticated:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username = username).first()
            if not user:
                new_user = User(username = username,password=  password,tickets_tot = 0)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('user_page'))
            return redirect(url_for('register'))
        return render_template("register.html")
    return redirect(url_for('user_page'))

@app.route("/user-page")
def user_page():
    global username
    if current_user.is_authenticated:
        user = User.query.filter_by(username = username).first()
        return render_template("user.html",user = user)
    return redirect(url_for('login'))

@app.route("/admin-page")
def admin_page():
    persons = Tickets.query.all()
    return render_template("admin.html", persons = persons)

@app.route("/logout")
def logout_page():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route("/ticket",methods = ["POST"])
def ticket_book():
    if request.method == "POST":
        user = User.query.filter_by(username = username).first()
        user.tickets_tot = 1
        db.session.commit()
        new_user = Tickets(username=username,no_of_tickets=1)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_page'))

if __name__ == "__main__":
    app.run(debug=True)