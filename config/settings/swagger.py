"""
Swagger settings 
"""

SPECTACULAR_SETTINGS = {
    "TITLE": "ReHo24 API",
    "DESCRIPTION": "Documentation of API endpoints of XP",
    "VERSION": "0.0.1",
    "SERVE_PERMISSIONS": [
        # "rest_framework.permissions.IsAdminUser",
        "rest_framework.permissions.AllowAny",
    ],
    # FileField (ImageField) to be handled properly
    # https://drf-spectacular.readthedocs.io/en/latest/faq.html?highlight=imagefield#filefield-imagefield-is-not-handled-properly-in-the-schema
    "COMPONENT_SPLIT_REQUEST": True,
    # for tag extraction and grouping
    "SCHEMA_PATH_PREFIX": r'/api/v[0-9]',
    "PREPROCESSING_HOOKS": ["contrib.utils.spectacular.exclude_wagtail_endpoints"],
}
