from werkzeug.utils import secure_filename
from flask import *
from db import *
from wtforms import Form,TextField,PasswordField,validators,SubmitField,FieldList,StringField
import os
import time
import math

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '加密Session所需的密钥'

#文件上传及下载的一些配置和函数
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 设置文件上传的目标文件夹
basedir = os.path.abspath(os.path.dirname(__file__))  # 获取当前项目的绝对路径
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc','docx'])  # 允许上传的文件后缀
users = []  # 这里存放所有的留言

# 判断文件是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


#登陆账号类
class LoginForm(Form):
    username=TextField('username',[validators.DataRequired()])
    password = PasswordField('password', [validators.DataRequired()])
    type1=TextField('type',[validators.DataRequired()])


class TitleForm(Form):
    username = TextField('username', [validators.DataRequired()])
    papertitle = TextField('papertitle',[validators.DataRequired()])


class TeacherStep3Form(Form):
    scores = FieldList(StringField('score', [validators.DataRequired()]), label='分数', min_entries=50)


class AdminStep3Form(Form):
    teachers = FieldList(StringField('teacher', [validators.DataRequired()]), label='评审教师', min_entries=50)



#主页
@app.route('/')
def index():
    return render_template('mainpage.html')


@app.route('/firstpage')
def firstpage():
    return render_template('firstpage.html')

# 登陆
@app.route('/login', methods=['get', 'post'])
def login():
    myform = LoginForm(request.form)
    if request.method == 'POST':
        if isExit(myform.username.data, myform.password.data,):
            session['username'] = myform.username.data
            session['type1'] = myform.type1.data
            session.permanent = True
            flash('登陆成功')
            return redirect(url_for('firstpage'))
        else:
            message = '登陆失败，账号或密码错误'
            return render_template('login.html', message=message, form=myform)
    return render_template('login.html', form=myform)

#获取当前用户名以维持登录状态
@app.context_processor
def my_context_processor():
    user = session.get('username')
    if user:
        return {'login_user': user}
    return {}


#登出
@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))


#注册
@app.route('/register', methods=['GET','POST'])
def register():
    myform=LoginForm(request.form)
    if request.method=='POST' and myform.validate():
        addUser(myform.username.data, myform.password.data, myform.type1.data)
        flash('注册成功,正在跳转。。。')
        return redirect(url_for('login'))
    return render_template('register.html', form=myform)


@app.route('/submit', methods=['GET','POST'])
def submit1():
    myform1=TitleForm(request.form)
    if request.method=='POST' and myform1.validate():
        addPapertitle(myform1.username.data, myform1.papertitle.data)
        return redirect(url_for('submit1'))
    return render_template('teacher_title.html', form=myform1)

@app.route('/delete', methods=['GET','POST'])
def delete():
    myform=TitleForm(request.form)
    if request.method=='POST' and myform.validate():
        deletePaper(myform.id.data,myform.username.data,myform.papertitle.data)
        return redirect(url_for('showtitle1'))
    return render_template('delete-cookies.html',form=myform)

# 选题
@app.route('/step1', methods=['GET', 'POST'])
def step1():
    if session['type1'] == '管理员':
        return showtitle1()
    elif session['type1'] == '学生':
        return showtitle()
    elif session['type1'] == '教师':
        return submit1()



# 提交/修改论文
@app.route('/step2', methods=['GET', 'POST'])
def step2():
    if session['type1'] == '学生':
        return get_form()
    elif session['type1'] == '教师':
        #return redirect(url_for('submit'))
        return get_request_data()


# 答辩
@app.route('/step3', methods=['GET', 'POST'])
def step3():
    if session['type1'] == '管理员':
        return redirect(url_for("admin_step3", type_request='admin'))
    elif session['type1'] == '学生':
        return student_step3()
    elif session['type1'] == '教师':
        return teacher_step3()


def teacher_step3():
    myform = TeacherStep3Form(request.form)
    students = findAllStudentOf(session['username'])
    students_data = list()
    topic = findTitle(session["username"])
    topic = topic if topic else "未定题"
    for index, student in enumerate(students):
        students_data.append([student[0], topic])

    if request.method == 'POST':
        for index, student in enumerate(students):
            saveScore2(student[0], myform.scores.data[index])
        flash('提交成功')
    else:
        for index, student in enumerate(students):
            myform.scores.entries[index].data = getScore2(student[0])
    return render_template('teacher_step3.html', form=myform, students=students_data)


def student_step3():
    student = session['username']
    score1 = getScore1(student)
    score2 = getScore2(student)
    score3 = '未评分'

    if score1 and score2:
        score3 = round((score1 + score2)/2, 1)
    score1 = round(float(score1), 1) if score1 else '未评分'
    score2 = round(float(score2), 1) if score2 else '未评分'

    two_teachers = findTeachers(session["username"])
    teacher1 = two_teachers[1]
    teacher1 = teacher1 if teacher1 else "未分配"

    teacher_name = teacher1 if teacher1 != "未分配" else "null"
    topic = findTitle(teacher_name)
    topic = topic if topic else "未定题"

    data = [
        teacher1,
        topic,
        score1,
        score2,
        score3
    ]
    return render_template('student_step3.html', data=data)


