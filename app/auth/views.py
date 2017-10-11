import flask
import flask_login
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from . import forms


@auth.before_app_request
def before_request():
    if flask_login.current_user.is_authenticated:
        flask_login.current_user.ping()
        if not flask_login.current_user.confirmed \
                and flask.request.endpoint[:5] != 'auth.' \
                and flask.request.endpoint != 'static':
            return flask.redirect(flask.url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if flask_login.current_user.is_anonymous or flask_login.current_user.confirmed:
        return flask.redirect(flask.url_for('main.index'))
    return flask.render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            flask_login.login_user(user, form.remember_me.data)
            return flask.redirect(flask.request.args.get('next') or flask.url_for('main.index'))
        flask.flash('汝到底是谁?')
    return flask.render_template('auth/login.html', form=form)


@auth.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    flask.flash('再见~')
    return flask.redirect(flask.url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    confirmed=1)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        # confirm mail is disabled tempoary.
        #send_email(user.email, '确认账户',
        #           'auth/email/confirm', user=user, token=token)
        #flask.flash('咱寄出了一封确认账户的电子邮件呐~去看看汝的收件箱呗.')

        return flask.redirect(flask.url_for('auth.login'))
    return flask.render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@flask_login.login_required
def confirm(token):
    if flask_login.current_user.confirmed:
        return flask.redirect(flask.url_for('main.index'))
    if flask_login.current_user.confirm(token):
        flask.flash('咱记下来了~ 已确认邮件地址')
    else:
        flask.flash('汝好像来晚了呢~ 验证码已经过期.')
    return flask.redirect(flask.url_for('main.index'))


@auth.route('/confirm')
@flask_login.login_required
def resend_confirmation():
    token = flask_login.current_user.generate_confirmation_token()
    send_email(flask_login.current_user.email, '确认账户',
               'auth/email/confirm', user=flask_login.current_user, token=token)
    flask.flash('咱寄出了一封确认账户的电子邮件呐~去看看汝的收件箱呗.')
    return flask.redirect(flask.url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@flask_login.login_required
def change_password():
    form = forms.ChangePasswordForm()
    if form.validate_on_submit():
        if flask_login.current_user.verify_password(form.old_password.data):
            flask_login.current_user.password = form.password.data
            db.session.add(flask_login.current_user)
            flask.flash('汝换了新的密码,好耶!')
            return flask.redirect(flask.url_for('main.index'))
        else:
            flask.flash('(￣ε(#￣)☆╰╮(￣▽￣///) 密码不对~')
    return flask.render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not flask_login.current_user.is_anonymous:
        return flask.redirect(flask.url_for('main.index'))
    form = forms.PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重置密码',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=flask.request.args.get('next'))
        flask.flash('咱寄出了一封帮忙重置密码的电子邮件呐~去看看汝的收件箱呗.')
        return flask.redirect(flask.url_for('auth.login'))
    return flask.render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not flask_login.current_user.is_anonymous:
        return flask.redirect(flask.url_for('main.index'))
    form = forms.PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return flask.redirect(flask.url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flask.flash('汝换了新的密码,好耶!')
            return flask.redirect(flask.url_for('auth.login'))
        else:
            return flask.redirect(flask.url_for('main.index'))
    return flask.render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@flask_login.login_required
def change_email_request():
    form = forms.ChangeEmailForm()
    if form.validate_on_submit():
        if flask_login.current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = flask_login.current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=flask_login.current_user, token=token)
            flask.flash('咱寄出了一封帮忙更换邮件地址的电子邮件呐~去看看汝新邮箱的的收件箱呗.')
            return flask.redirect(flask.url_for('main.index'))
        else:
            flask.flash('(￣ε(#￣)☆╰╮(￣▽￣///) 邮件地址或密码不对~.')
    return flask.render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@flask_login.login_required
def change_email(token):
    if flask_login.current_user.change_email(token):
        flask.flash('汝换了新的邮箱，就是这样.')
    else:
        flask.flash('嗯......汝在说啥？ (无效的请求)')
    return flask.redirect(flask.url_for('main.index'))
