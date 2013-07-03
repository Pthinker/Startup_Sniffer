from app import app
import socket

if socket.gethostbyname(socket.gethostname()).startswith('192'):
    port = 5000
else:
    port = 80

app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

