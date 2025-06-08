from flask import( Flask, render_template, jsonify, request, json,
                   flash, get_flashed_messages, session, redirect)
import requests, datetime, os
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
    username = userbase.Column('username',userbase.String(80), unique=True, nullable=False)
    password = userbase.Column('password',userbase.String(200), nullable=False)
class journalent(userbase.Model):
    id = userbase.Column('id',userbase.Integer, primary_key=True)
    user_id = userbase.Column('User_id', userbase.Integer, nullable = False)
    content = userbase.Column('Content', userbase.Text, nullable = False)
    date = userbase.Column('Date', userbase.String(100), nullable = False)
    tag = userbase.Column('Tag', userbase.String(100), nullable = True)
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
@back.route('/logout')
def logout():
     session.pop('user_id', None)
     flash('You have been logged out 🎈')
     return redirect('/login')
@back.route('/edit/<entry_id>', methods = ['GET','POST'])
def edit(entry_id):
    entry = journalent.query.get_or_404(entry_id)
    if entry.user_id != session['user_id']:
        flash('You are not allowed to edit this')
        return redirect('/login')
    if request.method == 'POST':
        entry.content = request.form['content']
        userbase.session.commit()
        flash('You have sucessfully changed it')
        return redirect('/dashboard')
    return render_template('edit_entry.html', entry = entry)
@back.route('/delete/<entry_id>', methods = ['GET','POST'])
def delete_entry(entry_id):
    entry = journalent.query.get_or_404(entry_id)
    if entry.user_id != session['user_id']:
        flash("You are not allowed to delete this")
        return redirect('/dashboard')
    userbase.session.delete(entry)
    userbase.session.commit()
    flash('You have sucessfully deleted the entry')
    return redirect('/dashboard')
     
@back.route('/dashboard')
def dashpage():
    user_id = session.get('user_id')
    if not user_id:
         flash('Sorry please login first')
         redirect('/login')
    user = User.query.get(user_id)
    entrielist = journalent.query.filter_by(user_id = user_id).all()
    return render_template('dashboard.html', entries = entrielist, user_id = user.username)
@back.route('/new', methods = ['POST','GET']) #looking out for post methods or get methos
def new_page():
    entry = ''
    if 'user_id' not in session: 
         flash('You must be logged in to create a message')
         return redirect('/login')
    if request.method == 'POST':
        entry = request.form.get('journal')
        tag = request.form.get('tag')
        print(tag)
        if entry:

                data = journalent(
                    date = datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                    user_id =session['user_id'],
                    content = entry,
                    tag = tag
                )
                userbase.session.add(data)
                userbase.session.commit()
                flash("✅ Your journal was saved successfully!")
                return redirect("/dashboard")

    return render_template('newentry.html', entry = request.form.get('journal'))
if __name__ == '__main__':
    back.run(debug=True)