openapi_html_string = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>APIdoc</title>
    <link rel="shortcut icon" href="
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAalJREFUSImtlsFx1EAQRV9Pga9sBm
gjACJwX21DIZEAIgJwBusIsDOQE2BVRcl7ZMjARGA7A/vIVqHmINnsrkbSyOafRq35/0+3uqcEE6BZ5TW7+DGF46LFP1QLYB9M23UUJEo8Xc6QvStg1oZusf
Xcl9ntGDcuA/c83xCnWe+lUdQoA5O8ExM+x1BHS6TpKkHqq7Cxm/vy4HqIP56B+zNQilrH6ALNKUXspZl1CUIKvO7hX2KUHYqIN5MbXx5ci2YXBdjHsZM8Ck
LhwPpO93QYbxy2VoST/y4unGBrfeiitlsKYP+J0j8xl993V6dNNatOIa7HOxA79t/enm6FQvs0q0rg/UT1c788zHej4Tkw92WaOGC/g5ygQVu/mwnyv/ouvq
FJng2820XvrRo00PS7Ai8mGPQinIG4xUSdV9EGmlY5nVmQc0wyzM0xN28H825jw0zTVRIyeLYtvkqQ+utGaGtoNrDQtCoRPA+lrBUohjNwdU7zce8QO/bLI+
277315dInV/65yEQ3t2zaoXYHxCVsnuxMZNnnngbPmyZKx/Y9G8ztTBQ/0F7HCjBF2T1XVAAAAAElFTkSuQmCC
    ">
    <style>
        body {
            background-color: #131417;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            grid-gap: 36px;
        }

        .box {
            grid-column: span 2;
            width: 300px;
            height: 200px;
            background: #2c303a;
            border-radius: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            transform: scale(1);
            transition: all .3s ease;
        }

        /* Dealing with 2 orphan items */

        .box:last-child:nth-child(3n - 1) {
            grid-column-end: -2;
        }

        .box:nth-last-child(2):nth-child(3n + 1) {
            grid-column-end: 4;
        }

        /* Dealing with single orphan */

        .box:last-child:nth-child(3n - 2) {
            grid-column-end: 5;
        }

        .box:hover {
            transform: scale(1.1);
            box-shadow: 0 0 20px #333743f0;
        }

        .box a {
            color: white;
            font-size: 30px;
            user-select: none;
        }

        .box img {
            user-select: none;
            height: 64px;
            margin-bottom: 10px;
        }

    </style>

</head>
<body>
<div class="grid">
    {% for ui in ui_templates %}
    <div class="box" onclick="window.location.href='{{ ui.name }}';return false">
        <img height="64" src="{{ ui.name }}/images/{{ ui.name }}.svg">
        <a>{{ ui.display_name }}</a>
    </div>
    {% else %}
    <div style="color: white; grid-column: span 2; display: flex; flex-direction: column; grid-column-end: 5;">
        <p>Please install at least one optional UI:</p>
        <p style="font-family: Consolas; background-color: #404348; border-radius: 5px; padding: 5px; font-size: 12px">
        $ pip install -U star-openapi[swagger,redoc,rapidoc,rapipdf,scalar,elements]
        </p>
        <p>More optional ui templates goto the document about
        <a href="https://luolingchun.github.io/star-openapi/v0.x/Usage/UI_Templates/" style="color: #0969da">
        UI_Templates.
        </a>
        </p>
    </div>
    {% endfor %}
</div>

</body>
</html>
"""
