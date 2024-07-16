from functools import wraps
from flask import Flask, abort, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager
from flask_login import login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import requests
import random
# ---------------------------------------------------------------------------------------------------------------------
app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# ---------------------------------------------------------------------------------------------------------------------

# models


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')


class Todo(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    done = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='todos')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)

# ---------------------------------------------------------------------------------------------------------------------
# forms
class TaskForm(FlaskForm):
    name = StringField('Task Name', validators=[InputRequired()])
    user_id = SelectField('Assign to User', coerce=int)
    submit = SubmitField('Add Task')


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


class ProjectForm(FlaskForm):
    id = StringField('Project ID')
    name = StringField('Project Name', validators=[InputRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[InputRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[InputRequired()])
    status = SelectField('Status', choices=[('not started', 'Not Started'), ('in progress', 'In Progress'), ('completed', 'Completed')], validators=[InputRequired()])
    submit = SubmitField('Add Project')
    update = SubmitField('Update Project')


class UserForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)])
    submit = SubmitField('Add User')
# ---------------------------------------------------------------------------------------------------------------------


@app.route('/')
@login_required
def home():
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    register_form = RegisterForm()

    if login_form.validate_on_submit() and 'login_submit' in request.form:
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))

    if register_form.validate_on_submit() and 'register_submit' in request.form:
        hashed_password = bcrypt.generate_password_hash(register_form.password.data)
        new_user = User(username=register_form.username.data, password=hashed_password, role='user')
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('login.html', login_form=login_form, register_form=register_form, pagetitle="Login | TaskQuest")


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role == 'admin':
        todo_list = Todo.query.all()
    else:
        todo_list = Todo.query.filter_by(user_id=current_user.id).all()
    
    projects = Project.query.all()
    return render_template('dashboard.html', pagetitle="Home | TaskQuest", todo_list=todo_list, projects=projects)



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    form = ProjectForm()
    if form.validate_on_submit():
        new_project = Project(
            name=form.name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('projects'))

    projects = Project.query.all()
    return render_template('Projects.html', form=form, projects=projects, pagetitle="Projects | TaskQuest")


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if current_user.role == 'admin':
        todo_list = Todo.query.all()
        users = User.query.all()
    else:
        todo_list = Todo.query.filter_by(user_id=current_user.id).all()
        users = None

    if request.method == 'POST':
        name = request.form['name']
        if current_user.role == 'admin':
            user_id = request.form['user_id']
        else:
            user_id = current_user.id

        new_task = Todo(name=name, done=False, user_id=user_id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('tasks'))

    return render_template("Tasks.html", todo_list=todo_list, users=users, pagetitle="Tasks | TaskQuest")



def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return func(*args, **kwargs)
    return decorated_function


@app.route('/users', methods=['GET', 'POST'])
@admin_required
@login_required
def users():
    form = UserForm()
    users = User.query.all()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('users'))

    return render_template('users.html', users=users, form=form, pagetitle="Users | TaskQuest")


@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('users'))


@app.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get("name")
    new_task = Todo(name=name, done=False, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("tasks"))

@app.route('/update/<int:todo_id>')
@login_required
def update(todo_id):
    todo = Todo.query.get(todo_id)
    if todo and (current_user.role == 'admin' or todo.user_id == current_user.id):
        todo.done = not todo.done
        db.session.commit()
    return redirect(url_for("tasks"))

@app.route('/delete/<int:todo_id>')
@login_required
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    if todo and (current_user.role == 'admin' or todo.user_id == current_user.id):
        db.session.delete(todo)
        db.session.commit()
    return redirect(url_for("tasks"))



def get_motivational_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        response.raise_for_status()
        quotes = response.json()
        if quotes:
            quote = quotes[0]
            return quote.get('q', 'Stay positive, work hard, make it happen.'), quote.get('a', 'Unknown')
        else:
            return "Stay positive, work hard, make it happen.", "Unknown"
    except requests.RequestException as e:
        print(f"Error fetching quote: {e}")
        return "Could not fetch quote", "Unknown"


@app.route('/quotes')
def quote():
    quote, author = get_motivational_quote()
    print(f"Fetched quote: {quote} - {author}")
    return render_template('quotes.html', pagetitle="Quotes | TaskQuest", quote=quote, author=author)


@app.route('/update_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def update_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return redirect(url_for('projects'))

    form = ProjectForm()

    if form.validate_on_submit() and form.update.data:
        project.name = form.name.data
        project.start_date = form.start_date.data
        project.end_date = form.end_date.data
        project.status = form.status.data
        db.session.commit()
        return redirect(url_for('projects'))

    form.id.data = project.id
    form.name.data = project.name
    form.start_date.data = project.start_date
    form.end_date.data = project.end_date
    form.status.data = project.status

    return render_template('update_project.html', form=form)


@app.route('/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get(project_id)
    if project:
        db.session.delete(project)
        db.session.commit()
    return redirect(url_for('projects'))


@app.route('/news')
@login_required
def news():
    api_key = 'fd60fc16b3404f539deec589b99e022b'
    url = f'https://newsapi.org/v2/everything?q=technology+programming&apiKey={api_key}'
    response = requests.get(url)

    if response.status_code == 200:
        articles = response.json().get('articles', [])
    else:
        articles = []

    return render_template('news.html', articles=articles, pagetitle="News | TaskQuest")

@app.route('/update_task/<int:todo_id>', methods=['POST'])
@login_required
@admin_required
def update_task(todo_id):
    task = Todo.query.get(todo_id)
    if task:
        task.name = request.form['name']
        task.user_id = request.form['user_id']
        db.session.commit()
    return redirect(url_for('tasks'))
# ---------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)
