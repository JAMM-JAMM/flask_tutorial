# 블루프린트(Blueprint)와 뷰(View)
# 뷰(view)는 사용자의 요청(request)에 대응(respond)할 화면을 의미한다.
# Flask는 사용자의 URL 요청(request)이 들어오면 패턴 매칭 방법을 이용해서
# 특정 뷰에 연결시키고, 뷰는 이에 상응하는 화면을 만들어낸다.

# 블루프린트 만들기

# 블루프린트란 연관있는 여러 개의 뷰를 그룹으로 묶어서 처리하는 방법을 말한다.
# 각각의 뷰를 앱에 직접 등록하는 대신 블루프린트에 등록하고, 이 블루프린트를 앱에 등록시킨다.
# 예를 들어서, 로그인과 관련된 코드와 뷰는 모두 하나의 블루프린트 안에서 작성된다.
# 따라서 블루프린트는 모두 같은 url_prefix를 갖는다.

# Flaskr 프로젝트에는 2개의 블루프린트가 있다. 하나는 사용자 인증 기능이고
# 다른 하나는 블로그 게시물 관련 기능이다.
# 각 블루프린트에 해당하는 코드는 각각 별도의 모듈로 관리된다.

# 튜토리얼 작업순서
# 1. 블루프린트 객체 생성 (auth.py)
# 2. 블루프린트 등록 (__init__.py)
# 3. 회원가입 코드 (auth.py)
# 4. 로그인 코드 (auth.py)
# 5. 로그인 한 유저화면 불러오기 (auth.py)
# 6. 로그아웃 코드 (auth.py)
# 7. 로그인 한 유저의 다른 화면을 위한 조건 (auth.py)

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import generate_password_hash, check_password_hash

from flaskr.db import get_db

# 1. 블루프린트 객체 생성 (auth.py)
# 이 코드는 'auth'라는 이름의 블루프린트를 생성한다.
# 앱의 오브젝트처럼 블루프린트 역시 위치를 지정해줘야 한다.
# 이를 위해 두 번째 인자로 __name__을 전달한다.
# url_prefix는 이 블루프린트에 속한 페이지 전체의 URL 앞단에 붙을 주소이다.
# 즉, __name__으로 받아오는 url 앞에 무조건 '/auth'를 붙여라 라는 뜻
bp = Blueprint('auth', __name__, url_prefix='/auth')

# 이후 __init__.py에서 블루프린트 등록을 해준다.

# 3. 회원가입 코드 (auth.py)
# 웹 사이트 방문자가 /auth/register라는 URL에 접속하면 register 뷰가 html 코드를 보여준다.
# 방문자가 화면에서 요구하는 양식을 채워서 회원가입을 하면, html 페이지는 채워진 정보에 대한 적합성을 체크한 후
# 신규 사용자를 등록하고 로그인 페이지로 보내준다.

# @bp.route() 는 /register라는 URL 요청(request)이 들어오면
# register 뷰로 연결해준다.
# Flask는 /auth/register URL 요청이 들어오면 하단의 register 함수를 실행하고 결과를 반환한다.
@bp.route('/register', methods=['GET', 'POST'])
def register():

    # 사용자가 내용을 입력하고 submit 버튼을 누르면, request.method가 지정한대로
    # 데이터는 'POST' 방식으로 전달된다.
    if request.method == 'POST':

        # request.form은 딕셔너리 형태로 작성되어 'key'와 'value' 형태로 저장된다.
        # 사용자는 username과 password를 입력한다.
        username = request.form['username']
        password = request.form['password']

        # db.py에서 작성한 함수다. 데이터 베이스를 불러온다.
        db = get_db()

        # 에러메세지 초기화
        error = None

        # username과 password가 공백이 아닌지 체크한다.
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # username 중복 체크를 위해서 db에 쿼리를 전송한다.
        # 이 때, db.execute()를 통해 전달되는 쿼리에 물음표는 변수 값을 전달하기 위한 placeholder이다.
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
        
        # 중복체크까지 성공했다면 신규 사용자 정보를 DB에 저장한다.
        # 보안을 위해 암호는 DB에 바로 저장하지 않고, generate_password_hash()를 이용하여 암호화 한 후 저장한다.
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)', (username, generate_password_hash(password))
            )
            # 데이터를 저장한 후, db.commit()을 이용해 DB의 데이터를 변경하였음을 확정한다.
            db.commit()

            # url_for의 인자로 주어진 auth 모듈의 login 함수의 블루프린트 url_prefix를 포함한
            # '/auth/login' url 엔드포인트를 생성한다.
            # redirect는 인자로 주어진 url을 받아서, 해당 url을 다루는 함수로 이동한다.
            return redirect(url_for('auth.login'))
        
        # error 메시지가 None이 아닌 경우, (신규 사용자 등록에 실패한 경우)
        # flash()를 통해 에러메시지를 전달한다.
        flash(error)
    
    # render_template()는 인자로 주어진 html 파일을 랜더링한다.
    # 사용자가 직접 auth/register에 접근하거나, 신규 사용자 등록에 실패한 경우
    # 에러가 발생하면 사용자 등록 화면이 표시된다.
    return render_template('auth/register.html')

