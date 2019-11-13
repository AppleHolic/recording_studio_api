import fire
import logging
from io import BytesIO
from flask import Flask, make_response
from flask_restplus import Api, Resource, fields, abort

#
# default app setup
#
from file_interface import FileInterface
from settings import MASTER_DIR
from utils import make_json_error, get_logger


APP = None
API = None
FILE_INTERFACE = None
logger = get_logger('main')


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

    def get(self):
        pass

    def delete(self, key):
        try:
            FILE_INTERFACE.remove_recorded_audio(key)
            return {'status': 'ok'}, 201
        except (KeyError, FileNotFoundError) as e:
            logger.info(str(e))
            abort(make_json_error(400, str(e)))
        except Exception as e:
            logger.info(str(e))
            abort(make_json_error(500, str(e)))

    @API.expect(RecordParams)
    def update(self, key):
        try:
            args = RecordParams.parse_args()
            bin_wav = args['file']
            FILE_INTERFACE.write_audio_buffer(key, BytesIO(bin_wav))
            return {'status': 'ok'}, 202
        except (ValueError, AssertionError) as e:
            logger.info(str(e))
            abort(make_json_error(400, str(e)))
        except Exception as e:
            logger.info(str(e))
            abort(make_json_error(500, str(e)))


@record.route('/<string:key>/<string:type>')
@API.response(404, 'key is not found')
@API.response(500, 'internal server error')
class WaveReader(Resource):

    @API.response(200, 'audio/wav')
    def get(self, key, type):
        global FILE_INTERFACE
        return None


# main func
def run_api(port=8888, debug=False):
    global APP, API

    loglevel = logging.DEBUG if debug else logging.INFO
    logger.setLevel(loglevel)

    APP.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    # run api
    fire.Fire(run_api)
