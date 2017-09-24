import flask
from . import main


@main.app_errorhandler(403)
def forbidden(e):
    if flask.request.accept_mimetypes.accept_json and \
            not flask.request.accept_mimetypes.accept_html:
        response = flask.jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return flask.render_template('errors/403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    if flask.request.accept_mimetypes.accept_json and \
            not flask.request.accept_mimetypes.accept_html:
        response = flask.jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return flask.render_template('errors/404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if flask.request.accept_mimetypes.accept_json and \
            not flask.request.accept_mimetypes.accept_html:
        response = flask.jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return flask.render_template('errors/500.html'), 500