@app.route('/step3/<type_request>', methods=['GET', 'POST'])
def admin_step3(type_request):
    myform = AdminStep3Form(request.form)
    students = findAll("学生")
    data = []

    # 填充数据
    for index, student in enumerate(students):
        student_name = student[0]

        two_teachers = findTeachers(student_name)
        teacher1 = two_teachers[1]
        teacher2 = two_teachers[2]
        teacher1 = teacher1 if teacher1 else "未分配"
        teacher2 = teacher2 if teacher2 else "未分配"

        teacher_name = teacher1 if teacher1 != "未分配" else "null"
        topic = findTitle(teacher_name)
        topic = topic if topic else "未定题"

        score1 = getScore1(student_name)
        score2 = getScore2(student_name)
        score3 = '未评分'
        if score1 and score2:
            score3 = round((score1 + score2)/2, 1)
        score1 = round(float(score1), 1) if score1 else '未评分'
        score2 = round(float(score2), 1) if score2 else '未评分'

        data.append([student_name, topic, teacher1, score1, score2, score3])

        if request.method == 'POST':
            teacher_name = myform.teachers.data[index]
            if teacher_name != "未分配":
                saveTeacher2(student_name, myform.teachers.data[index])
        else:
            myform.teachers.entries[index].data = teacher2

    if request.method == 'POST':
        return redirect(url_for("admin_step3", type_request='admin'))

    if type_request == "admin":
        return render_template('admin_step3.html', form=myform, data=data)
    elif type_request == "distribute":  # 自动分配
        teachers = findAll("教师")
        students_num = float(len(students))
        teachers_num = float(len(teachers))
        students_number_per_teacher = math.ceil(students_num / teachers_num)
        teacherDict = {}
        for teacher in teachers:
            teacherDict[teacher[0]] = 0

        for index, entry in enumerate(myform.teachers.entries):
            if entry.data == "未分配":
                teacher_pick = None
                for teacher in teachers:
                    if teacherDict[teacher[0]] < students_number_per_teacher:
                        teacher_pick = teacher[0]
                        teacherDict[teacher[0]] += 1
                        break
                myform.teachers.entries[index].data = teacher_pick
            elif entry.data != '':
                print(entry.data)
                print(teacherDict)
                teacherDict[entry.data] += 1

        return render_template('admin_step3.html', form=myform, data=data)
#管理员上传日期
@app.route('/upload',methods=['post','get'])
def upload():
    if request.method == 'POST':
        time1 = request.form['dinggang']
        time2 = request.form['tijiao']
        if saveTime(time1,time2):
            return redirect(url_for('upload'))
        else:
            message = '提交失败'
            return render_template('admin.html', message=message)
    return render_template('admin.html')


#管理员上传文件
@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])  # 拼接成合法文件夹地址
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # 文件夹不存在就创建
    f=request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname=f.filename
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = str(unix_time)+'.'+ext   # 修改文件名
        f.save(os.path.join(file_dir, new_filename))  #保存文件到upload目录

        return jsonify({"errno": 0, "errmsg": "上传成功"})
    else:
        return jsonify({"errno": 1001, "errmsg": "上传失败"})


#下载细则
@app.route("/download/one.docx")
def download():
    dirpath = os.path.join(app.root_path, 'upload')  # 这里是下在目录，从工程的根目录写起，比如你要下载static/js里面的js文件，这里就要写“static/js”
    return send_from_directory(dirpath, 'one.docx', as_attachment=True)  # as_attachment=True 一定要写，不然会变成打开，而不是下载


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')



@app.route('/form', methods=['get'])
def get_form():
    return render_template('form.html')


@app.route('/form', methods=['post'])
def submit_form():
    form = request.form
    file = request.files['file']
    if file:
        app.logger.debug(f'filename:{file.filename}')
        app.logger.debug(f'secure_filename:{secure_filename(file.filename)}')
        file.save(f'uploaded_files/{file.filename}')
    app.logger.debug(form)
    return render_template('form-result.html', data=form)

@app.route('/say/', methods=['GET', 'POST'])
def say():
    if request.method == 'GET':
        return render_template('form-result.html', says=users)
    else:
        title = request.form.get('say_title')
        text = request.form.get('say')
        user = request.form.get('say_user')
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        users.append({"title": title,
"text": text,
"user": user,
"date": date})
    return redirect(url_for('say'))

@app.route('/files')
def get_uploaded_file():
    filename = request.args['filename']
    return send_file(filename)

@app.route('/get_request_data')
def get_request_data():
    data = request.values
    return render_template('form-result.html', data=data)


def before_request():
    import glob
    files = glob.glob('uploaded_files/*')
    session['files'] = files


if __name__ == '__main__':
    app.before_request(before_request)
    app.run(host='127.0.0.1')
