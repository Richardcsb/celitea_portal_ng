import flask_wtf
import wtforms
from wtforms.validators import DataRequired, Length, Email

from ..models import *


class RegistrationForm(flask_wtf.FlaskForm):
    name = wtforms.StringField('汝是谁?', validators=[DataRequired(), Length(0, 64)])
    email = wtforms.StringField('电子邮件地址', validators=[DataRequired(), Length(0, 64), Email()])
    classnum = wtforms.StringField('学号', validators=[DataRequired(), Length(8)])
    gender = wtforms.SelectField('性别', validators=[DataRequired()])
    phone = wtforms.StringField('电话号码', validators=[DataRequired(), Length(11, 11)])
    desc = wtforms.TextAreaField('介绍下汝自己呗~')
    photo = wtforms.FileField('不留张照片？')
    submit = wtforms.SubmitField('就这样?')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.gender.choices = [(1, "男"), (2, "女")]


class InterviewForm(flask_wtf.FlaskForm):
    status = wtforms.RadioField('面试状态', coerce=int, validators=[DataRequired()])
    level = wtforms.SelectField('评价等级', coerce=int, validators=[DataRequired()])
    opinion = wtforms.TextAreaField('评价描述')
    submit = wtforms.SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(InterviewForm, self).__init__(*args, **kwargs)
        self.status.choices = [(status.id, status.text)
                               for status in Interview_status.query.order_by(Interview_status.id).all()]
        self.level.choices = [(i, "☆" * i) for i in range(6)]
