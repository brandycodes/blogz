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
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('Logged in')
            return redirect('/')
        else:
            flash('User does not exist or password is incorrect.', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #TODO - validate user's data
    
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email,password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            #TODO - user better response messaging
            return "<h1>Duplicate user</h1>"
    
    return render_template('register.html')

@app.route('/logout')
def logoout():
    del session['email'] 
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

    author = User.query.filter_by(email=session['email']).first()

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
