import sqlite3

import pytest
from flaskr.db import get_db

"""
 이 모듈은 flaskr의 db.py가 가지는 기능을 테스트하기 위한 목적을 가집니다. 
 
 db.py는 다음과 같은 기능을 지닙니다.
  1. get.db를 불러올 때 flask와 db가 연결되고, 요청 후에는 db가 종료됩니다. 
  2. click 라이브러리로 init-db를 데이터 초기화 명령어로 정의
  
  따라서 위의 두 기능을 테스트 합니다.   
"""

def test_get_close_db(app):

    """
     1. flask와 db를 연결을 활성화합니다.
     2. 이전 db 연결과 같은 connection이 유지되고 있는지 확인합니다.
     3. 1~2번 테스트 이후 teardown에 의하여 db 연결이 종료되어야 합니다.

     4. SQL를 실행함으로써 db 연결이 종료되었는지 확인합니다.
       - 실행되지 않았을 때, 실행되지 않은 이유가 db 연결이 종료(closed)됐다는 것이면 테스트에서 통과됩니다.
    """

    with app.app_context():
        db = get_db()
        assert db is  get_db()
    
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
    
    def fake_init_db():
        Recorder.called = True
    
    # monkeypatch는 pytest의 빌트인 fixture입니다.
    # init_db 함수가 포함된 경로에 타겟이 존재하는지 확인합니다.
    # 본 함수의 맨 밑에 위치한 Recorder.called을 통해 테스트 실패를 확인합니다.
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)

    # test_cli_runner.invoke(cli=None, args=None, **kwargs)
    #  - cli : 실행할 커맨드 객체, args : 실행할 커맨드를 str 형태로 리스트에 입력
    #  - 커맨드 실행 결과로 click.testing.Result 객체를 리턴합니다.
    result = runner.invoke(args=['init-db'])

    # click.testing.Result.output은 유니코드 문자열로 결과 값을 출력합니다.
    assert 'Initialized' in result.output

    # Recorder.called가 True로 변경됐는지 테스트합니다.
    assert Recorder.called