## SI 364

# export MAIL_USERNAME=margauxk364@gmail.com  MAIL_PASSWORD=si364homework

## Import statements
import os
from flask import request, Flask, render_template, session, redirect, url_for, flash, jsonify
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread
from werkzeug import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
import requests

# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364(thisisnotsupersecure)'
## Create a database in postgresql in the code line below, and fill in your app's database URI. It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME

## TODO: Create database and change the SQLAlchemy Database URI.
## Your Postgres database should be your uniqname, plus HW5, e.g. "jczettaHW5" or "maupandeHW5"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/margauxkFinal"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# TODO: Add configuration specifications so that email can be sent from this application, like the examples you saw in the textbook and in class. Make sure you've installed the correct library with pip! See textbook.
# NOTE: Make sure that you DO NOT write your actual email password in text!!!!
# NOTE: You will need to use a gmail account to follow the examples in the textbook, and you can create one of those for free, if you want. In THIS application, you should use the username and password from the environment variables, as directed in the textbook. So when WE run your app, we will be using OUR email, not yours.
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587 #default
app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USERNAME'] = 'margauxk364@gmail.com' # TODO export to your environs -- may want a new account just for this. It's expecting gmail, not umich
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
#app.config['MAIL_PASSWORD'] = 'si364homework'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT_PREFIX'] = '[Books App]'
app.config['MAIL_SENDER'] = 'Admin <{}>'.format(os.environ.get('MAIL_USERNAME')) # TODO fill in email
app.config['ADMIN'] = os.environ.get('MAIL_USERNAME')

# Set up Flask debug stuff
manager = Manager(app)
db = SQLAlchemy(app) # For database use
migrate = Migrate(app, db) # For database use/updating
manager.add_command('db', MigrateCommand) # Add migrate
mail = Mail(app) # For email sending
# TODO: Run commands to create your migrations folder and get ready to create a first migration, as shown in the textbook and in class.
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')

    #Additional checking methods for the form
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')



## Login routes
@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        new_read_list = List(user_id=user.id, type="read")
        new_to_read_list = List(user_id=user.id, type="toRead")
        db.session.add(new_read_list)
        db.session.add(new_to_read_list)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)
    


## DB load functions
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # returns User object or None
## Set up Shell context so it's easy to use the shell to debug
def make_shell_context():
    return dict(app=app, db=db, Tweet=Tweet, User=User, Hashtag=Hashtag)
# Add function use to manager
manager.add_command("shell", Shell(make_context=make_shell_context))

# TODO: Write a send_email function here. (As shown in examples.)
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs): # kwargs = 'keyword arguments', this syntax means to unpack any keyword arguments into the function in the invocation...
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg]) # using the async email to make sure the email sending doesn't take up all the "app energy" -- the main thread -- at once
    thr.start()
    return thr 

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    descr = db.Column(db.String)       

class List(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(80))      

class BookList(db.Model):
    __tablename__ = "book_list"
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(200), unique=True)    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

def books_for_search(searchTerm):
    r = requests.get("https://itunes.apple.com/search", params= {"entity" : "ebook", "term" : searchTerm}).json()["results"]
    for book in r:
        new_book = get_or_create_book(db.session, book["trackName"], book["description"])
    return r

def get_or_create_book(db_session, title, description):
    book = db_session.query(Book).filter_by(title=title).first()
    if book:
        return book
    else:
        book = Book(title=title, descr=description)
        db_session.add(book)
        db_session.commit()
        return book

def get_or_create_book_list(db_session, title, user, list_type):
    user_id = user.id
    list_id = db_session.query(List).filter_by(user_id=user_id, type=list_type).first().id
    book_id = db_session.query(Book).filter_by(title=title).first().id
    book_list = db_session.query(BookList).filter_by(book_id=book_id, list_id=list_id).first()
    if book_list:
        return book_list
    else:
        book_list = BookList(book_id=book_id, list_id=list_id)
        db_session.add(book_list)
        db_session.commit()
        return book_list

##### Controllers (view functions) #####

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


class EBookForm(FlaskForm):
    text = StringField("Please enter a book title or author:", validators=[Required()])
    submit = SubmitField('Submit')

# TODO: Edit the index route so that, when a tweet is saved by a certain user, that user gets an email. Use the send_email function (just like the one in the textbook) that you defined above.
# NOTE: You may want to create a test gmail account to try this out so testing it out is not annoying. You can also use other ways of making test emails easy to deal with, as discussed in class!
## This is also very similar to example code.
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = EBookForm()
    return render_template('index.html', form = form)

@app.route('/EBookResults', methods=['POST'])
@login_required
def results():
    form = EBookForm()
    if form.validate_on_submit():
        x = books_for_search(form.text.data)
        return render_template("books.html", books = x)

@app.route('/book/<title>', methods=['GET', "POST"])
@login_required
def description(title):
    x = books_for_search(title)[0]
    return render_template('desc.html', desc = x)

@app.route('/book/<title>/read', methods=["POST"])
@login_required
def addtoread(title):
    get_or_create_book_list(db.session, title, current_user, "read")
    return redirect("/")

@app.route('/book/<title>/toRead', methods=["POST"])
@login_required
def addtowanttoread(title):
    get_or_create_book_list(db.session, title, current_user, "toRead")
    return redirect("/")

@app.route('/email/read', methods=["POST"])
@login_required
def emailread():
    read = db.session.query(List, BookList, Book).filter(List.user_id == current_user.id).filter(List.type=="read").join(BookList).join(Book).all()
    send_email(current_user.email, "Your To Read List", "mail/read", read=read)
    flash('Email sent with your read list.')
    return redirect("/lists")

@app.route('/email/toRead', methods=["POST"])
@login_required
def emailtoread():
    toRead = db.session.query(List, BookList, Book).filter(List.user_id == current_user.id).filter(List.type=="toRead").join(BookList).join(Book).all()
    send_email(current_user.email, "Your To Read List", "mail/toRead", toRead=toRead)
    flash('Email sent with your to-read list.')
    return redirect("/lists")

@app.route('/lists', methods=["GET"])
@login_required
def user_lists():
    toRead = db.session.query(List, BookList, Book).filter(List.user_id == current_user.id).filter(List.type=="toRead").join(BookList).join(Book).all()
    read = db.session.query(List, BookList, Book).filter(List.user_id == current_user.id).filter(List.type=="read").join(BookList).join(Book).all()
    return render_template("user_lists.html",read=read, toRead=toRead)

@app.route("/list_item_counts")
def item_counts():
    return jsonify({
        "readListCount": len(db.session.query(List, BookList, Book).filter(List.user_id == current_user.id).filter(List.type=="toRead").join(BookList).join(Book).all()),
        "toReadListCount": len(db.session.query(List, BookList, Book).filter(List.user_id == current_user.id).filter(List.type=="read").join(BookList).join(Book).all()),
        })

if __name__ == '__main__':
    db.create_all()
    manager.run() # Run with this: python main_app.py runserver
    # Also provides more tools for debugging
