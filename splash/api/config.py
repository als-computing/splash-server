from starlette.config import Config

config = Config(".env")


class ConfigStore():
    # Full Mongo database url, including database and authentication
    MONGO_DB_URI = config("MONGO_DB_URI", cast=str, default="mongodb://localhost:27017")

    # Client ID used to validate google tokens
    GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", cast=str)

    # Client secret used to validate google tokens during OCID access check
    GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET", cast=str)

    # Key for generating access tokens
    TOKEN_SECRET_KEY = config("TOKEN_SECRET_KEY", cast=str)

    # Life span of a generated access token
    ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=30)

    # EXPERIMENTAL auth token url for validating with external OCID authenticator
    OAUTH_AUTH_URL = config('OAUTH_AUTH_URL', cast=str, default="https://accounts.google.com/o/oauth2/auth/oauthchooseaccount")

    # EXPERIMENTAL auth token redirect url for verifiying token
    OAUTH_TOKEN_URL = config("OAUTH_TOKEN_URL", cast=str, default="http://localhost:8080/api/idtokensignin/verifier")

    SPLASH_LOG_LEVEL = config("SPLASH_LOG_LEVEL", cast=str, default="INFO")