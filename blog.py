from flask import Flask,render_template,flash,request,session,redirect
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from flask_ckeditor import CKEditor
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from werkzeug.security import generate_password_hash,check_password_hash
import os
app=Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='XXXXXXX'
app.config['MYSQL_DB']='flog_db'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)
CKEditor(app)
Bootstrap(app)
app.config['SECRET_KEY']=os.urandom(24)

@app.route('/')
def index():
    cur=mysql.connection.cursor()
    res=cur.execute("SELECT * FROM blog")
    if res>0:
        blogs=cur.fetchall();
        cur.close()
        return render_template('index.html', blogs=blogs)
    cur.close()
    return render_template('index.html', blogs=None)
    return render_template('index.html')
@app.route('/about/')
def about():
    return render_template('about.html')
@app.route('/blogs/<int:id>/')
def blogs(id):
     cur=mysql.connection.cursor()
     res=cur.execute("SELECT * FROM blog WHERE blog_id={}".format(id))
     if res>0:
         blog=cur.fetchone()
         return render_template('blogs.html',blog=blog)
     return 'Blog not found'

@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method=='POST':
        userd=request.form
        if userd['psw']!=userd['pswrepeat']:
            flash("Password donot match Try again!",'danger')
            return render_template('register.html')
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO user(first_name,last_name,username,email,password)VALUES(%s,%s,%s,%s,%s)",[userd['first_name'],userd['last_name'],userd['username'],userd['email'],generate_password_hash(userd['psw'])])
        mysql.connection.commit();
        cur.close()
        flash("registeration successful Please login")
        return redirect('/login/')
    return render_template('register.html')

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=='POST':
        userd=request.form
        username=userd['username']
        cur=mysql.connection.cursor()
        res=cur.execute("SELECT * FROM user WHERE username=%s",([username]))
        if res>0:
            user=cur.fetchone()
            if check_password_hash(user['password'],userd['password']):
                session['login']=True
                session['firstName']=user['first_name']
                session['lastName']=user['last_name']
                flash('welcome'+session['firstName']+'you have successfully logged in','success')
            else:
                cur.close()
                flash("password doesnot match",'danger')
                return render_template('login.html')
        else:
            cur.close()
            flash("user not found",'danger')
            return render_template('login.html')
        cur.close()
        return redirect('/')
    return render_template('login.html')


@app.route('/write-blog/',methods=['GET','POST'])
def write_blog():
    if request.method=='POST':
        blogd=request.form
        title=blogd['title']
        body=blogd['body']
        author=session['firstName']+' '+session['lastName']
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO blog(title,author,body)VALUES(%s,%s,%s)",([title,author,body]))
        mysql.connection.commit()
        cur.close()
        #flash
        return redirect('/')
    return render_template('write_blog.html')

@app.route('/my-blogs/')
def my_blogs():
    author = session['firstName'] + ' ' + session['lastName']
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM blog WHERE author = %s",[author])
    if result_value > 0:
        my_blogs = cur.fetchall()
        return render_template('my_blogs.html',my_blogs=my_blogs)
    else:
        return render_template('my_blogs.html',my_blogs=None)


@app.route('/edit-blog/<int:id>/',methods=['GET','POST'])
def edit_blog(id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        title = request.form['title']
        body = request.form['body']
        cur.execute("UPDATE blog SET title = %s, body = %s where blog_id = %s",(title, body, id))
        mysql.connection.commit()
        cur.close()
        flash('Blog updated successfully', 'success')
        return redirect('/blogs/{}'.format(id))
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))
    if result_value > 0:
        blog = cur.fetchone()
        blog_form = {}
        blog_form['title'] = blog['title']
        blog_form['body'] = blog['body']
        return render_template('edit_blog.html', blog_form=blog_form)
   

@app.route('/delete-blog/<int:id>/')
def delete_blog(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM blog WHERE blog_id = {}".format(id))
    mysql.connection.commit()
    #flash("Your blog has been deleted", 'success')
    return redirect('/my-blogs')
@app.route('/logout/')
def logout():
    session.clear()
    #flash("You have been logged out", 'info')
    return redirect('/')
    return render_template('logout.html')

if __name__=='__main__':
    app.run()
