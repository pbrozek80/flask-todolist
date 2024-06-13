from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import *
import nh3
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hd%$YkEfBA6O6donzWKHFJDUI7fduh4908JGosokifcui'
ckeditor = CKEditor(app)
Bootstrap5(app)

# Flask-login
# login_manager = LoginManager()
# login_manager.login_view = 'login'
# login_manager.init_app(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def str2boolean(api_input):
    """Reads input strings as Boolean the right way. It is a replacement for native bool() method."""
    list_of_arguments = ['Yes', 'yes', 'checked', 'y', 'true', 'True', '1']
    if api_input in list_of_arguments:
        return True
    else:
        return False


# User (parent)
# List (child)
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    # This will act like a list of List objects attached to each User.
    # The "author" refers to the author property in the List class.
    lists = db.relationship("List", back_populates="author")


class List(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "lists" refers to the posts property in the User class.
    author = db.relationship("User", back_populates="lists")

    name = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    status = db.Column(db.String(100))
    date = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.String(100))
    progress = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, nullable=False)

    # Connecting "List (lists)" with "ListElement (elements)"
    elements = db.relationship("ListElement", back_populates="list_item")


# List (parent)
# ListElement (child)

class ListElement(db.Model):
    __tablename__ = "elements"
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.Integer)
    name = db.Column(db.String(250), unique=True, nullable=False)
    progress = db.Column(db.Integer)
    done = db.Column(db.Boolean, nullable=False)

    # Connection to Lists table:
    # Create Foreign Key, "lists.id" refers to the tablename of Lists.
    list_id = db.Column(db.Integer, db.ForeignKey("lists.id"))
    # Create reference to the List object, the "list_item" refers to the elements protperty in the List class.
    list_item = db.relationship("List", back_populates="elements")

    # Connecting "ListElement (elements)" with "Label(labels)" only with foreign key connected with labels.id
    label_id = db.Column(db.Integer, db.ForeignKey("labels.id"))

# W Labels ma być relacja One To Many
# czyli jedna etykieta może być użyta wielokrotnie


class Label(db.Model):
    __tablename__ = 'labels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    color = db.Column(db.String(50), nullable=False)


# with app.app_context():
#     db.create_all()
# uncomment only on the first start

@app.route('/', methods=['POST', 'GET'])
def index():
    lists = List.query.all()
    heading_title = 'Add a list'
    form = CreateListForm()
    if form.validate_on_submit():
        new_list = List(
            name=nh3.clean(request.form["name"]),
            description=nh3.clean(request.form["description"]),
            status=nh3.clean(request.form["status"]),
            date=date.today(),
            deadline=nh3.clean(request.form["deadline"]),
            progress=nh3.clean(request.form["progress"]),
            priority=nh3.clean(request.form["priority"]),
        )
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("index.html", form=form, heading_text=heading_title, all_lists=lists)


@app.route("/view/list/<int:list_id>", methods=['POST', 'GET'])
def show_list(list_id):
    heading_title = 'Add an element'
    requested_list = List.query.get(list_id)
    requested_elements = ListElement.query.filter_by(list_id=list_id)

    form = CreateListElementForm()
    if form.validate_on_submit():
        new_element = ListElement(
            list_id=list_id,
            name=nh3.clean(request.form["name"]),
            progress=nh3.clean(request.form["progress"]),
            priority=nh3.clean(request.form["priority"]),
            # It should be done with form.get if variable doesn't exist (checkbox not checked)!
            # The same thing in editing cafe
            # https://stackoverflow.com/questions/53791833/how-do-i-get-checkbox-on-using-python-flask-without-causing-a-400-bad-request
            done=str2boolean(request.form.get("done"))
        )
        db.session.add(new_element)
        db.session.commit()
        return redirect(url_for('show_list', list_id=list_id))

    return render_template("list.html", list=requested_list, elements=requested_elements,
                           form=form, heading_text=heading_title, list_id=list_id)


@app.route("/edit/list/<int:list_id>/<int:element_id>", methods=['POST', 'GET'])
def edit_list(list_id, element_id):
    element = ListElement.query.filter_by(id=element_id, list_id=list_id).first()
    edititemform = EditListElementForm(
        name=element.name,
        progress=element.progress,
        priority=element.priority,
        done=element.done,
    )

    if edititemform.validate_on_submit():
        element.name = nh3.clean(request.form.get("name"))
        element.progress = nh3.clean(request.form.get("progress"))
        element.priority = nh3.clean(request.form.get("priority"))
        # It should be done with form.get if variable doesn't exist (checkbox not checked)!
        # The same thing in editing cafe
        # https://stackoverflow.com/questions/53791833/how-do-i-get-checkbox-on-using-python-flask-without-causing-a-400-bad-request
        element.done = str2boolean(request.form.get("done"))
        db.session.commit()
        return redirect(url_for('show_list', list_id=list_id))

    return render_template("editlist.html", editform=edititemform, list_id=list_id)


@app.route('/labels', methods=['POST', 'GET'])
def show_labels():
    labels = Label.query.all()
    heading_title = 'Add a label'
    form = CreateLabelForm()
    if form.validate_on_submit():
        new_label = Label(
            name=nh3.clean(request.form["name"]),
            color=nh3.clean(request.form["color"]),
        )
        db.session.add(new_label)
        db.session.commit()
        return redirect(url_for('show_labels'))
    return render_template("labels.html", form=form, heading_text=heading_title, all_labels=labels)


@app.route("/delete/label/<int:label_id>", methods=['GET'])
def delete_label(label_id):
    label_to_delete = Label.query.filter_by(id=label_id).first()
    db.session.delete(label_to_delete)
    db.session.commit()
    return redirect(url_for('show_labels'))


@app.route("/delete/list/<int:list_id>/<int:element_id>", methods=['GET'])
def delete_element(list_id, element_id):
    element_to_delete = ListElement.query.filter_by(id=element_id, list_id=list_id).first()
    db.session.delete(element_to_delete)
    db.session.commit()
    return redirect(url_for('show_list', list_id=list_id))


if __name__ == "__main__":
    app.run(debug=True)