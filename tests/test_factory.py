from flaskr import create_app

"""
 본 모듈은 flaskr의 어플리케이션 팩토리를 테스트하기 위한 목적을 가집니다.
 
 flaskr의 어플리케이션 팩토리는 다음과 같은 기능을 지닙니다.
  1. 어플리케이션 생성
  2. /hello 경로로 접속하면 b"Hello, World" 출력
  
  따라서 위의 두 기능을 테스트 합니다.   
"""

def test_config():
    """
     flaskr을 테스트하기 위해서는 어플리케이션 팩토리가 테스트 모드로 변환되어야 합니다.
      1. testing의 기본 값은 False입니다. 어플리케이션 팩토리의 테스트 모드가 off 상태인지 확인합니다.
      2. 어플리케이선 팩토리를 테스트 모드로 전환시킨 후 testing을 통해 테스트 모드가 켜졌는지 확인합니다.
    """
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_hello(client):
    """
     client가 /hello 경로에 접속했을 때 나타나는 결과를 테스트합니다.
     b'Hello, World!'가 나왔다면, 통과입니다.
    """
    response = client.get('/hello')
    assert response.data == b'Hello, World!'