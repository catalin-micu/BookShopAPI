from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from flask_restx import Api

import const
from microservice_apis import anonymous, authentication, registered_users, admins

api = Api(title='Book Shop API', description='Book shop RESTful API')

api.add_namespace(anonymous.namespace)
api.add_namespace(authentication.namespace)
api.add_namespace(registered_users.namespace)
api.add_namespace(admins.namespace)

scheduler = BackgroundScheduler(
    jobstores={'default': SQLAlchemyJobStore(url=const.DB_CONNECTION_URL)}
)
scheduler.start()

