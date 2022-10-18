import logging

from flask import Flask, request
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix

import const
import microservice_apis
from orm import carts

app = Flask(__name__)
# ideally, these are kept in system environment variables and retrieved using os.environ but I will leave them like this
# for convenience
# arguably, a .env or a .flaskenv file could be used
app.config['JWT_SECRET_KEY'] = const.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = const.JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = const.JWT_REFRESH_TOKEN_EXPIRES
JWTManager(app)

app.wsgi_app = ProxyFix(app.wsgi_app)
microservice_apis.api.init_app(app)


logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler(const.LOG_FILE_NAME))

app.logger.addHandler(logging.FileHandler(const.LOG_FILE_NAME))


@app.before_request
def log_request_info():
    app.logger.debug(f'Headers:\n{request.headers}')

    if request.get_data():
        app.logger.debug(f'Body:\n{request.get_data()}')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
