from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fkBJ2eCwZaN4NJC4'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(360))
    body = db.Column(db.String(9999))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/')
        else:
            flash('User does not exist or password is incorrect.', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''
        space = ' '

        #make sure username doesn't already exist, pass in error if it does.
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            username_error = "Username already exists, please choose a new one."
            password = ''
            verify = ''

        #validate username
        if len(username) < 3 or len(username) > 20 or username.count(space) != 0:
            username_error = 'Please enter a valid username (3-20 characters, no spaces).'
            password = ''
            verify = ''

        #validate password
        if len(password) < 3 or len(password) >20 or password.count(space) != 0:
            password_error = "Please enter a valid password (3-20 characters, no spaces)."
            password = ''
            verify = ''
        
        #validate verify
        if verify != password:
            verify_error = "Password verification must match."
            password = ''
            verify = ''

        #if no errors, create new user and log them in
        if not username_error and not password_error and not verify_error:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("Account created!")
            return redirect('/')
        
        #if there is an error, re-render the template with relevant error messages.
        else:
            flash("Account could not be created, see error message below.", 'error')
            return render_template('register.html', 
                title="Register an Account on Blogz!",
                username=username, username_error=username_error,
                password=password, password_error=password_error,
                verify=verify, verify_error=verify_error)
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['username']
    flash("Logged out!")
    return redirect('/')


@app.route('/')
def index():
    blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog!", blogs=blogs)

@app.route('/blog', methods=['POST', 'GET'])
def show_blog():
    
    if request.args:
        blog_id = request.args.get('id')
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('single_post.html', blogs=blogs)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog!", blogs=blogs)

    
@app.route('/newpost', methods=['POST', 'GET'])
def create_new_post():
    if request.method == 'GET':
        return render_template('new_post.html', title="New Blog Entry")

    author = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog = Blog(blog_title, blog_body, author)

        title_error = ''
        body_error = ''

        if len(blog_title) == 0:
            title_error = "Please enter a title for your new post."
        if len(blog_body) == 0:
            body_error = "Please enter text for your new post."

        if not title_error and not body_error:
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog.id))
        
        else:
            blogs = Blog.query.all()
            return render_template('new_post.html', title="Build a Blog!", blogs=blogs,
                blog_title=blog_title, title_error=title_error, 
                blog_body=blog_body, body_error=body_error)

if __name__ == '__main__':
    app.run()
