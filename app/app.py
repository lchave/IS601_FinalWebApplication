from typing import List, Dict
import os
import simplejson as json
from flask import Flask, request, Response, redirect,session,url_for, flash
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message


app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'moviesData'
mysql.init_app(app)

app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
app.config['MAIL_SENDER'] = os.environ.get('MAIL_SENDER')
mail = Mail(app)

@app.route('/', methods=['GET','POST'])
def index ():
    return render_template("login.html")

@app.route('/index', methods=['GET'])
def index_homepage():
    user = {'username': 'Luis'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblMovieImport')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, movies=result)

@app.route('/login', methods=['POST'])
def index_login ():
    if 'email' in request.form and 'password' in request.form:
        email = request.form ['email']
        password = request.form ['password']
        cursor = mysql.get_db().cursor()
        cursor.execute("SELECT * FROM logininfo WHERE email=%s AND password=%s",(email,password))
        info = cursor.fetchone()
        print(info)
        if info is not None:
            if info ['email'] == email and info ['password'] == password:
                username = info ['name']
                string01 = "{'username': '"
                string02 = "'}"
                user= string01 + username + string02
                return render_template("profile.html",user=user)
        else:
            return render_template("login.html")

@app.route('/new', methods=['GET'])
def form_register_get():
    return render_template('register.html')

@app.route('/new', methods=['POST'])
def form_register_post():
    recipient = request.form['email']
    msg = Message('You have successfully register to the IS 601 - Final Web Application', recipients=[recipient])
    msg.body = ('Congratulations! You have successfully register to the IS 601 - Final Web Application '
                'Regards,'
                'Ricardo Torres & Luis Chavez Saenz')
    msg.html = ('<h1>IS 601 - Final Web Application</h1>'
                '<p>Congratulations! You have successfully register to our final project '
                '<b>IS 601 - Final Web Application</b>! '
                'by '
                '<b>Ricardo Torres & Luis Chavez Saenz</b></p>')
    mail.send(msg)
    flash(f'A registration message was sent to {recipient}.')
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('name'), request.form.get('email'), request.form.get('pass'))
    sql_insert_query = """INSERT INTO logininfo (name, email, password) VALUES (%s,%s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/charts', methods=['GET'])
def charts_view():
    user = {'username': 'Luis'}
    legend = '# of Movies per Decade'
    labels = ['1960s or prior', '1970s', '1980s', '1990s', '2000s', '2010s or later']
    values = []
    cursor = mysql.get_db().cursor()
    queries = ['SELECT * FROM tblMovieImport t WHERE t.Year < 1970','SELECT * FROM tblMovieImport t WHERE t.Year >= 1970  AND t.Year< 1980','SELECT * FROM tblMovieImport t WHERE t.Year >= 1980  AND t.Year< 1990','SELECT * FROM tblMovieImport t WHERE t.Year >= 1990  AND t.Year< 2000','SELECT * FROM tblMovieImport t WHERE t.Year >= 2000  AND t.Year< 2010','SELECT * FROM tblMovieImport t WHERE t.Year >= 2010']
    for query in queries:
        cursor.execute(query)
        values.append(cursor.rowcount)
    rating_legend = 'Chronological Movie Ratings'
    rating_labels = []
    cursor.execute('SELECT Year FROM tblMovieImport ORDER BY Year ASC')
    for year in cursor.fetchall():
        rating_labels.append(list(year.values())[0])
    rating_values = []
    cursor.execute('SELECT Score FROM tblMovieImport ORDER BY Year ASC')
    for rating in cursor.fetchall():
        rating_values.append(list(rating.values())[0])
    cursor.execute('SELECT * FROM tblMovieImport ORDER BY Score DESC LIMIT 10')
    result = cursor.fetchall()
    return render_template('charts.html', title='Home', user=user, movies=result, labels=labels, legend=legend, values=values, rating_labels=rating_labels, rating_legend=rating_legend, rating_values=rating_values)

@app.route('/view/<int:movie_id>', methods=['GET'])
def record_view(movie_id):
    user = {'username': 'Luis'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblMovieImport WHERE id=%s', movie_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', user=user, movie=result[0])

@app.route('/edit/<int:movie_id>', methods=['GET'])
def form_edit_get(movie_id):
    user = {'username': 'Luis'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblMovieImport WHERE id=%s', movie_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', user=user, movie=result[0])

@app.route('/edit/<int:movie_id>', methods=['POST'])
def form_update_post(movie_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Year'), request.form.get('Score'), request.form.get('Title'), movie_id)
    sql_update_query = """UPDATE tblMovieImport t SET t.Year = %s, t.Score = %s, t.Title = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/index", code=302)

@app.route('/movies/new', methods=['GET'])
def form_insert_get():
    user = {'username': 'Luis'}
    return render_template('new.html', title='New Movie Form', user=user)

@app.route('/movies/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Year'), request.form.get('Score'), request.form.get('Title'))
    sql_insert_query = """INSERT INTO tblMovieImport (Year,Score,Title) VALUES (%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/index", code=302)

@app.route('/delete/<int:movie_id>', methods=['POST'])
def form_delete_post(movie_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblMovieImport WHERE id = %s """
    cursor.execute(sql_delete_query, movie_id)
    mysql.get_db().commit()
    return redirect("/index", code=302)

@app.route('/api/v1/movies', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblMovieImport')
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/movies/<int:movie_id>', methods=['GET'])
def api_retrieve(movie_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblMovieImport WHERE id=%s', movie_id)
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/movies/<int:movie_id>', methods=['PUT'])
def api_edit(movie_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['Title'], content['Year'], content['Score'],movie_id)
    sql_update_query = """UPDATE tblMovieImport t SET t.Title = %s, t.Year = %s, t.Score = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/movies/', methods=['POST'])
def api_add() -> str:
    content = request.json
    cursor = mysql.get_db().cursor()
    inputData = (content['Title'], content['Year'], content['Score'])
    sql_insert_query = """INSERT INTO tblMovieImport (Title,Year,Score) VALUES (%s,%s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp

@app.route('/api/v1/movies/<int:movie_id>', methods=['DELETE'])
def api_delete(movie_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblMovieImport WHERE id = %s """
    cursor.execute(sql_delete_query, movie_id)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)