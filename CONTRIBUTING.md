## Contributing Guide

Thank you for contributing to Star OpenAPI.

1. [Create a new issue](https://github.com/luolingchun/star-openapi/issues/new)
2. [Fork and Create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)

Before submitting pr, you need to complete the following steps:

1. Install requirements

    ```bash
    uv sync
    ```

2. Running the tests

    ```bash
    set pythonpath=. 
    # or export pythonpath=.
    pytest tests
    ```

3. Running the ruff

    ```bash
    ruff check star_openapi tests examples
    ```

4. Running the ty

    ```bash
    ty check star_openapi
    ```

5. Building the docs

   Serve the live docs with [Material for MkDocs](https://github.com/squidfunk/mkdocs-material), and make sure it's
   correct.

    ```bash
    mkdocs serve
    ```
