from flask import Flask, render_template, abort, jsonify, request, redirect, url_for, flash, session
from models import setup_db, Grade, Semester, Module, MCQ
from flask_cors import CORS
from forms import GradeForm, SemesterForm, ModuleForm, MCQForm
import sys
from functools import wraps
import json
# from auth import AuthError, requires_auth
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode


app = Flask(__name__)
db = setup_db(app)
oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id='a3y7iLQNxrQT0pWbHPubMeCZ54spTRJW',
    client_secret='YH517B-qeU54GU6hSxVg1uGbqJsDxT0s9qWTD90pHsHKavPwTefBJwTg9AxcXm2O',
    api_base_url='https://bmclp.auth0.com',
    access_token_url='https://bmclp.auth0.com/oauth/token',
    authorize_url='https://bmclp.auth0.com/authorize',
    # audience='Coffee',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

CORS(app, resources={r"/api/*": {"origins": "*"}})


MCQS_PER_PAGE = 10
accessable_users = ['krvhrv188', 'saj99h']

@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers",
        "Content-Type, Authorization")
    response.headers.add(
        "Access-Control-Allow-Methods",
        "GET, POST, PUT, PATCH, OPTIONS")
    return response

def paginate_mcqs(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * MCQS_PER_PAGE
    end = start + MCQS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

@app.route('/')
def index():
    if 'profile' not in session:
        return render_template('pages/home.html')
    return render_template('pages/home.html', userinfo=session['profile'])

@app.route('/about')
def about():
    if 'profile' not in session:
        return render_template('pages/about.html')
    return render_template('pages/about.html', userinfo=session['profile'])


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='https://mcq.bmclearn.com/callback')

