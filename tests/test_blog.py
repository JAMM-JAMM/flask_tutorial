import pytest
from flaskr.db import get_db
from flask import session

"""
 이 모듈은 flaskr의 blog.py에서 정의한 기능을 테스트하기 위한 목적을 가집니다. 
  - 메인 페이지의 레이아웃을 확인합니다.
  - 로그인 후 이뤄질 수 있는 기능을 테스트 합니다.
  - 글의 작성자만 가능한 기능을 테스트 합니다.
  - 글의 작성자가 해당 글을 수정/삭제를 위해 글이 존재하는지 테스트 합니다.
  - 글 작성 기능을 테스트 합니다.
  - 글 수정 기능을 테스트 합니다.
  - 글 삭제 기능을 테스트 합니다.
"""


def test_index(client, auth):
    """
    메인 페이지의 레이아웃을 확인합니다.
     1. client와 auth를 오버라이딩 합니다.

     2. 로그인 전과 로그인 한 후, '메인 페이지' 변화를 확인합니다.
      로그인 전
      - 로그인 버튼과 회원가입 버튼이 존재합니다.

      로그인 후
      - 로그아웃 버튼이 존재합니다.
      - client의 아이디가 존재합니다.
      - client가 작성한 글의 제목과 날짜가 존재합니다.
      - clinet가 작성한 글의 본문이 존재합니다.
      - clinet가 작성한 글에 수정 버튼이 존재합니다.
    """

    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
        '/create',
        '/1/update',
        '/1/delete',
))
def test_login_required(client, path):
    """
    로그인 후 이뤄질 수 있는 기능을 테스트 합니다.
     1. client를 오버라이딩 하고 다양한 테스트 케이스를 path 인자로 넘겨 받습니다.
     2. client가 글쓰기/수정/삭제를 눌렀을 때 로그인 페이지로 이동되는지 확인합니다.
    """

    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_author_required(app, client, auth):
    """
    글의 작성자만 가능한 기능을 테스트 합니다.
     1. app과 client, auth를 오버라이딩 합니다.
     2. 테스트를 위해 client가 작성한 글을 다른 사용자가 작성한 것으로 수정한 후 저장합니다.
     3. client가 로그인 하도록 한 후, 수정과 삭제를 시도합니다. 403 오류가 나온다면 테스트 통과입니다.
     4. 현재 client는 메인 페이지에서 수정 버튼을 볼 수 없습니다.
    """

    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
        '/2/update',
        '/2/delete',
))
def test_exists_required(client, auth, path):
    """
    글의 작성자가 해당 글을 수정/삭제를 위해 글이 존재하는지 테스트 합니다.
     1. client, auth, path를 오버라이딩 합니다.
     2. client가 로그인 한 후, 존재하지 않는 글에 수정/삭제 경로에 접근합니다.
    """

    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    """
      글 작성 기능을 테스트 합니다.

      1. client가 로그인 한 후 글 작성 버튼을 눌렀을 때 정상적으로 출력되는지 확인합니다.
      2. client 글 작성이 가능한 조건에 맞추어 제출했을 때 정상적으로 글이 작성됐는지 확인합니다.
       - 기존 DB에는 한 개의 글이 있었습니다. 따라서 성공적으로 글이 제출 됐다면, DB에는 두 개의 글이 존재해야 합니다.  
    """
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    """
      글 수정 기능을 테스트 합니다.
      1. client가 로그인 한 후 글 수정 버튼을 눌렀을 때 정상적으로 출력되는지 확인합니다.
      2. 1번 게시글의 제목을 수정한 뒤, 정상적으로 수정이 이뤄졌는지 확인합니다.  
    """
    
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


def test_delete(client, auth, app):
    """
      글 삭제 기능을 테스트 합니다.
      1. client가 로그인 한 후 글 삭제 버튼을 눌렀을 때 메인 페이지로 이동되는지 테스트 합니다.
      2. 글 삭제가 이뤄진 뒤, 1번 게시글이 남아있는지 테스트 합니다. 
    """

    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None