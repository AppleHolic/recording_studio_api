from io import BytesIO

from flask import Flask, make_response
from flask_restplus import Api, Resource, fields, abort

#
# default app setup
#
from file_interface import FileInterface
from settings import MASTER_DIR
from utils import make_json_error

APP = None
API = None
FILE_INTERFACE = None


def setup():
    global APP, API, FILE_INTERFACE

    APP = Flask(__name__)
    # cors config
    APP.config['CORS_HEADERS'] = 'Content-Type'

    # api
    API = Api(APP)

    FILE_INTERFACE = FileInterface(MASTER_DIR)


setup()


#
# make namespace
#
record = API.namespace('v1/record', description='Recording API')

RecordParams = API.parser()
RecordParams.add_argument('key', type=str, required=True)
RecordParams.add_argument('file', type=str, required=True)

RecordInfo = API.model('RecordInfo', {
    'key': fields.String(required=True),
    'audio': fields.Raw(),
    'recorded': fields.Raw()
})


@record.route('')
class RecordList(Resource):
    pass


@record.route('/<string:key>')
class RecordRead(Resource):

    @API.marshal_witth(RecordInfo, skip_none=True)
    def get(self):
        pass

    @API.expect(RecordParams)
    def update(self):
        try:
            args = RecordParams.parse_args()
            key, bin_wav = args['key'], args['file']
            FILE_INTERFACE.write_audio_buffer(key, BytesIO(bin_wav))
            return {'status': 'ok'}, 202
        except (ValueError, AssertionError) as e:
            print(str(e))
            abort(make_json_error(400, str(e)))
        except Exception as e:
            print(str(e))
            abort(make_json_error(500, str(e)))


@record.route('/<string:key>/<string:type>')
@API.response(404, 'key is not found')
@API.response(500, 'internal server error')
class WaveReader(Resource):

    @API.response(200, 'audio/wav')
    def get(self, key, type):
        global FILE_INTERFACE
        return None