@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'nickname': userinfo['nickname'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    print(session.values())
    return redirect('/dashboard')


def requires_auth(users=[]):
    def requires_auth_decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'profile' not in session:
            # Redirect to Login page here
                return redirect('/')
            if session['profile']['nickname'] not in users:
                return abort(405)
            return f(*args, **kwargs)

        return decorated
    return requires_auth_decorator

@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('about', _external=True), 'client_id': 'a3y7iLQNxrQT0pWbHPubMeCZ54spTRJW'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@app.route('/dashboard')
@requires_auth(accessable_users)
def dashboard():
    return render_template('pages/home.html', userinfo=session['profile'])

## Grades ##

@app.route('/grades')
def grade():
    query = Grade.query.all()
    if 'profile' not in session:
        return render_template('pages/grades.html', data=query)
    return render_template('pages/grades.html', data=query, userinfo=session['profile'])

@app.route('/grades/add', methods=['GET'])
@requires_auth(accessable_users)
def add_grade_form():
    form = GradeForm()
    return render_template('forms/new_adds.html', form=form, userinfo=session['profile'])

@app.route('/grades/add', methods=['POST'])
@requires_auth(accessable_users)
def add_grade_submission():
    try:
        new_grade = Grade(
            num=request.form['num']
        )
        print(new_grade)
        Grade.insert(new_grade)
        flash('Grade ' + request.form['num'] + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Grade ' + request.form['num'] + ' could not be listed.')
    finally:
        db.session.close()
    query = Grade.query.all()
    return render_template('pages/grades.html', data=query, userinfo=session['profile'])

## /Grades ##

## Semesters ##

@app.route('/grades/<int:grade_id>')
def semester(grade_id):
    query = Semester.query.filter_by(grade_id=grade_id).all()
    if 'profile' not in session:
        return render_template('pages/semesters.html', data=query)
    return render_template('pages/semesters.html', data=query, userinfo=session['profile'])
  
@app.route('/semesters/add', methods=["GET"])
@requires_auth(accessable_users)
def add_semester_form():
    form = SemesterForm()
    grades = Grade.query.order_by(Grade.id).all()
    return render_template('forms/new_adds.html', form=form, grades=grades, userinfo=session['profile'])

@app.route('/semesters/add', methods=["POST"])
@requires_auth(accessable_users)
def add_semester_submission():
    try:
        grade_id=request.form['grade_id']
        new_semester = Semester(
            num=request.form['num'],
            grade_id=grade_id
        )
        Semester.insert(new_semester)
        flash('Semester ' + request.form['num'] + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Semester ' + request.form['num'] + ' could not be listed.')
    finally:
        db.session.close()
    query = Semester.query.filter_by(grade_id=grade_id).all()
    return render_template('pages/semesters.html', data=query, userinfo=session['profile'])
  
## /Semeseters ##

## Modules ##

@app.route('/grades/<int:grade_id>/<int:semester_id>')
def module(grade_id, semester_id):
    query = Module.query.filter(Module.grade_id==grade_id, Module.semester_id==semester_id)
    if 'profile' not in session:
        return render_template('pages/modules.html', data=query)
    return render_template('pages/modules.html', data=query, userinfo=session['profile'])

@app.route('/modules/add', methods=["GET"])
@requires_auth(accessable_users)
def add_module_form():
    form = ModuleForm()
    
    grades = Grade.query.order_by(Grade.id).all()

    return render_template('forms/new_adds.html', form=form, grades=grades, userinfo=session['profile'])

@app.route('/modules/add', methods=["POST"])
@requires_auth(accessable_users)
def add_module_submission():
    try:
        grade_id=request.form['grade_id']
        semester_id = request.form['semester_id']
        new_module = Module(
            name=request.form['name'],
            grade_id=grade_id,
            semester_id=semester_id
        )
        Module.insert(new_module)
        flash('Module ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Module ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    query = Module.query.filter(Module.grade_id==grade_id, Module.semester_id==semester_id)
    return render_template('pages/modules.html', data=query, userinfo=session['profile'])

@app.route('/modules/<int:module_id>/edit', methods=["GET"])
@requires_auth(accessable_users)
def edit_module_form(module_id):
    form = ModuleForm()
    module_query = Module.query.get(module_id)
    module_details = Module.format(module_query)
    form.name.data = module_details['name']
    form.grade_id.data = module_details['grade_id']
    form.semester_id.data = module_details['semester_id']
    
    grades = Grade.query.order_by(Grade.id).all()
    
    return render_template('forms/edit_adds.html', form=form, grades=grades, module_id=module_id, userinfo=session['profile'])

@app.route('/modules/<int:module_id>/edit', methods=["POST"])
@requires_auth(accessable_users)
def edit_module_submission(module_id):
    try:
        module_data = Module.query.get(module_id)
        setattr(module_data, 'name', request.form['name'])
        setattr(module_data, 'grade_id', request.form['grade_id'])
        setattr(module_data, 'semester_id', request.form['semester_id'])
        Module.update(module_data)
        flash('Module ' + request.form['name'] + ' was successfully edited!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Module ' + request.form['name'] + ' could not be edit.')
    finally:
        db.session.close()
    
    query = Module.query.filter(Module.grade_id==request.form['grade_id'], Module.semester_id==request.form['semester_id'])
    return render_template('pages/modules.html', data=query, userinfo=session['profile'])

@app.route('/modules/<int:module_id>', methods=['DELETE'])
@requires_auth(accessable_users)
def delete_module(module_id):
    try:
        Module.query.filter_by(id=module_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        
## /Modules ##

## MCQS ##

@app.route('/modules/<int:module_id>/mcqs')
def mcq(module_id):
    page = request.args.get('page', 1, type=int)
    query = MCQ.query.filter_by(module_id=module_id).order_by(MCQ.id).paginate(page=page, per_page=MCQS_PER_PAGE)
    if 'profile' not in session:
        return render_template('pages/mcqs.html', data=query)
    return render_template('pages/mcqs.html', data=query, userinfo=session['profile'])

@app.route('/mcqs/add', methods=["GET"])
@requires_auth(accessable_users)
def add_mcq_form():
    form = MCQForm()
    modules = Module.query.order_by(Module.id).all()
    
    return render_template('forms/new_mcq.html', form=form, modules=modules, userinfo=session['profile'])

@app.route('/mcqs/add', methods=["POST"])
@requires_auth(accessable_users)
def add_mcq_submission():
    try:
        choice_E = None
        if 'choice_E' in request.form:
            choice_E = request.form['choice_E'] 
        module_id=request.form['module_id']
        new_mcq = MCQ(
            question=request.form['question'],
            choice_A=request.form['choice_A'],
            choice_B=request.form['choice_B'],
            choice_C=request.form['choice_C'],
            choice_D=request.form['choice_D'],
            choice_E=choice_E,
            answer=str(request.form['answer']).capitalize(),
            module_id=module_id
        )
        MCQ.insert(new_mcq)
        flash('MCQ ' + request.form['question'] + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. MCQ ' + request.form['question'] + ' could not be listed.')
    finally:
        db.session.close()
    page = request.args.get('page', 1, type=int)
    mcqs = MCQ.query.filter_by(module_id=module_id).order_by(MCQ.id).paginate(page=page, per_page=MCQS_PER_PAGE)
    return render_template('pages/mcqs.html', data=mcqs, userinfo=session['profile'])

@app.route('/mcqs/<int:mcq_id>/edit', methods=["GET"])
# @requires_auth(accessable_users)
def edit_mcq_form(mcq_id):
    form = MCQForm()
    mcq_query = MCQ.query.get(mcq_id)
    mcq_details = MCQ.format(mcq_query)
    form.question.data = mcq_details['question']
    form.choice_A.data = mcq_details['choice_A']
    form.choice_B.data = mcq_details['choice_B']
    form.choice_C.data = mcq_details['choice_C']
    form.choice_D.data = mcq_details['choice_D']
    form.choice_E.data = mcq_details['choice_E']
    form.answer.data = mcq_details['answer']
    form.module_id.data = mcq_details['module_id']
    modules = Module.query.order_by(Module.id).all()
    
    return render_template('forms/edit_mcq.html', form=form, modules=modules, mcq_id=mcq_id, userinfo=session['profile'])

@app.route('/mcqs/<int:mcq_id>/edit', methods=["POST"])
# @requires_auth(accessable_users)
def edit_mcq_submission(mcq_id):
    try:
        page = request.args.get('page', 1, type=int)
        mcq_data = MCQ.query.get(mcq_id)
        choice_E = None
        if 'choice_E' in request.form:
            choice_E = request.form['choice_E'] 
        module_id=request.form['module_id']
        setattr(mcq_data, 'question', request.form['question'])
        setattr(mcq_data, 'choice_A', request.form['choice_A'])
        setattr(mcq_data, 'choice_B', request.form['choice_B'])
        setattr(mcq_data, 'choice_C', request.form['choice_C'])
        setattr(mcq_data, 'choice_D', request.form['choice_D'])
        setattr(mcq_data, 'choice_E', choice_E)
        setattr(mcq_data, 'answer', request.form['answer'])
        setattr(mcq_data, 'module_id', module_id)
        MCQ.update(mcq_data)
        flash('MCQ ' + request.form['question'] + ' was successfully edited!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. MCQ ' + request.form['question'] + ' could not be edit.')
    finally:
        db.session.close()
    mcqs = MCQ.query.filter_by(module_id=module_id).order_by(MCQ.id).paginate(page=page, per_page=MCQS_PER_PAGE)
    return render_template('pages/mcqs.html', data=mcqs, userinfo=session['profile'])

@app.route('/mcqs/<int:mcq_id>', methods=['DELETE'])
@requires_auth(accessable_users)
def delete_mcq(mcq_id):
    try:
        MCQ.query.filter_by(id=mcq_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

## /MCQS ##
app.debug=True
app.run(host='192.168.1.13', port=80)