from datetime import timedelta


# microservice_apis/authentication.py
PASSWORD_REGEX = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,32}$'

# orm
DB_CONNECTION_URL = 'postgresql://postgres:password@localhost:5432/book_shop'

# core/registered_users
CART_CLEANUP_TIMEDELTA_MINUTES = 30

# main.py / Flask app config
JWT_SECRET_KEY = '_thisIs-mySuper*secretAnd@secureBackup#KEY'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=23)

# logging
LOG_FILE_NAME = 'file.log'
