# pip3 freeze > requirements.txt
import os
import re
import random

import click
import markdown
# from markdown.extensions.toc import TocExtension
from flask import Flask, render_template, request, Markup, url_for, redirect
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor, CKEditorField


app = Flask(__name__)

# 富文本编辑器
app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_HEIGHT'] = 400
app.secret_key = 'secret string'
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(app.root_path, "data.db")
)

ckeditor = CKEditor(app)
db = SQLAlchemy(app)


class Message(db.Model):
    """用sqlalchemy orm 代替sql来操作数据库"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.Text)


class English(Message):
    pass


class PostForm(FlaskForm):
    title = StringField('Title')
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UploadForm(FlaskForm):
    file_field = FileField(
        "Submit",
        validators=[FileRequired(), FileAllowed("md")]
    )
    submit = SubmitField("submit")


@app.cli.command()
def initdb():
    db.create_all()
    click.echo("create success!")


# 登陆验证成功跳转文件上传
@app.route('/login', methods=['POST', 'GET'])
def login():
    """用flask_login来做登录交互"""
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        user_info = request.form.to_dict()
        username = user_info['u']
        password = user_info['p']
        if username == 'upload' and password == 'aini3333nian.':
            return redirect(url_for('upload'))
        elif username == 'delete' and password == 'aini3333nian.':
            return redirect(url_for('delete'))
        elif username == 'english' and password == 'aini3333nian.':
            return redirect(url_for('english'))
        else:
            return redirect(url_for('login'))


# md文件上传
@app.route("/upload", methods=["'POST'," "GET"])
def upload():
    upload_form = UploadForm()
    if upload_form.validate_on_submit():
        f = request.files["file"]
        base_path = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(base_path, "static/mdDoc/", f.filename)  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
        return redirect(url_for("upload"))
    return render_template("upload.html")


@app.route('/edit1', methods=['GET', 'POST'])
def edit1():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        data = Message(title=title, body=body)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for("message"))
    return render_template('edit1.html', form=form)


# 编辑留言墙(对数据库进行操作)
@app.route("/delete", methods=["POST", "GET"])
def delete():
    if request.method == 'POST':
        data = request.form.to_dict()
        id = data['u']
        db.session.delete(id)
        return redirect(url_for("delete"))
    return render_template("delete.html")


# 前端展示我在阅读英文文档过程中看不懂的句子
@app.route('/edit2', methods=['GET', 'POST'])
def edit2():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        data = English(title=title, body=body)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for("english"))
    return render_template('edit2.html', form=form)


@app.route('/english')
def english():
    # 查询数据库中的英语句子
    message_list = English.query.all()
    return render_template('english.html', message_list=message_list)


@app.route('/talk')
def message():
    # 查询数据库中的留言
    message_list = Message.query.all()
    return render_template('message.html', message_list=message_list)


# 上侧栏的网页们
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/visual')
def visual():
    return render_template('visual.html')


@app.route('/box')
def toolsbox():
    return render_template('toolsbox.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/notes/<name>')
def displayMD(name):
    content = createMD('static/mdDoc/{}.md'.format(name))  # markdown文件的路径
    return render_template('displayMD.html', **locals())


@app.route('/lion')
def lion():
    return render_template('lion.html')


# 将md笔记文件显示为html
def createMD(filename):
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
            'markdown.extensions.toc']
    mdcontent = ""
    with open(filename, 'r', encoding='utf-8') as f:
        mdcontent = f.read()

    html = markdown.markdown(mdcontent, extensions=exts)
    content = Markup(html)
    return content


@app.route('/music')
def music():
    path = './static/music/'
    all_files = os.listdir(path)
    music_list = []
    for i in all_files:
        x = re.findall(r'(.*?).mp3', i)[0]
        music_list.append(x)
        random.shuffle(music_list)
    return render_template('music.html', music_list=music_list)


if __name__ == "__main__":
    app.run(debug=True)
