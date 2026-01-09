Star openAPI provides the `star` command, which allows you to implement some quick commands

## star

By default, running the `star` command will prompt the following message, and by default, it will search for the `app`
variable in `asgi.py` in the current path.

```shell
> star
WARNING: Could not import module 'asgi:app': No module named 'asgi'
Usage: star [OPTIONS] COMMAND [ARGS]...

  A general utility script for star-openapi applications.

  An application to load must be given with the 'xxx:app', or with a 'asgi.py'
  file in the current directory.

Options:
  -a, --app TEXT  Application to run, like asgi:app.
  -v, --verbose   Enable verbose mode.
  --help          Show this message and exit.

Commands:
  run  Run a development server.
```

You can use `--app` to specify the location of the app, or you can use `--verbose` to print error details.

```shell
> star --verbose -app module:app    
Traceback (most recent call last):
  File "D:\workspace\star-api-demo\.venv\Lib\site-packages\star_openapi\cli.py", line 450, in _load_app
    importlib.import_module(module)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "C:\Users\xxx\AppData\Roaming\uv\python\cpython-3.14.0-windows-x86_64-none\Lib\importlib\__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1398, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1371, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1335, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'module'
WARNING: Could not import module 'module:app': No module named 'module'
Usage: star [OPTIONS] COMMAND [ARGS]...

  A general utility script for star-openapi applications.

  An application to load must be given with the 'xxx:app', or with a 'asgi.py'
  file in the current directory.

Options:
  -a, --app TEXT  Application to run, like asgi:app.
  -v, --verbose   Enable verbose mode.
  --help          Show this message and exit.

Commands:
  run  Run a development server.
```

## run

A built-in command for debugging services, essentially calling `uvicorn`.

```shell
> star run
INFO:     Will watch for changes in these directories: ['D:\\workspace\\star-api-demo\\src']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [45752] using WatchFiles
INFO:     Started server process [20628]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## custom cli

```python
from star_openapi import OpenAPI

app = OpenAPI()


@app.cli.command("create_db")
def create_db():
    ...


@app.cli.command("init_db")
def init_db():
    ...


@app.cli.command("register_permission")
def register_permission():
    ...
```

Executing the `star` command will display the following information:

```shell
> star
Usage: star [OPTIONS] COMMAND [ARGS]...

  A general utility script for star-openapi applications.

  An application to load must be given with the 'xxx:app', or with a 'asgi.py'
  file in the current directory.

Options:
  -a, --app TEXT  Application to run, like asgi:app.
  -v, --verbose   Enable verbose mode.
  --help          Show this message and exit.

Commands:
  create_db             Create database.
  init_db               Initialize database.
  register_permission   Register permission.
  run                   Run a development server.
```