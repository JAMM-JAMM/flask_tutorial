import os

from flask import Flask


# Flask 어플리케이션은 Flask 클래스의 인스턴스 형태로 만들어진다. 
# 따라서 어플리케이션과 관련된 설정, URL 등은 클래스 내에 등록되게 된다.

# Flask 어플리케이션을 만드는 가장 직접적인 방법은 디폴트 코드에 직접 Flask 인스턴스를 만드는 것이다. 
# (즉, global로 Flask 인스턴스를 생성한다는 의미)
# 하지만 프로젝트의 규모가 커지면 까다로운 문제들이 발생한다.

# 이번 튜토리얼에서는 디폴트 코드를 작성하는 대신, 별도의 내부 모듈(어플리케이션 팩토리)을 이용하여 인스턴스를 생성할 것이다.
# create_app 함수를 application factory라고 부른다.
# 이 함수를 통해 환경설정, 등록, 필요한 어플리케이션 설정 등 각종 기능들을 설정할 것이다.

# __init__.py의 두 가지 기능
# 1. 어플리케이션 팩토리를 담는 것
# 2. 파이썬 엔진이 flaskr 디렉토리를 하나의 패키지처럼 인식하도록 안내한는 기능

def create_app(test_config=None):
    
    # 앱 인스턴스를 생성하고 환경설정을 불러온다.
    # 1. __name__
    # 현재 파이썬 모듈의 이름 (또는 현재 모듈을 지칭하는 방법)
    # 앱(어플리케이션)은 실행 결로를 판단하기 위해서 해당 클래스를 호출한 모듈이 어디인지 알아야 한다. 
    # 2. instance_relative_config=True
    # 앱에게 설정파일은 인스턴스 폴더에 있다라고 알려주는 역할을 한다.
    # 인스턴스 폴더는 flaskr 패키지 외부에 위치하고, git과 같은 툴을 통한 버전 관리 때 저장되면 안되는
    # 민감한 정보(비밀번호, 설정 값, DB 파일 등)를 담고 있기 때문에 별도로 관리해야 함.
    app = Flask(__name__, instance_relative_config=True)

    # app.config.from_mapping()는 앱의 기본 설정을 세팅한다.
    # SECRET_KEY는 Flask 내에서 데이터 보안을 위해 사용된다. 
    # 개발 중에는 디버깅 등 편의를 위해 'dev'로 설정해놓고 진행하지만,
    # 실 가동 환경에서는 꼭 랜덤 값으로 써줘야 함
    # DATABASE는 SQLite 데이터베이스 파일의 경로이다. 
    # 해당 파일들은 app.instance_path 하위에 위치한다.
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # app.config.from_pyfile(): instance 폴더에 config.py 파일이 존재하는 경우, 해당 파일로부터 산출되는 값으로 기본 환경을 설정
    # test_config: 어플리케이션 팩토리로 전달되어 인스턴스 구성 대신 설정 값으로 쓰일 수 있다.
    # 이는 튜토리얼 후반부에 테스트용 설정 값과 개발용 설정 값을 분리하기 위해 만들어졌다.
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # 인스턴스 폴더의 존재 여부를 보장하기 위한 코드이다.
    # os.makedirs()는 app.instance_path에 instance 폴더가 존재하는지 확인해서 없으면 만드는 부분이다.
    # Flask는 인스턴스 폴더를 자동으로 생성하지 않기 때문에 이 코드를 통해 프로젝트가 실행되면, 자동으로 instance 폴더가 생성된다.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # @app.route()는 Flask가 정상 작동하는지 확인하기 위한 그리팅 화면이다.
    # flask를 작동시킨 후 해당 경로로 이동하면 "Hello, Nice to meet you!"가 출력됨을 확인할 수 있다.
    @app.route('/hello')
    def hello():
        return "Hello, world!"
    
    print("============================================================")
    print("flaskr/__init__.py에서 app이 생성되었습니다.")
    
    # db.py의 DB 초기화 함수 실행 (__init__.py)

    # 현재 폴더인 flaskr에서 db.py를 불러온다.
    from . import db
    
    # init_app 함수에서 생성된 어플리케이션을 인자로 전달한다.
    db.init_app(app)

    # 블루프린트 등록 (__init__.py)

    # auth 모듈의 bp 객체를 앱에 블루프린트로 등록시킨다.
    # 뷰와 코드는 블루프린트에 등록되며, 블루프린트는 앱에 등록됨을 알 수 있다.
    from . import auth
    app.register_blueprint(auth.bp)

    # 블루프린트 등록 (__init__.py)

    # 블로그 블루프린트는 사용자 인증 블루프린트와 다르게 url_prefix를 사용하지 않았다.
    # 따라서 index(디폴트) 뷰가 '/' 바로 아래에 위치하게 된다.
    # 마찬가지로 create 뷰는 '/create'에 위치한다.
    # 블로그는 Flaskr 프로젝트의 메인 기능이므로 블로그 전체의 인덱스를 포스트 리스트 화면으로 세팅하는 것이다.
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app

    # 어플리케이션 실행
    # 터미널을 열어서, Flask에게 앱의 위치를 알려주고, development 모드로 실행하도록 지시한 후 앱을 실행시킨다.
    # flask-tutorial 디렉토리 최상위 위치에서 실행시켜야 한다.
    # flaskr 패키지 안에서 실행시키지 않도록 주의해야함!!

    # Mac
    # $ export FLASK_APP=flaskr
    # $ export FLASK_ENV=development
    # $ flask run