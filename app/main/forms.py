import flask_wtf
import wtforms
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..pagedown import PageDownField
from ..editormd import EditorMdField
from ..models import *


class NameForm(flask_wtf.FlaskForm):
    name = wtforms.StringField('汝是谁?', validators=[DataRequired()])
    submit = wtforms.SubmitField('OK')


class RegistrationForm(flask_wtf.FlaskForm):
    name = wtforms.StringField('汝是谁?', validators=[DataRequired(), Length(0, 64)])
    email = wtforms.StringField('电子邮件地址', validators=[DataRequired(), Length(0, 64), Email()])
    classnum = wtforms.StringField('学号', validators=[DataRequired(), Length(8)])
    gender = wtforms.SelectField('性别', validators=[DataRequired()])
    phone = wtforms.StringField('电话号码', validators=[DataRequired(), Length(11, 11)])
    telegram = wtforms.StringField('Telegram (用户名，不含"@")', validators=[Length(0, 64)])
    personal_page = wtforms.StringField('Blog', validators=[Length(0, 64)])
    ability = wtforms.TextAreaField('汝都擅长些啥咧？')
    desc = wtforms.TextAreaField('介绍下汝自己呗~')
    photo = wtforms.FileField('不留张照片？')
    submit = wtforms.SubmitField('就这样?')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.gender.choices = [(1, "男"), (2, "女")]


class EditProfileForm(flask_wtf.FlaskForm):
    name = wtforms.StringField('真实姓名', validators=[Length(0, 64)])
    about_me = wtforms.TextAreaField('介绍下汝自己呗~')
    tag = wtforms.SelectMultipleField('标签', coerce=int)
    telegram = wtforms.StringField('Telegram (用户名，不含"@")', validators=[Length(0, 64)])
    blog = wtforms.StringField('Blog', validators=[Length(0, 64)])
    twitter = wtforms.StringField('Twitter (用户名，不含"@")', validators=[Length(0, 64)])
    github = wtforms.StringField('Github 用户名', validators=[Length(0, 64)])
    submit = wtforms.SubmitField('就这样?')

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.tag.choices = [(tag.id, tag.name)
                            for tag in Tag.query.order_by(Tag.id).all()]


class EditProfileAdminForm(flask_wtf.FlaskForm):
    email = wtforms.StringField('Email', validators=[DataRequired(), Length(1, 64),
                                                     Email()])
    username = wtforms.StringField('用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              ' (╯・∧・)╯ ┻━┻ 用户名只能包含字母，数字和下划线。 ')])
    confirmed = wtforms.BooleanField('已确认')
    role = wtforms.SelectField('角色', coerce=int)
    name = wtforms.StringField('真实姓名', validators=[Length(0, 64)])
    about_me = wtforms.TextAreaField('介绍')
    submit = wtforms.SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise wtforms.ValidationError('(ノ｀Д´)ノ┻━┻ 这个邮箱注册过啦~')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise wtforms.ValidationError('(ノ｀Д´)ノ┻━┻ 这个用户名注册过啦~')


class PostForm(flask_wtf.FlaskForm):
    title = wtforms.StringField("这里是标题", validators=[DataRequired()])
    category = wtforms.SelectField("选个分类吧", coerce=int)
    tag = wtforms.SelectMultipleField('标签', coerce=int)
    content = EditorMdField()
    submit = wtforms.SubmitField('咱写好了')
    def __init__(self, allow_post=False, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all() if category.id != 1]
        self.tag.choices = [(tag.id, tag.name)
                            for tag in Tag.query.order_by(Tag.id).all()]
        if allow_post:
            self.category.choices.insert(0, (1, "社团消息"))
            

class CommentForm(flask_wtf.FlaskForm):
    body = wtforms.StringField('汝不说些啥?', validators=[DataRequired()])
    submit = wtforms.SubmitField('好啦好啦,我说就是了~')


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
