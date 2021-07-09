# Flask Tutorial
flask 튜토리얼을 통한 블로그 페이지 클론코딩

<br />

**Reference**
- https://gaza-anywhere-coding.tistory.com/51?category=839938
- https://www.finterstella.com/7?category=809900
- https://flask.palletsprojects.com/en/2.0.x/tutorial/factory/

<br />

## base.html

```html
<!--
    템플릿
    지금까지 웹 사이트에서 이용할 사용자 인증 관련 기능을 개발했다.
    하지만 이들 URL에 접속하려고 하면 TemplateNotFound 라는 에러메시지가 뜬다.
    이는 사용자 인증 관련 뷰가 render_template() 이라는 함수를 호출하지만
    아직 템플릿을 작성하지 않았기 때문이다. flaskr 패키지에서는 탬플릿 파일들을 templates 디렉토리에 저장할 것이다.

    템플릿은 정적인 데이터 뿐 아니라 placeholder를 이용해서 표시되는 동적인 데이터를 함께 담고있는 파일이다.
    템플릿은 데이터와 결합해 최종적인 화면을 생성한다. Flask는 탬플릿을 화면에 뿌려주기 위해 Jinja라는 탬플릿 라이브러리를 사용한다.

    Jinja는 autoescape, 즉 사용자가 입력한 문자가 기존 html 코드와 뒤섞여서 화면을 깨지게 만드는 것을 방지하는 기능을 탑재하고 있다.

    Jinja는 파이썬과 매우 유사한 형식을 갖는다. 탬플릿 내에서 '{{  }}'로 둘러쌓인 부분은 출력문 삽입을 위해 사용되고, 
    '{%  %}'로 둘러쌓인 부분은 if나 for와 같은 제어문을 삽입할 때 사용된다. 파이썬과 다른 부분은 들여쓰기를 통해 for나 if에 속한
    절이 구분되지 않고, 시작과 끝을 표시하는 태그를 이용한다는 점이다.

    튜토리얼 진행 순서
    1. base.html 작성
    2. base를 상속한 html 작성 (로그인)
    3. base를 상속한 html 작성 (회원가입)
-->

<!--
    1. base.html 작성
    대게 웹 사이트의 각 페이지는 본문을 제외하면 동일한 헤더와 풋터를 갖는 단일 레이아웃으로 표현된다.
    베이스 레이아웃을 이용해 각 템플릿마다 전체 레이아웃을 일일히 작성하는 대신, 중복되는 부분을 재활용 할 수 있다.
-->

<!doctype html>
<title>{% block title %}{% endblock %} - Flaskr</title>
<!-- 스타일을 입히기 위해 'flaskr/static/style.css'를 읽어온다. -->
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
<nav>
  <h1>Flaskr</h1>
  <ul>
    <!--
        jinja2에서는 g가 기본적으로 제공된다.

        g.user의 데이터가 들어올 수 있는 과정은 다음과 같다.
        1. 모든 뷰는 auth.py의 load_logged_in_user을 거쳐서 실행된다.
        2. load_logged_in_user 안에는 세션의 아이디를 식별하고 DB에서 정보를 꺼내온다.
        3. 꺼내온 정보는 g.user에 담긴다.
        4. g.user에 담긴 정보를 jinja2를 통해 꺼내온다.
    -->
    <!--
        g.user 정보의 존재 여부에 따라 username과 logout 링크가 표시될 지,
        register와 log in 링크가 표시될 지 결정된다. url_for() 역시 g.user 정보에 따라 자동으로 생성된다.
    -->
    {% if g.user %}
      <li><span>{{ g.user['username'] }}</span>
      <!--
          url_for은 jinja에서 자동적으로 지원되는 기능이다.
          이를 통해 생성된 url 경로를 클릭하면, 해당 결로를 갖는 함수로 이동한다.
      -->
      <li><a href="{{ url_for('auth.logout') }}">Log Out</a>
    {% else %}
      <li><a href="{{ url_for('auth.register') }}">Register</a>
      <li><a href="{{ url_for('auth.login') }}">Log In</a>
    {% endif %}
  </ul>
</nav>
<section class="content">
  <header>
    <!--
      상속받는 템플릿은 header의 이름으로 정의된 block 영역을 오버라이딩 할 수 있다.
    -->
    {% block header %}{% endblock %}
  </header>
  <!--
      페이지 타이틀과 본문 사이에 탬플릿은 auth.py에서 오류 메세지를 flash 했다면,
      그 정보를 루프를 돌면서 get_flashed_message()가 생성하는 메세지를 뿌려준다.
  -->
  {% for message in get_flashed_messages() %}
    <div class="flash">{{ message }}</div>
  {% endfor %}
  {% block content %}{% endblock %}
</section>
<!--
    템플릿들이 공유하는 블록들은 다음 3개 이다.
    
    1. {% block title %} 블록은 브라우저 탭에 표시될 페이지 제목을 출력한다.
    2. {% block heaeder %} 는 웹 페이지 상에 표시되는 페이지 제목을 출력한다.
    3. {% block content %} 는 각 페이지의 본문이 표시되는 부분이다.

    베이스 템플릿은 템플릿 디렉토리 안에 위치한다. 다른 파일들과 함께 유기적으로 유지하기 위해 
    블루프린트를 위한 탬플릿은 블루프린트와 같은 이름의 디렉토리에 저장된다.
-->
```

<br />

