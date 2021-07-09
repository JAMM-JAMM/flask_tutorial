# 설치 가능한 프로젝트 만들기

# 우리는 지금까지 Flask를 통해 웹 게시판을 만들었다.
# 개발 과정에서 우리는 /flask_tutorial에서만 웹을 동작시켰다.

# 하지만 실제 코드가 있는 flaskr 폴더을 패키지화 한 뒤, 해당 프로젝트를 설치받으면
# /flask_tutorial 경로에서만이 아닌, 다른 경로에서도 웹을 동작시킬 수 있다.

# 따라서 이번 튜토리얼에서는 늦게 소개되었지만, 프로젝트의 패키지화는 앞으로의 웹 개발에서 선행되어야 하는 작업이다.

# 튜토리얼 진행 순서
# 1. 패키지화: 프로젝트 정의(패키지화 할 파일/폴더 정의) (flask_tutorial/setup.py), 패키지화 할 상세 파일 정의 (flask_tutorial/MANIFEST.in)
# 2. 패키지화 한 프로젝트 설치
# 3. 테스트

# distutils 패키지는 파이썬 설치에 추가적인 모듈을 빌드하고 설치하기 위한 기능을 제공한다.
# 이번 실습에서는 flaskr을 모듈로써 빌드하려고 한다.
# 모듈은 파이썬으로만 작성되었거나, C로 작성된 확장 모듈이거나 파이썬과 C로 작성되었을 수도 있다.

# 하지만 distutils 패키지를 직접 사용하기 보다는 setuptools 라이브러리를 사용할 것을 권장하고 있다.
# setuptools는 파이썬 패키지 권한으로 작동한다.

# 또한, 공식 가이드에서 권장되는 모든 pip 인스톨러는 setup.py 스크립트에서 setuptools 라이브러리와 함께 실행된다.
# 만약에 스크립트 자체에 distutils 패키지를 import 했더라도 함께 실행된다.

from setuptools import find_packages, setup


setup(

    # 배포할 패키지의 이름
    name='flaskr',

    # 배포할 패키지 버전
    version='1.0.0',

    # packages는 어떤 패키지를 포함할 지 파이썬에 정의해준다.
    # find_packages()는 자동으로 패키지(flaskr)의 위치를 찾아낸다.
    packages=find_packages(),

    # 패키지 내에 있는 폴더들과 데이터를 포함할 지를 선택한다.
    # True로 선택했다면, MANIFEST.in 파일을 만들어서 어떤 파일/폴더를 포함할 지 명시해야 한다.
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)

# 패키지화 할 상세 파일 정의 (flask_tutorial/MANIFEST.in)

# include flaskr/schema.sql
# graft flaskr/static
# graft flaskr/templates
# global-exclude *.pyc

# MANIFEST.in 파일 안에 위 내용을 정의한다.
# 이로써, flaskr 폴더의 패키지화 정의는 모두 끝

# 패키지화 한 프로젝트 설치
# 터미널에서 flask_tutorial 경로로 이동
# pip install -e .를 입력한다. : 현재 경로 (.)에서 setup.py을 찾아서 개발자 모드로 설치한다는 의미이다.

# 실행 결과
# 1. pip install -e .을 입력하면 flask_tutorial에서 파일을 수집한다.
# 2. flaskr에 포함된 라이브러리들이 flaskr과 호환되는 버전인지 체크한다.
# 3. flaskr이 성공적으로 설치되었다.
