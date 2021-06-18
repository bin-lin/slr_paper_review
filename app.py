from gevent.pywsgi import WSGIServer
from slr_label import create_app

app = create_app()
http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()
