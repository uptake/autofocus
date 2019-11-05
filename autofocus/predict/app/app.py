from flask import Flask

from .routes.predict import predict_route
from .routes.predict_zip import predict_zip_route


app = Flask(__name__)
app.config.from_object(__name__)

app.register_blueprint(predict_route)
app.register_blueprint(predict_zip_route)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
