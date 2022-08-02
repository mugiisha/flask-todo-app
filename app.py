from distutils.log import error
from flask import Flask,render_template,request,redirect,url_for,jsonify,abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://postgres:keppi@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db=SQLAlchemy(app)
migrate=Migrate(app,db)

class Todo(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    description=db.Column(db.String(),nullable=False)
    completed=db.Column(db.Boolean(),default=False,nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)
    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

class TodoList(db.Model):
    __tablename__='todolists'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(),nullable=False)
    todos = db.relationship('Todo',backref='list',lazy=True)



@app.route('/lists/<list_id>')
def get_list_todos(list_id):
   return  render_template('index.html',
   lists=TodoList.query.all(),
   active_list=TodoList.query.get(list_id)
   , todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/lists/create', methods=['POST'])
def create_list():
    error = False
    body={}
    try:
        list_name=request.get_json()['name']
        list=TodoList(name=list_name)
        db.session.add(list)
        db.session.commit()
        body['name']=list.name
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

@app.route('/lists/<list_id>/delete-list', methods=['DELETE'])
def delete_list(list_id):
    try:
        todo = TodoList.query.get(list_id)
        print(todo)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


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

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed=request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed=completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/<todo_id>/delete-todo', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        print(todo)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))




if __name__ == '__main__':
    app.run(debug=True)