# 이번 튜토리얼에서는 Python을 통해 SQLite 데이터베이스를 초기화하는 것을 배웁니다.

# DB 구축
# 사용자 데이터와 블로그 글 데이터를 저장하기 위해서 SQLite라는 데이터베이스를 이용한다.
# SQLite는 파이썬 빌트인 데이터베이스로 sqlite3 모듈을 이용해서 접근할 수 있다.
# SQLite는 파이썬 빌트인 데이터베이스라 별도로 설정을 할 필요가 없어 편리하다.
# 하지만 동시에 다중 write가 안된다는 단점이 있다.
# 작은 사이트에서는 문제가 없지만, 상용으로 사용한다면 다른 데이터베이스를 선택하는 것이 유용하다.

# 튜토리얼 수행순서
# 1. DB 연결 함수 정의, DB 연결 해지 함수 정의 (db.py)
# 2. 테이블 생성 쿼리 파일 생성 (user, post 테이블 생성) (schema.sql)
# 3. DB 초기화 함수 정의 (schema.sql로 초기화) (db.py)
# 4. 가상 환경에서 사용될 함수 이름 정의 (db.py)
# 5. 어플리케이션에 DB 연결함수와 해지 함수를 등록 (db.py)
# 6. db.py의 DB 초기화 함수 실행 (__init__.py)

# 1. 데이터베이스 연결, DB 연결 함수 정의, DB 연결 해지 함수 정의 (db.py)
# 데이터베이스를 사용하기 위해 첫 번째 할 일은 앱과 데이터베이스를 연결해주는 일이다.
# 이후 데이터베이스로의 모든 쿼리는 이 커넥션을 통해 전달되고, 수행이 완료되면 커넥션을 닫아준다.

# 웹 어플리케이션은 통상적으로 request를 통해 커넥션을 연결시키고, response를 보내기 직전에 닫아준다.

import sqlite3

# click은 터미널에서 실행되며, 빌트인, 확장, 어플리케이션에서 정의한 명령어를 사용할 수 있게 한다.
import click

# g는 각각의 request에 할당되는 고유한 객체이다.
# request에 해당하는 데이터를 저장하는데 사용된다.
from flask import g

# current_app은 request를 발생시킨 Flask 앱을 가리키는 객체이다.
# 어플리케이션이 생성되거나 request를 처리할 때, "현재 어플리케이션이 위치한 경로의 sql파일을 읽어오기" 등에 사용된다.
from flask import current_app

# with_appcontext는 click.command()를 사용할 때 함께 사용된다.
from flask.cli import with_appcontext

# get_db 함수는 최초 실행 시 g 객체를 생성해서 할당해주는데,
# 두 번째 실행부터는 새로 g 객체를 생성하지 않고 이미 생성해놓은 g를 재활용한다.
def get_db():

    # 1. flask와 sqlite 간에 연결된 "db"라는 객체명이 없다면,
    if 'db' not in g:

        # 데이터베이스 설정 키 값에서 지정한 파일로 커넥션을 맺어준다
        g.db = sqlite3.connect(
            
            # DATABASE는 flask_tutorial/instance/flask.sqlite이다.
            # 아직 이 파일이 있을 필요는 없고, 뒤에서 초기화 시켜줄 때 생성된다.
            current_app.config['DATABASE'],
            
            # sqlite3.PARSE_DECLTYPES
            # db에 있는 컬럼 데이터를 가져올 때, 타입이 무엇인지 판별하는 역할을 한다.
            # 가장 앞에 있는 단어를 통해 판별 (ex. integer primary key -> integer로 인식)
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # sqlite3.Row는 커넥션이 결과값을 딕셔너리 형태로 돌려주게 한다.
        # 이를 db의 row_factory 객체로 저장하여 사용한다.
        # 이를 통해 각 컬럼에 컬럼명을 이용해 접근할 수 있다.
        g.db.row_factory = sqlite3.Row

    return g.db

# close_db 함수는 g 객체의 db 값을 확인해서 커넥션이 생성되었는지 확인하고, 커넥션이 생성되었으면 닫아준다.
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
    
    # click.echo는 터미널에 출력되는 문구이다.
    click.echo("------------------------------------------------------")
    click.echo("close.db(): teardown_appcontext로 설정한 close_db()가 활성화 되었습니다")
    click.echo("close.db(): flask와 sqlite 간의 연결을 종료합니다.")
    click.echo("======================================================")

# 3. DB 초기화 함수 정의 (db.py)

def init_db():

    # get_db()를 호출하여 request로부터 flask와 sqlite의 연결을 담당하는 객체를 생성하여 커넥션을 맺는다.
    db = get_db()

    # open_resource()
    # flaskr 패키지와 관련된 파일을 열 수 있다.
    # 이는 나중에 응용 프로그램을 배포할 때, 해당 파일의 위치가 어디에 있는 지 알 필요가 없기 때문에
    # 상대위치로 지정한 파일을 가져올 수 있다.
    # 그리고 이 파일에서 읽어온 명령어는 커넥션을 통해 실행한다.
    with current_app.open_resource('schema.sql') as f:
        
        # executescript()는 여러 개의 sql문을 한 번에 실행할 수 있는 sqlite의 함수이다.
        db.executescript(f.read().decode('utf8'))

# 4. 가상 환경에서 사용될 함수이름 정의 (db.py)

# click.command()는 어플리케이션의 함수가 가상환경에서 사용되는 이름을 지정한다.
# db를 초기화하는 init_db() 함수는 터미널에서 init-db라는 이름으로 실행되고, 성공 여부를 반환한다.
@click.command('init-db')
@with_appcontext
def init_db_command():
    
    click.echo("---------------------------------------------------------------")
    click.echo("init_db_command(): add_command로 설정한 init_db_command가 실행되었습니다.")
    init_db()
    click.echo('Initialized the database.')
    click.echo("init_db_command(): schema.sql을 기본값으로 데이터베이스를 초기화 했습니다.")

# 5. 어플리케이션에 DB 연결 함수와 해지 함수 등록 (db.py)

# close_db와 init_db_command 기능을 앱 인스턴스로 등록해야 앱에서 사용할 수 있다.
# 그러나 여기에서는 어플리케이션 팩토리(flaskr/__init__.py)를 사용하기 때문에 해당 인스턴스를 사용할 수 없다.
# 대신 응용 프로그램을 작성하고 등록을 수행하는 함수를 작성한다.
# 어플리케이션 팩토리에서 init_app(app) 기능을 import해서 실행시켜준다.
def init_app(app):

    # app.teardown_appcontext()는 response를 리턴할 때 마다 Flask에 에 해당 함수를 호출하도록 지시한다.
    # 여기에서 close_db 함수는 response 후에 객체를 제거(정리)하는 목적으로 사용
    app.teardown_appcontext(close_db)

    # app.cli.add_command()는 터미널에서 사용할 수 있는 flask command를 추가할 수 있다.
    app.cli.add_command(init_db_command)

# 이후 __init__.py로 이동하여 init_app 함수를 import해서 등록해준다.

# 결과

# create_app()이 실행된 결과로 instance 폴더와 그 하위에 flaskr.sqlite가 생성되었다.
# flaskr.sqlite은 sqlite 데이터베이스 파일이다.
# init_db_command를 통해서 schema.sql에 적힌 sql문을 실행시킨 후, 그 내용들이 flaskr.sqlite로 저장된 것으로 보인다.
