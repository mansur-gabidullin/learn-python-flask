from flask import Flask

import db
import controller

# create and configure the app
app = Flask(__name__, instance_relative_config=True)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db.init(app)
controller.init(app)