# 4. 회원가입 코드 (auth.py)

# login 뷰 까지 가는 방법은 위에서 설명한 register 뷰와 동일한 패턴매칭 방법을 이용한다.

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # 사용자 정보는 쿼리를 통해 가져오고, 추후 사용을 위해 변수 값에 저장한다.
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        
        # check_password_hash()를 이용해서 비밀번호를 암호화하고, DB에 저장된 값과 비교한다.
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        # 사용자 인증이 완료되면 사용자 정보는 세션에 저장한다.
        # 세션은 딕셔너리 형태로 되어있다.
        # 세션은 로그인에 성공한 유저가 다른 페이지에서도 로그인 상태를 유지하기 위해 사용된다.
        # 즉, 세션에 저장된 id는 후속 request에서 재사용이 가능하다.
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
        
    return render_template('auth/login.html')

# 5. 로그인 한 유저화면 불러오기 (auth.py)

# bp.before_app_request() 함수는 모든 사용자들에게 뷰를 보여주기 전에 거쳐지는 함수이다.
# 이 함수를 이용해 각 뷰 함수가 실행되기 전에 실행할 함수를 생성한다.
# 사용자가 호출하는 URL이 무엇이든 load_logged_in_user()가 먼저 실행되도록 설정한다.
# load_logged_in_user()은 세션에 저장되어 있는 사용자 user_id를 가져오고, 이를 g.user에 저장한다.
@bp.before_app_request
def load_logged_in_user():
    
    # 세션에 사용자의 아이디가 저장되어 있다면, DB에 저장된 사용자의 기록을 불러온다.
    user_id = session.get('user_id')

    # 유저에 대한 기록이 있다면, g.user에 DB에 기록된 정보를 저장한다.
    if user_id is None:
        g.user = None
    
    # 유저에 대한 기록이 없다면, g.user에 None을 저장한다.
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()

# 6. 로그아웃 코드 (auth.py)

# 로그아웃은 user_id를 세션에서 지우면 된다. 이후에는 load_logged_in_user에서 user_id가 더 이상 조회되지 않는다.
# 사용자가 /auth/logout을 요청하면, 로그아웃 시킨다. (세션 초기화)
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# 7. 로그인 한 유저의 다른화면을 위한 조건 (auth.py)
# 블로그에서 글을 작성하거나, 수정, 삭제를 위해 사용자 정보가 필요하다. 
# 각각의 기능에서 이를 수행하기 위해 사용자 정보를 체크해야 하는데 데코레이터를 이용해 할 수 있다.

# login_required() 는 데코레이터로 사용되며, 로그인 후 이용할 수 있는 기능에 대한 식별 함수이다.
# 이 데코레이터는 데코레이터를 호출하는 모든 함수의 밖에서 실행된다. 주 기능은 user가 로그인 되었는지 확인하고,
# 그렇지 않다면 로그인 화면으로 보내주는 기능이다.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view