# 블로그 블루프린트

# 블로그 블루프린트를 만들기 위해 사용자 인증 섹션에서 사용한 것과 동일한 기술을 이용한다.
# 블로그는 전체 포스트 목록 화면을, 그리고 로그인한 유저를 위해 포스트 작성/수정/삭제 화면을 제공한다.

# 각 화면을 만드는 동안 개발 서버는 운영(running) 상태로 유지하여, 코드를 하나씩 수정해가면서
# 브라우저를 통해 각각의 URL에 대한 접속 테스트를 진행한다.

# 튜토리얼 진행순서
# 1. 블루프린트 생성: 블루프린트 객체 생성 (blog.py) -> 블루프린트 객체 등록 (__init__.py)
# 2. Read: 글 보여주기 코드 (blog.py) -> 글 보여주기 탬플릿 (/template/blog/index.html)
# 3. Create: 글 작성 코드 (blog.py) -> 글 작성 탬플릿 (/template/blog/create.html)
# 4. Update, Delete: 글 수정 가능여부 식별 코드 (blog.py) -> 글 수정 코드 (blog.py), 글 삭제 코드 (blog.py) -> 글 수정 탬플릿 (/template/blog/update.html)

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash

from flaskr.auth import login_required
from flaskr.db import get_db

# 1. 블루프린트 생셩: 블루프린트 객체 생성 (blog.py)

# Blueprint 함수에 prefix 인자를 넣지 않는다.
# 따라서 prefix는 None이 된다.
bp = Blueprint('blog', __name__)

# 2. Read

# 글 보여주기 코드 (blog.py)
# 인덱스 (디폴트 뷰)
# 인덱스는 메인 페이지로 전체 포스트 목록을 최신 글부터 보여줍니다.
# 해당 페이지에서 DB에 있는 사용자가 작성한 글을 모두 보여줍니다.
# 글에는 '글 번호 / 글 제목 / 글 내용 / 작성 시각 / 작성자 id / 작성자 닉네임'이 포함됩니다.
# 포스트 목록과 작성자를 함께 표시하기 위해 SQL 문을 이용해서 DB에서 목록을 불러올 때 JOIN을 이용한다.
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username FROM post p JOIN user u ON p.author_id = u.id ORDER BY created DESC'
    ).fetchall()

    # render_template의 두 번째 인자는 **context이다.
    # jinja2에는 전달할 변수명을 짓고, 해당 변수에 데이터를 저장한다. (변수명: posts)
    # jinja2에서는 {{ posts }} 와 같이 해당 변수명을 입력하여 읽어낼 수 있다.
    return render_template('blog/index.html', posts=posts)

# 3. Create

# 글 작성 코드 (blog.py)

# create 뷰는 사용자 등록을 위한 register 뷰와 동일하게 작동한다.
# 새 글을 입력할 폼을 표시하고, 입력된 정보의 유효성 체크를 하며, DB에 저장하는 기능이다.
# @login_required 데코레이터는 로그인된 사용자인지 체크하며, 로그인된 사용자가 아니라면 로그인 페이지로 보낸다.
@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # 로그인한 사용자가 글을 작성할 때, 사용되는 함수이다.
    # 1. 로그인을 검증하기 위해 login_required 데코레이터를 사용했다.
    # 2. 글을 제출할 때, 제목을 달지 않았으면, flash 오류를 발생시키고 글 작성 페이지로 다시 이동한다.
    # 3. 정상적으로 글이 작성되었다면, 메인 페이지로 이동한다.
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)', (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template('blog/create.html')

# 4. Update, Delete

