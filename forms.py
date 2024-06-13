from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, DateField, BooleanField, IntegerRangeField, \
    HiddenField, ColorField
from wtforms.validators import DataRequired, NumberRange


# WTForm

class CreateListElementForm(FlaskForm):
    name = StringField("Item name", validators=[DataRequired()])
    progress = IntegerRangeField("Progress (%)", validators=[NumberRange(0, 100)])
    priority = IntegerRangeField("Priority (1-6)", validators=[DataRequired(), NumberRange(1, 6)])
    done = BooleanField("Done")
    submit = SubmitField("Save item")


class EditListElementForm(FlaskForm):
    name = StringField("Item name", validators=[DataRequired()])
    progress = IntegerRangeField("Progress (%)", validators=[NumberRange(0, 100)])
    priority = IntegerRangeField("Priority (1-6)", validators=[DataRequired(), NumberRange(1, 6)])
    done = BooleanField("Done")
    submit = SubmitField("Save item")


class CreateListForm(FlaskForm):
    name = StringField("List Name", validators=[DataRequired()])
    description = StringField("List description", validators=[DataRequired()])
    status = StringField("Status")
    deadline = DateField("Deadline date")
    progress = IntegerRangeField("Progress (%)", validators=[NumberRange(0, 100)])
    priority = IntegerRangeField("Priority (1-6)", validators=[DataRequired(), NumberRange(1, 6)])
    submit = SubmitField("Save list")


class CreateLabelForm(FlaskForm):
    name = StringField("Label name", validators=[DataRequired()])
    color = ColorField("Pick #hex color", validators=[DataRequired()])
    submit = SubmitField("Save label")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class SignInForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


# class CommentForm(FlaskForm):
#     text = CKEditorField("Comment", validators=[DataRequired()])
#     submit = SubmitField("Submit Comment")