from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

local_server = True

# create the app
app = Flask(__name__)
app.secret_key = os.getenv(b"SECRECT_KEY")

# User Session
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize the app with the extension
db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    if session.get("user_type") == "agent":
        return SupportAgents.query.get(int(user_id))
    return Customers.query.get(int(user_id))


# Models
class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))


class Customers(UserMixin, db.Model):
    __tablename__ = 'customers'
    cust_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(31), nullable=False)
    email = db.Column(db.String(31), unique=True, nullable=False)
    username = db.Column(db.String(31), unique=True, nullable=False)
    password = db.Column(db.String(1023), nullable=False)

    def get_id(self):
        return self.cust_id


class SupportAgents(UserMixin, db.Model):
    __tablename__ = 'supportagents'
    agent_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(31), nullable=False)
    email = db.Column(db.String(31), unique=True, nullable=False)
    password = db.Column(db.String(1023), nullable=False)
    is_manager = db.Column(db.Boolean, default=False) 

    def get_id(self):
        return self.agent_id


class SupportCases(db.Model):
    __tablename__ = 'supportcases'
    case_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    issueDescription = db.Column(db.String(1023), nullable=False)
    priority = db.Column(db.String(7), nullable=False)
    status = db.Column(db.String(15), default='Open')
    datesubmitted = db.Column(db.DateTime, default=datetime.utcnow)
    dateresolved = db.Column(db.DateTime, default=None)

    # Link case to a user
    user_id = db.Column(db.Integer, db.ForeignKey('customers.cust_id'), nullable=False)
    user = db.relationship('Customers', backref='cases')

    # Link case to an agent
    agent_id = db.Column(db.Integer, db.ForeignKey('supportagents.agent_id'), nullable=True)
    agent = db.relationship('SupportAgents', backref='assigned_cases')


# Routes
@app.route('/test')
def test():
    try:
        query = Test.query.all()
        return "Db connected :)"
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def home():
    if 'username' in session:
        return render_template('user_dashboard.html', username=session['username'])
    return render_template("home.html", username='to Support App')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords don't match", "danger")
            return redirect(url_for('signup'))

        user_email = Customers.query.filter_by(email=email.lower()).first()
        if user_email:
            flash("Email already registered", "warning")
            return redirect(url_for("signup"))
        
        user_username = Customers.query.filter_by(username=username.lower()).first()
        if user_username:
            flash("Username already taken", "warning")
            return redirect(url_for("signup"))

        gen_pass = generate_password_hash(password)

        try:
            query = Customers(fullname=fullname, email=email.lower(), username=username.lower(), password=gen_pass)
            db.session.add(query)
            db.session.commit()
            flash("Signup Successful!!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return f"Error occurred: {e}"

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Customers.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['username'] = user.username
            session['user_type'] = 'customer'
            flash("Login Successful!!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logout success", "primary")
    return redirect(url_for('home'))

@app.route('/lodge-case', methods=['GET', 'POST'])
@login_required
def lodge_case():
    if request.method == 'POST':
        issueDescription = request.form.get('issue_description')
        priority = request.form.get('priority')
        datesubmitted_str = request.form.get('date_of_submission')

        try:
            datesubmitted = datetime.strptime(datesubmitted_str, '%Y-%m-%d')

            query = SupportCases(
                issueDescription=issueDescription, 
                priority=priority, 
                user_id=current_user.cust_id
                )

            db.session.add(query)
            db.session.commit()
            flash("Case Submitted!!", "info")
            return redirect(url_for('home'))

        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('lodge_case'))
        except Exception as e:
            db.session.rollback()
            return f"Error occurred: {e}"

    return render_template('lodge-case.html')

@app.route('/my-cases', methods=['GET'])
@login_required
def my_cases():
    cases = SupportCases.query.filter_by(user_id=current_user.cust_id).all()
    return render_template('my-cases.html', cases=cases)

@app.route('/agent-signup', methods=['GET', 'POST'])
def agent_signup():
    if request.method == 'POST':
        fullname = request.form.get('agent_name')
        email = request.form.get('agent_email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords don't match", "danger")
            return redirect(url_for('agent_signup'))

        user_email = SupportAgents.query.filter_by(email=email).first()
        if user_email:
            flash("Email already registered", "warning")
            return redirect(url_for("agent_signup"))
    
        gen_pass = generate_password_hash(password)

        try:
            query = SupportAgents(fullname=fullname, email=email, password=gen_pass)
            db.session.add(query)
            db.session.commit()
            flash("Signup Successful!!", "success")
            return redirect(url_for('agent_login'))
        except Exception as e:
            db.session.rollback()
            return f"Error occurred: {e}"

    return render_template('agent-signup.html')

@app.route('/agent-login', methods=['GET', 'POST'])
def agent_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = SupportAgents.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['fullname'] = user.fullname
            session['user_type'] = 'agent'
            if user.is_manager:
                flash("Manager login successful!", "success")
                return redirect(url_for('manager_dashboard'))
            else:
                flash("Login Successful!!", "success")
                return redirect(url_for('agent_dashboard'))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for('agent_login'))

    return render_template('agent-login.html')

@app.route("/agent-dashboard")
@login_required
def agent_dashboard():
    if not isinstance(current_user, SupportAgents):
        flash("Unauthorized access", "danger")
        return redirect(url_for("home"))


    if session.get('user_type') != 'agent':
        flash("Unauthorized access", "danger")
        return redirect(url_for('home'))

    assigned_cases = SupportCases.query.filter_by(agent_id=current_user.agent_id).all()
    return render_template('agent_dashboard.html', agent_name=session['fullname'], assigned_cases=assigned_cases)

@app.route('/manager-dashboard')
@login_required
def manager_dashboard():
    if not isinstance(current_user, SupportAgents):
        flash("Unauthorized access", "danger")
        return redirect(url_for("home"))

    if session.get('user_type') != 'agent' or not current_user.is_manager:
        flash("Unauthorized access", "danger")
        return redirect(url_for('home'))

    agents = SupportAgents.query.filter_by(is_manager=False).all()
    all_cases = SupportCases.query.all()
    return render_template('manager_dashboard.html', manager_name = session['fullname'], all_cases = all_cases,
                           agents = agents) 

@app.route('/assign_case', methods=['POST'])
@login_required
def assign_case():
    case_id = request.form.get('case_id')
    agent_id = request.form.get('agent_id')

    case = SupportCases.query.filter_by(case_id=case_id).first()
    agent = SupportAgents.query.filter_by(agent_id=agent_id).first()

    if case and agent:
        case.agent_id = agent.agent_id
        case.status = "In Progress"  
        db.session.commit()
        flash(f"Case {case_id} assigned to {agent.fullname} and marked as 'In Progress'.", "success")
    else:
        flash("Failed to assign case. Please try again.", "danger")

    return redirect(url_for('manager_dashboard'))


@app.route("/update_status", methods=["POST"])
@login_required
def update_status():
    case_id = request.form.get("case_id")
    new_status = request.form.get("status")
    
    case = SupportCases.query.filter_by(case_id=case_id).first()
    if case and case.agent_id == current_user.agent_id:
        case.status = new_status
        db.session.commit()
        flash("Case status updated successfully.", "success")
    else:
        flash("Unauthorized or case not found.", "danger")
    
    return redirect(url_for("agent_dashboard"))

# Run
if __name__ == "__main__":
    app.run(debug=True)