# 글 수정 가능여부 식별 코드
# update와 delete 뷰는 id 정보를 함께 표출한다.
# 코드를 중복해서 작성하지 않도록 get_post 함수로 작성해서 각각의 뷰에서 불러와 사용한다.
# check_author 인자는 익명 글을 허용할 지에 대한 부분이다.
def get_post(id, check_author=True):
    
    # 글의 작성자가 글 수정 또는 삭제 버튼을 눌렀을 때, 유효성을 식별하기 위해 사용되는 코드이다.
    # 이 함수에서는 두 가지를 식별한다.
    # 1. 글이 존재하는지?
    # 2. 로그인한 유저의 id와 글의 작성자가 같은 사람인지?
    # 만약 유효성 식별에서 적합하지 않다면, 페이지에 오류 메세지를 전달한다.
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username FROM post p JOIN user u ON p.author_id = u.id WHERE p.id = ?', (id,)
    ).fetchone()

    # abort()는 미리 정의된 예외상황에 따른 HTTP 코드 값을 반환한다.
    # 이 코드에서 사용된 404는 'Not Found', 403은 'Forbidden'을 의미한다.
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post

# 글 수정 코드 (blog.py)

# 지금까지 만들어온 뷰와 다르게 update 함수는 id라는 인자 값을 받아온다.
# 이 인자는 경로 값에 있는 <int:id> 값을 사용한다.
# 실제 URL을 보면, 1/update 와 같이 되어있는 것을 확인할 수 있다.
# Flask는 경로에 1 값을 가져와 이 값이 int인지 확인하고 id 인자로 넘겨준다.
# 만약 int: 를 표시하지 않고 <id> 처럼 쓰게되면, 이 값은 문자로 처리된다.
@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):

    # 1. 로그인을 검증하기 위해 login_required 데코레이터를 사용했다.
    # 2. get_post() 함수를 통해 수정이 가능한 글인지에 대한 유효성 검사를 한다.
    #   - 가능하다면, 글에 대한 정보를 post 변수에 저장한다.
    #   - 가능하지 않다면, get_post 함수 내부의 abort를 통해서 사용자 페이지에 오류를 전달한다.
    # 3. 글 제목이 존재하지 않으면, 글 수정 페이지로 돌아가서 에러 메시지를 나타낸다.
    #   - 수정 요청 때 받은 내용이 request 객체에 남아있다.
    #   - 또한, request에 담긴 데이터는 ImmutableMultiDict([]) 객체를 통해서 저장이 되는데,
    #     이는 같은 모듈(blog.py)에서라도 다른 함수에서는 초기화되는 성질이 있다.
    #   - 따라서 update 함수 내에서 update.html을 랜더링하면, 
    #     "유저가 작성 중이던 글"을 웹 페이지로 전달받을 수 있다.
    #   - 반면에, 다른 함수에서 html 파일을 랜더링하면 request 객체를 초기화하여 웹 페이지로 전달할 수 있다.
    # 4. 글 제목이 존재한다면, 사용자가 작성한 내용으로 글을 수정한다.
    #   - redirect 함수를 통해 index 함수에서 index.html이 랜더링 된다.
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                'WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post = post)

# 글 삭제 코드 (blog.py)

# 삭제 뷰는 별도의 탬플릿이 없고, 버튼도 update.html의 일부분으로 포함되어 /<id>/delete URL로 연결된다.
# 별도의 탬플릿이 없기 때문에 데이터를 넘겨주는 부분과 인덱스로 화면을 전환하는 부분만 처리한다.
@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    
    # 1. 로그인을 검증하기 위해 login_required 데코레이터를 사용했다.
    # 2. get_post() 를 통해 삭제가 가능한 글인지에 대해서 유효성을 검사한다.
    #   - 가능하다면, 글에 대한 정보를 post 변수에 저장한다.
    #   - 가능하지 않다면, get_post() 함수 내부의 abort를 통해서 사용자 페이지에 오류가 전달된다.
    # 3. 해당 글을 삭제하고 메인 페이지로 이동한다.
    get_post(id)
    db = get_db()
    db.execute(
        'DELETE FROM post WHERE id = ?', (id,)
    )
    db.commit()
    return redirect(url_for('blog.index'))