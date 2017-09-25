import os
import time

import flask
import flask_login
import werkzeug.utils

from . import registration
from .forms import RegistrationForm, InterviewForm
from ..decorators import hr_operate_required
from ..models import *


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


def convert_image(original, path):
    os.system("cp {} {}/".format(original, path))
    os.system("mogrify -resize 1000x1000\> -format jpg {}".format(original))


@flask_login.login_required
@registration.route('/', methods=['GET', 'POST'])
def main():
    if flask_login.current_user.can(Permission.MODERATE_REGISTRATIONS):
        return flask.redirect(url_for('.lists'))
    else:
        return flask.redirect(url_for('.register'))


@flask_login.login_required
@registration.route('/add', methods=['GET', 'POST'])
def register():
    if flask_login.current_user.can(Permission.MEMBER):
        flask.flash("汝已经是正式成员啦~")
        return flask.redirect('/')

    form = RegistrationForm()
    registrations = set([registration.classnum for registration in
                         Registration.query.order_by("classnum").all()])
    if request.method == 'POST':
        if not form.validate_on_submit():
            register = Registration()
            register.id = flask_login.current_user.id
            register.email = form.email.data
            register.classnum = form.classnum.data
            register.name = form.name.data
            register.gender = form.gender.data
            register.desc = form.desc.data.replace("\r\n", "\n")
            register.phone = form.phone.data
            file = request.files['photo']
            print(file.filename)
            # if user does not select file, browser also
            # submit a empty part without filename
            if register.classnum in registrations:
                flask.flash("(╯´ω`)╯ ┻━┻ 汝不是已经报名过了么")
                return flask.redirect(request.url)
            if not file.filename:
                flask.flash('No selected file')
                return flask.redirect(request.url)
            if file and allowed_file(file.filename.lower()):
                interview = Interview()
                filename = werkzeug.utils.secure_filename(str(time.time()).replace(".", ""))
                upload_dir = current_app.config['UPLOAD_DIR']
                file.save(os.path.join(upload_dir, filename))
                convert_image(original=os.path.abspath(os.path.join(upload_dir, filename))
                              , path=os.path.abspath(os.path.join(upload_dir) + "/original"))
                register.photo = filename
                # send_email(register.email, '{}的报名确认~'.format(register.name),
                #           'mail/registration', reg=register)
                # print(current_app.sms.async_send_mass_sms_code("celitea-纳新",register.phone))
                db.session.add(register)
                interview.id = register.id
                interview.status = 1
                db.session.add(interview)
                flask.flash('OK，坐下来放松一下呗~')
                return flask.redirect("/")
            else:
                flask.flash("这不是照片 (╯=3=)╯ ┻━┻")
    form.email.data = flask_login.current_user.email
    return flask.render_template('registrations/add.html', form=form)


@registration.route('/list')
@registration.route('/list/<status>')
@flask_login.login_required
@hr_operate_required
def lists(status="all"):
    statuses = {"all": 0, "ready": 1, "confirmed": 2, "rejected": 3, "talking": 4}
    if not status in statuses:
        flask.abort(404)
    if status == "all":
        reg = Registration.query.order_by("classnum").all()
    else:
        reg = [user for user in Registration.query.order_by("classnum").all() if
               user.interview.status == statuses[status]]
    return flask.render_template("registrations/list.html", registrations=reg, length=len(reg))


@registration.route('/view/<classnum>', methods=['GET', 'POST'])
@flask_login.login_required
@hr_operate_required
def view(classnum):
    # Find this registrations
    reg_query = Registration.query.order_by("classnum")
    classnums = {registration.classnum: registration.id for registration in reg_query.all()}
    classnum_ids = sorted(classnums.keys())
    current_reg = reg_query.filter_by(classnum=classnum).first_or_404()
    current_interview = Interview.query.filter_by(id=classnums[classnum]).first()
    current_reg_position = classnum_ids.index(current_reg.classnum)
    # Try find +1 -1 registrations.
    try:
        priv_reg = False
        if current_reg_position - 1 >= 0:
            priv_reg = reg_query.filter_by(id=classnums[classnum_ids[current_reg_position - 1]]).first()
    except KeyError or IndexError:
        priv_reg = False
    try:
        next_reg = False
        if current_reg_position + 1 < len(classnum_ids):
            next_reg = reg_query.filter_by(id=classnums[classnum_ids[current_reg_position + 1]]).first()
    except KeyError or IndexError or AssertionError:
        next_reg = False
    # Make from
    form = InterviewForm()
    if form.validate_on_submit():
        current_interview.status = form.status.data
        current_interview.level = form.level.data
        current_interview.opinion = form.opinion.data
        db.session.add(current_interview)
        if current_interview.status == 2:
            reg_user = User.query.filter_by(id=current_interview.id).first()
            reg_user.role_id = 2
            db.session.add(reg_user)
        return flask.redirect(url_for('.lists'))
    form.status.data = current_interview.status
    form.level.data = current_interview.level
    form.opinion.data = current_interview.opinion
    return flask.render_template("registrations/view.html", reg=current_reg, priv_reg=priv_reg, next_reg=next_reg,
                                 form=form)


@registration.route("/delete/<int:id>")
@flask_login.login_required
@hr_operate_required
def delete(id):
    reg_query = Registration.query.filter_by(id=id).first_or_404()
    db.session.delete(reg_query)
    try:
        os.remove(os.path.abspath(os.path.join(current_app.config['UPLOAD_DIR'], reg_query.photo)))
        os.remove(os.path.abspath(os.path.join(current_app.config['UPLOAD_DIR'], "original", reg_query.photo)))
    except FileNotFoundError:
        pass
    flask.flash("嗯，这个不好吃~")
    return flask.redirect(url_for('.registrations'))


@registration.route('/export')
@registration.route('/export/<status>')
@flask_login.login_required
@hr_operate_required
def export(status="all"):
    statuses = {"all": 0, "ready": 1, "confirmed": 2, "rejected": 3, "talking": 4}
    if not status in statuses:
        flask.abort(404)
    if status == "all":
        reg = Registration.query.order_by("classnum").all()
    else:
        reg = [user for user in Registration.query.order_by("classnum").all() if
               user.interview.status == statuses[status]]
    title = "姓名,性别,电子邮件地址,专业和班级,电话号码,特长与兴趣,自我介绍"
    str_reg_list = [title]
    for registration in reg:
        str_reg = "{},{},{},{},{},{},{}".format(registration.name,
                                                {1: "男", 2: "女"}[registration.gender],
                                                registration.email,
                                                registration.classnum,
                                                registration.phone,
                                                registration.ablity.replace("\r\n", "\n").replace("\n", ' ') or "",
                                                registration.desc.replace("\r\n", "\n").replace("\n", ' ') or "")
        str_reg_list.append(str_reg)
    response = flask.make_response("\n".join(str_reg_list))
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response
