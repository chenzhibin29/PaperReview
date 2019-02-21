import pymysql
from flask import *
# 打开数据库连接
db = pymysql.connect("localhost", "root", "123456", "test")

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()


def addUser(username, password, type1):
    sql="insert into test.login_account  values ('%s','%s','%s')" % (username,password,type1)
    db.ping(reconnect=True)
    cursor.execute(sql)
    db.commit()


def addPapertitle(username, papertitle):
    sql = "insert into test.title (username,papertitle) values ('%s','%s')" % (username,papertitle)
    db.ping(reconnect=True)
    cursor.execute(sql)
    db.commit()


def showtitle():
    sql = "SELECT * FROM test.title"
    db.ping(reconnect=True)
    cursor.execute(sql)
    u = cursor.fetchall()
    return render_template('show-cookies.html',u=u)


def showtitle1():
    sql = "SELECT * FROM test.title"
    db.ping(reconnect=True)
    cursor.execute(sql)
    u = cursor.fetchall()
    return render_template('delete-cookies.html',u=u)


def deletePaper(username,papertitle):
    sql = "delete * from test.title where id='%d' username='%s' and papertitle='%s'" %(id,username,papertitle)
    db.ping(reconnect=True)
    cursor.execute(sql)
    u=cursor.fetchall()
    return render_template('delete-cookies.html',u=u)


def isExit(username,password):
    sql = "select * from test.login_account where username='%s' and password='%s'" %(username,password)
    db.ping(reconnect=True)
    cursor.execute(sql)
    result=cursor.fetchall()
    if (len(result)==0):
        return 0
    else:
        return 1


def findAll(type):
    sql = "select * from test.login_account where type1='%s';" % type
    cursor.execute(sql)
    return cursor.fetchall()


def saveScore2(name, score2):
    score = int(score2)
    sql = "insert into score(name,score2) values(%s,%d) on  DUPLICATE key update score2=%d;" % (name, score, score)
    cursor.execute(sql)
    db.commit()


def getScore2(name):
    sql = "select score2 from score where name = %s" % name
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
        sql = "insert into score(name) values(%s)" % name
        cursor.execute(sql)
        db.commit()
        return None
    return result[0][0]


def saveScore1(name, score1):
    score = int(score1)
    sql = "insert into score(name,score1) values(%s,%d) on  DUPLICATE key update score1=%d;" % (name, score, score)
    cursor.execute(sql)
    db.commit()


def getScore1(name):
    sql = "select score1 from score where name = %s" % name
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
        sql = "insert into score(name) values(%s)" % name
        cursor.execute(sql)
        db.commit()
        return None
    return result[0][0]


def findTeachers(name):
    sql = "select * from distribution where student = %s" % name
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
        sql = "insert into distribution(student) values(%s)" % name
        cursor.execute(sql)
        db.commit()
        return (name, None, None)
    return result[0]


def findAllStudentOf(name):
    sql = "select student from distribution where teacher2 = %s" % name
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def saveTeacher2(name, teacher2):
    sql = "insert into distribution(student,teacher2) values(%s,%s) on  DUPLICATE key update teacher2=%s;" % (name, teacher2, teacher2)
    cursor.execute(sql)
    db.commit()


def findTitle(teacherName):
    sql = "select papertitle from title where username = %s;" % teacherName
    cursor.execute(sql)
    result = cursor.fetchall()
    return result[0][0]


def saveTime(time1,time2):
    sql="update test.time_set set (time1,time2)= (str_to_date(%s’,’%%Y-%%m-%%d’),\
    str_to_date(\’%s\’,’%%Y-%%m-%%d’))” %(time1,time2) where num=1 "
    if cursor.execute(sql):
        return 1
    else:
        return 0

