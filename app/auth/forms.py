import flask_wtf
import wtforms
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from ..models import User


class LoginForm(flask_wtf.FlaskForm):
    email = wtforms.StringField('电子邮件地址', validators=[DataRequired(), Length(1, 64),
                                                      Email()])
    password = wtforms.PasswordField('密码', validators=[DataRequired()])
    remember_me = wtforms.BooleanField('在本次会话中保存登录状态')
    submit = wtforms.SubmitField('登录')


class RegistrationForm(flask_wtf.FlaskForm):
    email = wtforms.StringField('电子邮件地址', validators=[DataRequired(), Length(1, 64),
                                                      Email()])
    username = wtforms.StringField('用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              ' (╯・∧・)╯ ┻━┻ 用户名只能包含字母，数字和下划线。 ')])
    password = wtforms.PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='(╯=﹁"﹁=)╯ ┻━┻ 两次输入的密码不一样')])
    password2 = wtforms.PasswordField('重复密码', validators=[DataRequired()])
    submit = wtforms.SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise wtforms.ValidationError('(ノ｀Д´)ノ┻━┻ 这个邮箱注册过啦~<br />或许汝需要试试 <a href="/auth/login">登录</a>?')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise wtforms.ValidationError('(ノ｀Д´)ノ┻━┻ 这个用户名注册过啦~')


class ChangePasswordForm(flask_wtf.FlaskForm):
    old_password = wtforms.PasswordField('旧密码', validators=[DataRequired()])
    password = wtforms.PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='(╯=﹁"﹁=)╯ ┻━┻ 两次输入的密码不一样')])
    password2 = wtforms.PasswordField('重复一遍新密码', validators=[DataRequired()])
    submit = wtforms.SubmitField('更改密码 | ω・`)')


class PasswordResetRequestForm(flask_wtf.FlaskForm):
    email = wtforms.StringField('邮件地址', validators=[DataRequired(), Length(1, 64),
                                                    Email()])
    submit = wtforms.SubmitField('发送密码重置邮件,Biu~')


class PasswordResetForm(flask_wtf.FlaskForm):
    email = wtforms.StringField('邮件地址', validators=[DataRequired(), Length(1, 64),
                                                    Email()])
    password = wtforms.PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='(╯=﹁"﹁=)╯ ┻━┻ 两次输入的密码不一样')])
    password2 = wtforms.PasswordField('重复一遍新密码', validators=[DataRequired()])
    submit = wtforms.SubmitField('更改密码 | ω・`)')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise wtforms.ValidationError('咦?这个邮件地址咱好像不认识 😂 ')


class ChangeEmailForm(flask_wtf.FlaskForm):
    email = wtforms.StringField('新的邮件地址', validators=[DataRequired(), Length(1, 64),
                                                      Email()])
    password = wtforms.PasswordField('密码', validators=[DataRequired()])
    submit = wtforms.SubmitField('更改邮件地址| ω・`)')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise wtforms.ValidationError('(ノ｀Д´)ノ┻━┻ 这个邮箱注册过啦~')
