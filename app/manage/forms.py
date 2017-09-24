import flask_wtf
import wtforms
import wtforms.validators
from ..models import *

class AddTagForm(flask_wtf.FlaskForm):
    add_name = wtforms.StringField('', validators=[wtforms.validators.DataRequired(), wtforms.validators.Length(0, 64)])
    submit = wtforms.SubmitField('增加标签')


class DeleteTagForm(flask_wtf.FlaskForm):
    del_name = wtforms.SelectMultipleField('', coerce=int, validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('删除标签')

    def __init__(self, *args, **kwargs):
        super(DeleteTagForm, self).__init__(*args, **kwargs)
        self.del_name.choices = [(tag.id, tag.name)
                             for tag in Tag.query.order_by(Tag.id).all()]
