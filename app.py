from flask import Flask,render_template,request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200),nullable=True)
    desc = db.Column(db.String(500),nullable=True)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

# db.create_all()


@app.route('/',methods=['GET','POST'])
def hello_world():
    if request.method== 'POST':
        title=request.form['title']
        desc=request.form['desc']
        todo = Todo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()
    allTodo= Todo.query.all()
    print(allTodo)
    return render_template('index.html',allTodo=allTodo)

@app.route('/show')
def products():
    allTodo= Todo.query.all()
    print(allTodo)
    return 'this is products pavge!'


# if __name__ == '__main__':
    # app.run(debug=True,port=8000)

if __name__ == '__main__':
    # This ensures that the database tables are created before running the app
    with app.app_context():
        db.create_all()
    app.run(debug=True)