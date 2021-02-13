from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, Length
import enum


class GradeForm(Form):
    num = StringField(
        'num', validators=[DataRequired()]
    )
        

class SemesterForm(Form):
    num = StringField(
        'num', validators=[DataRequired()]
    )
    grade_id = StringField(
        'grade_id', validators=[DataRequired()]
    )
    
class ModuleForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    grade_id = StringField(
        'grade_id', validators=[DataRequired()]
    )
    semester_id = SelectField(
        'semester_id', validators=[DataRequired()],
        choices = [
            ('1', '1'),
            ('2', '2')]
    )
    
class MCQForm(Form):
    question = StringField(
        'question', validators=[DataRequired()]
    )
    choice_A = StringField(
        'choice_A', validators=[DataRequired()]
    )
    choice_B = StringField(
        'choice_B', validators=[DataRequired()]
    )
    choice_C = StringField(
        'choice_C', validators=[DataRequired()]
    )
    choice_D = StringField(
        'choice_D', validators=[DataRequired()]
    )
    choice_E = StringField(
        'choice_E'
    )
    answer = StringField(
        'answer', validators=[DataRequired(), Length(max=1)]
    )
    module_id = StringField(
        'module_id', validators=[DataRequired()]
    )