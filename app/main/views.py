import flask
import flask_login
import flask_sqlalchemy
import werkzeug.contrib.atom
from . import main
from . import forms
from .. import decorators
from .. import models


@main.after_app_request
def after_request(response):
    for query in flask_sqlalchemy.get_debug_queries():
        if query.duration >= models.current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            models.current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not models.current_app.testing:
        flask.abort(404)
    shutdown = models.request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        flask.abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
    if flask_login.current_user.is_member():
        posts = models.Post.query.order_by(
            models.Post.timestamp.desc()).limit(10)
    else:
        posts = models.Post.query.filter_by(is_post=True).order_by(
            models.Post.timestamp.desc()).limit(10)
    return flask.render_template('index.html', posts=posts)


@main.route('/category/<category>')
@decorators.member_required
def category(category):
    category_id = models.Category.query.filter_by(
        name=category).first_or_404().id
    posts = models.Post.query.filter_by(
        category_id=category_id).order_by(models.Post.timestamp.desc())
    return flask.render_template('index.html', posts=posts)


@main.route('/user/<username>')
@flask_login.login_required
def user(username):
    user = models.User.query.filter_by(username=username).first_or_404()
    page = models.request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(models.Post.timestamp.desc()).paginate(
        page, per_page=models.current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return flask.render_template('user.html', user=user, posts=posts,
                                 pagination=pagination, show_followed=True)


@main.route('/edit-profile', methods=['GET', 'POST'])
@flask_login.login_required
def edit_profile():
    form = forms.EditProfileForm()
    if form.validate_on_submit():
        flask_login.current_user.name = form.name.data
        flask_login.current_user.about_me = form.about_me.data
        flask_login.current_user.telegram = form.telegram.data
        flask_login.current_user.blog = form.blog.data
        flask_login.current_user.twitter = form.twitter.data
        flask_login.current_user.github = form.github.data
        models.db.session.add(flask_login.current_user)
        for tag in flask_login.current_user.tags.all():
            models.db.session.delete(tag)
        for tag in form.tag.data:
            conn = models.Connection(
                user_id=flask_login.current_user.id, user_tag_id=tag)
            models.db.session.add(conn)
        flask.flash('已更新个人资料,biu~')
        return flask.redirect(models.url_for('.user', username=flask_login.current_user.username))
    form.name.data = flask_login.current_user.name
    form.about_me.data = flask_login.current_user.about_me
    form.telegram.data = flask_login.current_user.telegram
    form.blog.data = flask_login.current_user.blog
    form.tag.data = [connect.user_tag_id for connect in list(
        flask_login.current_user.tags.all())]
    form.twitter.data = flask_login.current_user.twitter
    form.github.data = flask_login.current_user.github
    return flask.render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@flask_login.login_required
@decorators.admin_required
def edit_profile_admin(id):
    user = models.User.query.get_or_404(id)
    form = forms.EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = models.Role.query.get(form.role.data)
        user.name = form.name.data
        user.about_me = form.about_me.data
        models.db.session.add(user)
        flask.flash('已更新个人资料,biu~')
        return flask.redirect(models.url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.about_me.data = user.about_me
    return flask.render_template('edit_profile.html', form=form, user=user)


@flask_login.login_required
@main.route("/create-post", methods=['GET', 'POST'])
def create_post():
    form = forms.PostForm(allow_post=flask_login.current_user.is_moderator())
    if form.validate_on_submit():
        post = models.Post(title=form.title.data,
                           is_post=(form.category.data == 1),
                           category_id=form.category.data,
                           body=form.content.data,
                           author_id=flask_login.current_user._get_current_object().id)
        models.db.session.add(post)
        models.db.session.commit()
        for tag in form.tag.data:
            conn = models.PostConnection(
                post_id=post.id, post_tag_id=tag)
            models.db.session.add(conn)
        return flask.redirect(models.url_for('.index'))
    return flask.render_template('create_post.html', form=form, current_user=flask_login.current_user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = models.Post.query.get_or_404(id)
    if not post.is_post and not flask_login.current_user.is_member():
        flask.abort(403)
    form = forms.CommentForm()
    if form.validate_on_submit():
        comment = models.Comment(body=form.body.data,
                                 post=post,
                                 author=flask_login.current_user._get_current_object())
        models.db.session.add(comment)
        flask.flash('电波已成功到达目标位置~')
        return flask.redirect(models.url_for('.post', id=post.id, page=-1))
    comments = post.comments.order_by(models.Comment.timestamp.asc()).all()
    return flask.render_template('post.html', posts=[post], form=form,
                                 comments=comments)


@main.route('/post/<int:id>.md', methods=['GET'])
def post_raw(id):
    post = models.Post.query.get_or_404(id)
    if not post.is_post and not flask_login.current_user.is_member():
        flask.abort(403)
    response = flask.make_response(post.body)
    response.headers['Content-Type'] = "text/plain"
    return response


@flask_login.login_required
@main.route('/post/<int:id>/edit', methods=['GET', 'POST'])
def edit_post(id):
    post = models.Post.query.get_or_404(id)
    if post.author_id != flask_login.current_user.id:
        if not flask_login.current_user.is_administrator():
            flask.abort(403)
    form = forms.PostForm(allow_post=flask_login.current_user.is_moderator())
    if form.validate_on_submit():
        post.title = form.title.data
        post.is_post = (form.category.data == 1)
        post.category_id = form.category.data
        post.body = form.content.data
        post.author_id = flask_login.current_user._get_current_object().id
        models.db.session.add(post)
        models.db.session.commit()
        for tag in post.tags.all():
            models.db.session.delete(tag)
        for tag in form.tag.data:
            conn = models.PostConnection(
                post_id=post.id, post_tag_id=tag)
            models.db.session.add(conn)
        return flask.redirect(models.url_for('.post', id=id))
    form.title.data = post.title
    form.category.data = post.category
    form.tag.data = [tag.id for tag in post.tags.all()]
    return flask.render_template('create_post.html', form=form, current_user=flask_login.current_user, post=post)


@main.route('/feed.atom')
def recent_feed():
    feed = werkzeug.contrib.atom.AtomFeed('Celitea 计算机精英协会',
                                          feed_url=flask.request.url, url=flask.request.url_root)
    posts = models.Post.query.filter_by(is_post=True).order_by(
        models.Post.timestamp.desc()).limit(10).all()
    for post in posts:
        feed.add(post.title, post.body_html,
                 content_type='html',
                 author=post.author.username,
                 url=flask.request.url_root +
                 flask.url_for('.post', id=post.id),
                 updated=post.timestamp,
                 published=post.published)
    return feed.get_response()


@main.route('/archives')
def archives():
    if flask_login.current_user.is_member():
        posts = models.Post.query.order_by(models.Post.timestamp.desc()).all()
    else:
        posts = models.Post.query.filter_by(is_post=True).order_by(
            models.Post.timestamp.desc()).all()
    return flask.render_template('archives.html', posts=posts)
