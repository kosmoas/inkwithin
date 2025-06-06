from flask import( Flask, render_template, jsonify, request, json,
                   flash, get_flashed_messages, session, redirect)
import requests, datetime, entriesdb, os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
load_dotenv()
back = Flask(__name__)
back.secret_key = os.getenv('FLASH_KEY', 'devkey')
entrielist = []

back.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
back.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
userbase = SQLAlchemy(back)
class User(userbase.Model):
    id = userbase.Column('id',userbase.Integer, primary_key=True)
    \
    username = userbase.Column('username',userbase.String(80), unique=True, nullable=False)
    password = userbase.Column('password',userbase.String(200), nullable=False)
with back.app_context():
    userbase.create_all()
def load_entries():
    try:
        with open('journal_entries.json', 'r') as journal:
            entrielist = json.load(journal)
    except (FileNotFoundError):
        entrielist = []
    return entrielist
def save_entries(newlist):
        with open('journal_entries.json', 'w') as journal:
            json.dump(newlist, journal, indent = 4)

@back.route('/')
def home():
    return render_template('journal.html')
@back.route('/api/journal', methods =['POST'])
def journal_page():
    data = request.json # now that I have the data I want to append it to both the entrylist and the file
    listt = load_entries() #loading entries from the json
    listt.append(data) #adding entries to the json
    with open('journal_entries.json', 'w') as entries: #open the file   
        json.dump(listt, entries) #load it onto the file
    return jsonify({'status': 'yes'})
@back.route('/register', methods = ['POST', 'GET'])
def register():
     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username = username).first():
             flash('Sorry this username already exist')
             return redirect('/register')
        hashpass = generate_password_hash(password)
        new_user = User(username = username, password = hashpass)
        userbase.session.add(new_user)
        userbase.session.commit()
        flash('You have sucessfully made a new account!')
        return redirect('/login')
     return render_template('register.html')
@back.route('/login', methods = ['POST', 'GET'])
def login():
     if request.method == 'POST':
          username = request.form['username']
          password = request.form['password']
          user = User.query.filter_by(username = username).first()
          if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash('Logged in!')
                return redirect('/dashboard')
          else:
               flash('Sorry incorrect credentials')
               return redirect('/login')
     return render_template('login.html')
@back.route('/dashboard')
def dashpage():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    entrielist = entriesdb.get_all_entries()
    return render_template('dashboard.html', entries = entrielist, user_id = user.username)
@back.route('/new', methods = ['POST','GET']) #looking out for post methods or get methos
def new_page():
    entry = ''
    if request.method == 'POST':
        entry = request.form.get('journal')
        if entry:
                entries = load_entries()
                data = {
                    'Date': datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                    'user': 'Anon',
                    'entry': entry
                }
                entries.append(data)
                entriesdb.appendtodb(data['user'], data['entry'], data['Date'])
                save_entries(entries)
                flash("✅ Your journal was saved successfully!")
                return redirect("/dashboard")

    return render_template('newentry.html', entry = request.form.get('journal'))
if __name__ == '__main__':
    back.run(debug=True)