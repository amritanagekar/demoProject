from flask import Flask,render_template,request,redirect,url_for,flash,session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SECRET_KEY']='secretkey'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),nullable=False,unique=True)
    emailid = db.Column(db.String(20),nullable=False,unique=True)
    password = db.Column(db.String(80),nullable=False)
    todos = db.relationship('Todo', backref='user')
    
    def __repr__(self) -> str:
        return f"{self.id} - {self.username}"
    
    def __init__(self,emailid,password,username):
        self.username= username
        self.emailid=emailid
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        # print(self.password)
        # print(password)
        return bcrypt.checkpw(password.encode('utf-8'), self.password)
    
class Todo(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200),nullable=True)
    desc = db.Column(db.String(500),nullable=True)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
# db.create_all()
    
# @app.route('/',methods=['GET','POST'])
# def home():
#     return render_template('home.html')
    
@app.route('/',methods=['GET','POST'])
def login():
    if request.method== 'POST':
        # username= request.form['username']
        emailid= request.form['emailid']
        password= request.form['password']
        # print(emailid)
        user=User.query.filter_by(emailid=emailid).first()
        # print(user)

        if user and user.check_password(password):
            # print(user)
            # print(user.check_password)
            session['loggedin']=True
            # session['username']=user.username
            session['emailid']=user.emailid
            session['user_id']=user.id
            return redirect("/dashboard")
        else:
            render_template('login.html',error="Invalid user")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('emailid', None)
    session.pop('user_id',None)
    return redirect('/')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method== 'POST':
        username=request.form['username']
        emailid=request.form['emailid']
        password=request.form['password']
        user= User(username=username,emailid=emailid,password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('register.html')


@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html')   
    return redirect(url_for('login'))

@app.route('/index',methods=['GET','POST'])
def index():
    if 'loggedin' in session:
        if request.method== 'POST':
            title=request.form['title']
            desc=request.form['desc']
            user_id=session['user_id']
            print(desc)
            print(user_id)
            todo = Todo(title=title, desc=desc,user_id=user_id)
            db.session.add(todo)
            db.session.commit()
            # print(user_id)
        allTodo = Todo.query.filter_by(user_id=session['user_id']).all()
        # print(user_id)
        return render_template('index.html',allTodo=allTodo)
    return redirect(url_for('login'))

@app.route('/update/<int:sno>',methods=['GET','POST'])
def update(sno):
        if request.method== 'POST':
           title=request.form['title']
           desc=request.form['desc']
           todo= Todo.query.filter_by(sno=sno).first()
           todo.title= title
           todo.desc=desc
           db.session.add(todo)
           db.session.commit()
           return redirect("/index")
        todo= Todo.query.filter_by(sno=sno).first()
        return render_template('update.html',todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo= Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect('/index')

# if __name__ == '__main__':
    # app.run(debug=True,port=8000)

if __name__ == '__main__':
    # This ensures that the database tables are created before running the app
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5000)