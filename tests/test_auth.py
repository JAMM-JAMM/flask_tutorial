import pytest
from flask import g, session
from flaskr.db import get_db

"""
 이 모듈은 flaskr의 auth.py에서 정의한 기능을 테스트하기 위한 목적을 가집니다. 
   
   1. 회원가입 : 성공 조건은 한 개이고, 실패 조건은 여러 개 있습니다. 두 조건을 함수로 나누어 테스트를 진행합니다.
     
     성공조건
     - Username과 Password가 request 객체에 채워져 있고, username이 기존 db에 존재하지 않습니다. 
     
     실패조건
     - Username가 request 객체에 채워져 있어야 합니다.
     - Password가 request 객체에 채워져 있어야 합니다.
     - request 객체로 넘어온 Username과 같은 회원이 있는지 확인합니다.
    
   2. 로그인
     성공조건
      (1) request 객체로 넘어온 username으로 db에 검색했을 때, 결과가 None이 아닙니다.
      (2) (1)에서의 검색 결과에서 도출한 비밀번호와 client가 제출한 비밀번호와 비교한 후 같다면 로그인에 성공합니다.
          
       
   3. 로그인 후 다른 페이지 이동 시, 로그인 상태 유지
     - 세션에 user_id가 존재합니다.
       
   4. 로그아웃
    
   5. 로그인 후에만 사용 가능한 기능을 정의하기 위한 데코레이터
    -> 데코레이터는 기능을 실행 했을 때 테스트 가능하므로, 이 함수는 test_blog.py에서 테스트합니다.  
     - 세션이 빈 상태라면, 이 데코레이터로 지정된 기능을 사용할 수 없습니다. (auth/login 경로로 이동하게 합니다)
     - 세션에 user_id가 존재한다면, 이 데코레이터로 지정된 기능을 사용할 수 있습니다.
"""


def test_register(client, app):
    """
     1. client와 app을 오버라이딩합니다.
     2. 회원가입 버튼을 클릭했을 때 오류 발생이 일어나지 않는지 테스트 합니다
     3. client가 회원가입에 성공적인 조건으로 요청을 보냈을 때, 오류가 없는지 테스트 합니다.
     4. 회원가입에 성공한 뒤, db에 해당 아이디 정보가 들어갔는지 테스트 합니다.
    """
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "select * from user where username = 'a'",
        ).fetchone() is not None


# @pytest.mark.parametrize를 사용하면 여러 개의 케이스를 순차대로 테스트할 수 있습니다.
@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', b'Username is required.'),
        ('a', '', b'Password is required.'),
        ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    """
    1. client를 오버라이딩하고 username, password, message를 인자로 받습니다.
     이 중에서 username, password, message는 @pytest.mark.parametrize에 정의한 데이터로 입력받습니다.

    2. 회원가입에 실패하는 조건으로 데이터를 전송하여 테스트합니다.
     이 때, 예상되는 결과(message)와 매칭되는지 확인합니다.
    """
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


def test_logout(client, auth):
    """
     1. client와 auth를 오버라이딩 합니다.
      - auth를 오버라이딩 한 이유는 로그인 한 후에 테스트를 진행하기 위함입니다.
     2. 로그아웃을 실행시킨 후 세션에 user_id가 남아있는지 테스트 합니다.
    """
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session