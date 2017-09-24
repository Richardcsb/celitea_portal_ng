import flask
import flask_login

from . import forms
from . import manage
from ..models import *


@manage.before_request
def before_request():
    if not flask_login.current_user.is_member():
        flask.abort(403)


@manage.route('/')
def manage_index():
    return flask.render_template("manage/index.html")


def operate_add_tag(name):
    tag = Tag.query.filter_by(name=name).first()
    if not tag:
        tag = Tag(name=name)
        db.session.add(tag)
        flask.flash('已添加标签 "{}" 😋😋'.format(name))
    else:
        flask.flash('"{}" 这个标签已经有啦~ 😋😋'.format(name))


def operate_del_tag(name):
    tag = Tag.query.filter_by(name=name).first()
    if tag:
        db.session.delete(tag)
        flask.flash('已删除标签 "{}" 😋😋'.format(name))
    else:
        flask.flash('没有 "{}" 这个标签啦~ 😋😋'.format(name))


@manage.route('/tags/add/<name>', methods=['GET', 'POST'])
def add_tag(name):
    operate_add_tag(name)
    return flask.redirect(url_for('.list_tag'))


@manage.route('/tags/delete/<name>', methods=['GET', 'POST'])
def del_tag(name):
    operate_del_tag(name)
    return flask.redirect(url_for('.list_tag'))


@manage.route('/tags', methods=['GET', 'POST'])
def list_tag():
    tags = Tag.query.all()
    add_tag_form = forms.AddTagForm()
    del_tag_form = forms.DeleteTagForm()
    if add_tag_form.validate_on_submit() or del_tag_form.validate_on_submit():
        if add_tag_form.add_name.data:
            operate_add_tag(add_tag_form.add_name.data)
            return flask.redirect(url_for('manage.list_tag'))
        if del_tag_form.del_name.data:
            for tag_id in del_tag_form.del_name.data:
                tag = Tag.query.filter_by(id=tag_id).first()
                if tag:
                    db.session.delete(tag)
            flask.flash('已删除选定的标签 😋😋')
        return flask.redirect(url_for('manage.list_tag'))
    return flask.render_template("manage/tags.html", tags=tags, add_tag_form=add_tag_form, del_tag_form=del_tag_form)
