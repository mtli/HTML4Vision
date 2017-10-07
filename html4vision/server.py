import sys
import os

from flask import Flask
from flask import send_from_directory

app = Flask(__name__, static_url_path='/dummy/path/to/avoid/conflict', root_path=os.getcwd())

@app.route('/<path:path>')
def sendfile(path):
    return send_from_directory('', path)

if __name__ == "__main__":
    port = 6096 if len(sys.argv) < 2 else int(sys.argv[1])
    app.run('0.0.0.0', port, threaded=True)
