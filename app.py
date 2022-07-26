from distutils.log import error
from flask import Flask,render_template,request,redirect,url_for,jsonify,abort
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://postgres:keppi@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db=SQLAlchemy(app)

class Todo(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    description=db.Column(db.String(),nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

db.create_all()

@app.route('/')
def index():
   return  render_template('index.html', data=Todo.query.all())

@app.route('/todos/create', methods=['POST'])
def createtodo():
    error= False
    body={}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error=True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if(error):
        abort (400)
    else:
        return jsonify(body)




if __name__ == '__main__':
    app.run(debug=True)