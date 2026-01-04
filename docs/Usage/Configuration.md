star-openapi provides various configurations that you can use to customize the behavior of the API documentation and UI.

## SWAGGER_HTML_STRING

You can customize the custom behavior of this template.

You can find the default `SWAGGER_HTML_STRING` in the star-openapi source code.

## SWAGGER_CONFIG

You can change the default behavior of the Swagger UI.

```python
from star_openapi import OpenAPI

app = OpenAPI(info=info)

app.config["SWAGGER_CONFIG"] = {
    "docExpansion": "none",
    "validatorUrl": "https://www.b.com"
}
```

[More configuration options for Swagger UI](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md).

## OAUTH_CONFIG

You can configure OAuth 2.0 authorization for Swagger UI.

```python
from star_openapi import OpenAPI

app = OpenAPI(info=info)

app.config["OAUTH_CONFIG"] = {"clientId": "xxx", "clientSecret": "xxx"}
```

[More configuration options for Swagger UI](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/oauth2.md).

## SCALAR_HTML_STRING

You can customize the custom behavior of this template.

You can find the default `SCALAR_HTML_STRING` in the star-openapi source code.

## SCALAR_CONFIG

You can change the default behavior of the Scalar UI.

[More configuration options for Swagger UI](https://github.com/scalar/scalar/blob/main/documentation/configuration.md).

## REDOC_HTML_STRING
You can customize the custom behavior of this template.

You can find the default `REDOC_HTML_STRING` in the star-openapi source code.

## REDOC_CONFIG

You can change the default behavior of the Redoc UI.

[More configuration options for Redoc UI](https://github.com/Redocly/redoc/blob/main/docs/config.md).

## RAPIDOC_HTML_STRING

You can customize the custom behavior of this template.

You can find the default `RAPIDOC_HTML_STRING` in the star-openapi source code.

## RAPIDOC_CONFIG

You can change the default behavior of the Rapidoc UI.

[More configuration options for Rapidoc UI](https://rapidocweb.com/examples.html).

## RAPIPDF_HTML_STRING

You can customize the custom behavior of this template.

You can find the default `RAPIPDF_HTML_STRING` in the star-openapi source code.

## RAPIPDF_CONFIG

You can change the default behavior of the Rapipdf UI.

[More configuration options for Rapipdf UI](https://mrin9.github.io/RapiPdf/).

## ELEMENTS_HTML_STRING

You can customize the custom behavior of this template.

You can find the default `ELEMENTS_HTML_STRING` in the star-openapi source code.


## ELEMENTS_CONFIG

You can change the default behavior of the Elements UI.

[More configuration options for Rapipdf UI](https://github.com/stoplightio/elements/blob/main/docs/getting-started/elements/elements-options.md).