## login.html
```html
{% extends 'base.html' %}

{% block header %}
  <h1>{% block title %}Log In{% endblock %}</h1>
{% endblock %}

{% block content %}
  <form method="post">
    <label for="username">Username</label>
    <!--
        required는 제공된 양식에 내용을 채워넣지 않으면, 제출되지 않도록 하는 기능이다.
        대부분의 브라우저에서는 required 기능을 지원하지만, 지원되지 않는 브라우저를 대비해서
        반드시 서버 단에서도 id/pw 등이 넘어오지 않는 경우를 대비해야 한다.
    -->
    <input name="username" id="username" required>
    <label for="password">Password</label>
    <input type="password" name="password" id="password" required>
    <input type="submit" value="Log In">
  </form>
{% endblock %}
```

<br />

## register.html
```html
<!--
    base.html을 상속받는다. jinja 탬플릿은 block을 통해서 base template을 상속 받을 수 있다.
    이를 통해 중복되는 코드를 줄일 수 있다.
-->
{% extends 'base.html' %}

{% block header %}
  <!--
      아래와 같은 형식을 통해서 base.html에 존재하는 두 개의 block에
      동일한 데이터를 한 번에 넘겨줄 수 있다.
  -->
  <h1>{% block title %}Register{% endblock %}</h1>
{% endblock %}

{% block content %}
  <form method="post">
    <label for="username">Username</label>
    <input name="username" id="username" required>
    <label for="password">Password</label>
    <input type="password" name="password" id="password" required>
    <input type="submit" value="Register">
  </form>
{% endblock %}
```

<br />

## style.css

- 이제 사용자 인증 기능은 뷰와 템플릿이 결합되어 정상 작동된다.
- 하지만 아직 일반 웹 사이트처럼 예쁘게 보이지 않는다.
- HTML로 되어있는 탬플릿에 CSS라고 불리우는 스타일 시트를 추가하겠다.
- 스타일 시트는 수시로 변하지 않고, 개발자가 따로 손대지 않는 이상 변하지 않아 정적 파일이라고 부른다.
- Flask는 자동으로 static이라는 디렉토리를 생성하고 그 안에 정적 파일들을 저장하여 탬플릿과 연동시킨다. 앞서 작성한 base.html 탬플릿에 이미 style.css와의 연동 부분이 포함되어 있따.
- 정적 파일에는 CSS 파일 이외에도 이미지나 JavaScript 파일 등이 포함된다.
- 정적 파일들은 모두 flaskr/static 디렉토리 내에 저장되어 url_for('static', filename='...')처럼 불러오게 된다.

## index.html

```html
{% extends 'base.html' %}

{% block header %}
  <h1>{% block title %}Posts{% endblock %}</h1>
  <!--
      로그인된 사용자라면 header 블록 내에 있는 New 버튼이 활성화되며 create 뷰로 링크가 생성된다.
  -->
  {% if g.user %}
    <a class="action" href="{{ url_for('blog.create') }}">New</a>
  {% endif %}
{% endblock %}

{% block content %}
<!-- 유저들이 작성한 글을 보여준다. -->
  {% for post in posts %}
    <article class="post">
      <header>
        <div>
          <h1>{{ post['title'] }}</h1>
          <!-- 'by ??? on 2021-07-10'가 글의 제목 밑에 출력된다.-->
          <div class="about">by {{ post['username'] }} on {{ post['created'].strftime('%Y-%m-%d') }}</div>
        </div>
        <!-- 글의 작성자의 글을 클릭했을 때는 수정하기 버튼을 나타낸다. -->
        {% if g.user['id'] == post['author_id'] %}
          <a class="action" href="{{ url_for('blog.update', id=post['id']) }}">Edit</a>
        {% endif %}
      </header>
      <!-- 글의 내용을 출력한다. -->
      <p class="body">{{ post['body'] }}</p>
    </article>
    <!--
        1. loop.last는 반복문에서 마지막 반복을 제외하고 수행되는 명령어이다.
        2. hr은 html 에서 가로 줄을 나타내는데 사용된다.
        즉, 아래 코드는 글의 내용을 가로 줄로 구분하기 위해 작성되었다. (맨 마지막 줄은 가로 줄을 그리지 않는다.)
    -->
    {% if not loop.last %}
      <hr>
    {% endif %}
  {% endfor %}
{% endblock %}
```

<br />

## update.html
```html
{% extends 'base.html' %}

{% block header %}
  <h1>{% block title %}Edit "{{ post['title'] }}"{% endblock %}</h1>
{% endblock %}

{% block content %}
  <form method="post">
    <label for="title">Title</label>
    <!--
        객체 설명
        request.form['...']는 수정을 요청하는 값이 request 객체에 저장된 것
        post['...']는 db에 있는 특정 값에 대한 내용

        jinja2의 operation 설명
        'or'은 왼쪽이 True가 아니면 오른쪽이 True를 의미한다.
        request.form['...']에 내용이 없으면, post['body']를 출력하고
        request.form['...']에 내용이 들어있으면 그에 대한 내용을 출력한다.
    -->
    <input name="title" id="title"
      value="{{ request.form['title'] or post['title'] }}" required>
    <label for="body">Body</label>
    <textarea name="body" id="body">{{ request.form['body'] or post['body'] }}</textarea>
    <input type="submit" value="Save">
  </form>
  <hr>
  <form action="{{ url_for('blog.delete', id=post['id']) }}" method="post">
    <input class="danger" type="submit" value="Delete" onclick="return confirm('Are you sure?');">
  </form>
{% endblock %}
```