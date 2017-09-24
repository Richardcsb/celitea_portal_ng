from jinja2 import Markup
from flask import current_app
from wtforms.fields import TextAreaField
from wtforms.widgets import HTMLString, TextArea

editormd_html = '''
<div id="editormd">
        <textarea style="display:none;" name="content"></textarea>
</div>
'''


class _editormd(object):
    def include_editormd(self):
        return Markup('''
<script src="/static/components/editor.md/editormd.min.js"></script>
<script type="text/javascript">
    $(function() {
        var editor = editormd("editormd", {
            path : "/static/components/editor.md/lib/", // Autoload modules mode, codemirror, marked... dependents libs path
            width: "100%",
            height: 740,
            codeFold : true,
            saveHTMLToTextarea : false,    // 保存 HTML 到 Textarea
            searchReplace : true,           // 关闭实时预览
            htmlDecode : "style,script,iframe|on*",            // 开启 HTML 标签解析，为了安全性，默认不开启    
            //toolbar  : false,             //关闭工具栏
            //previewCodeHighlight : false, // 关闭预览 HTML 的代码块高亮，默认开启
            emoji : true,
            taskList : true,
            tocm            : true,         // Using [TOCM]
            tex : true,                   // 开启科学公式TeX语言支持，默认关闭
            imageUpload : true,
            imageFormats : ["jpg", "jpeg", "gif", "png", "bmp", "webp"],
            imageUploadURL : "https://img.yoitsu.moe",
            crossDomainUpload : true,
            classPrifex : "input-field",
            onload : function() {
                
            }
        });
    });

</script>
''')

    def html_head(self):
        return self.include_editormd()


class EditorMd(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['editormd'] = _editormd()
        app.context_processor(self.context_processor)

    @staticmethod
    def context_processor():
        return {'editormd': current_app.extensions['editormd']}


class EditorMdWidget(TextArea):
    def __call__(self, field, **kwargs):
        html=editormd_html
        return HTMLString(html)

class EditorMdField(TextAreaField):
    widget = EditorMdWidget()
