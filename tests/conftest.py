import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

"""
 이 모듈은 fixture라고 불리는 setup 함수로 구성되어 있습니다.
 fixture는 pytest 라이브러리의 데코레이터에 의해 표현됩니다.
 
 이 모듈은 flaskr의 기능을 테스트하기 위한 환경 구축을 목적으로 합니다.
  1. 데이터베이스의 user와 post 테이블에 테스트로 사용할 데이터 입력
  2. 가상 유저 만들기 
  3. CLI 테스트를 위한 환경 구축 
"""

# __file__ : 현재 파일의 위치를 절대경로로 표시
# os.path.dirname() : 인자로 입력된 절대경로에서 마지막 폴더 위치를 표현
# os.path.join() : 경로와 파일명을 인자로 받아서 하나의 경로를 만듦
# open() : 파일을 열음. rb는 읽기/바이너리 형식으로 파일을 연다는 것을 뜻함.

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():

    """
    1. 어플리케이션 팩토리(create_app)를 테스트 모드로 전환 시킵니다.
     - 테스트가 이뤄지는 동안 사용되는 데이터베이스는 db_path로 지정합니다.
     해당 데이터베이스는 임시적으로 사용하는 파일이므로, 테스트가 종료되면 삭제됩니다.

    2. 테스트로 사용할 클라이언트를 만듭니다.
     - client 함수를 통해 뷰로 request을 보낸 뒤, response를 통해 버그를 확인할 수 있습니다.

    3. cli 커맨드를 테스트하기 위해 runner 함수를 만듭니다.
    """

    # tempfile.mkstemp()을 사용하면 일시적으로 파일을 만들고, 삭제할 수 있음.
    # os 수준의 파일 핸들러와 파일이 저장된 경로를 튜플 형태로 리턴함.
    # os 수준의 파일 핸들러는 파일이 열리는 순서에 따라 1, 2, 3, ...으로 표현됨.
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    
    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """
     1. app fixture를 오버라이딩 합니다.
     오버라이딩이 적용 가능한 범위는 모듈 뿐만 아니라, 동일 폴더에 존재하는 모듈들입니다.
     즉, test_db.py나 test_factory.py에서도 fixture를 오버라이딩 받을 수 있습니다.

     2. 테스트 클라이언트를 리턴합니다.
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
     1. app fixture을 오버라이딩 합니다.
     2. CLI command를 테스트할 수 있도록 합니다.
      - test_cli_runner()는 test_cli_runner_class의 인스턴스를 리턴합니다.
    """
    return app.test_cli_runner()

class AuthActions(object):
    
    """
     flaskr에서 작성한 어플리케이션의 주된 기능은 로그인 후 사용 가능하도록 설계되었습니다.
     따라서 클라이언트의 로그인 테스트가 기본으로 설정되어 있어야 합니다.
    """

    def __init__(self, client):
        self._client = client
    
    def login(self, username='test', password='test'):

        """
         1. data.sql에서 테스트를 위해 저장했던 아이디/비밀번호를 기본 인자로 받습니다.
         2. 아이디/비밀번호를 post로 /auth/login에 전송한 결과를 리턴받습니다.
        """

        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )
    
    def logout(self):

        """
         클라이언트가 /auth/logout을 클릭함으로써 로그아웃된 결과를 리턴받습니다.
        """

        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    """
      1. client를 오버라이딩 받은 후 AuthActions()의 인자로 사용함으로써,
       클라이언트가 로그인/로그아웃 기능을 사용한 결과를 나타낼 수 있습니다
      2. 클라이언트가 선택할 수 있는 활동(로그인/로그아웃)을 fixture로 지정합니다.
    """
    return AuthActions(client)