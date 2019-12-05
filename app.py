import fire
import logging
from io import BytesIO

import werkzeug
from flask import Flask, make_response, request
from flask_restplus import Api, Resource, abort, reqparse
from flask_cors import CORS
from file_interface import FileInterface
from settings import MASTER_DIR
from utils import make_json_error, get_logger, make_wave_buf, set_res_headers

#
# default app setup
#
APP = None
API = None
FILE_INTERFACE = None
logger = get_logger('main')


def setup():
    global APP, API, FILE_INTERFACE

    APP = Flask(__name__)
    cors = CORS(APP)
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


@record.route('/list/<string:list_type>')
class RecordList(Resource):

    def get(self, list_type):
        global FILE_INTERFACE
        try:
            info_list = list(FILE_INTERFACE.get_type_list(list_type, blind_files=True))
            return {'info': info_list}, 200
        except (KeyError, FileNotFoundError) as e:
            logger.error(str(e))
            abort(make_json_error(400, str(e)))
        except Exception as e:
            logger.error(str(e))
            abort(make_json_error(500, str(e)))


@record.route('/page/<string:list_type>/<int:page>')
class RecordPage(Resource):

    def get(self, list_type, page):
        global FILE_INTERFACE
        try:
            info_list = list(FILE_INTERFACE.get_page(page, list_type))
            return {'info': info_list}, 200
        except (KeyError, FileNotFoundError) as e:
            logger.error(str(e))
            abort(make_json_error(400, str(e)))
        except Exception as e:
            logger.error(str(e))
            abort(make_json_error(500, str(e)))


@record.route('/page-numbers/<string:list_type>')
class NumberRecordPages(Resource):

    def get(self, list_type):
        global FILE_INTERFACE
        try:
            nb_pages = FILE_INTERFACE.get_nb_pages(list_type)
            return {'nb_pages': nb_pages}, 200
        except KeyError as e:
            logger.error(str(e))
            abort(make_json_error(400, str(e)))
        except Exception as e:
            logger.error(str(e))
            abort(make_json_error(500, str(e)))


@record.route('/audio/<string:audio_type>/<string:key>')
class AudioItem(Resource):

    @API.response(200, "audio/wav")
    def get(self, audio_type, key):
        global FILE_INTERFACE
        try:
            audio_buf = make_wave_buf(*FILE_INTERFACE.read_audio(audio_type, key))
            response = make_response(audio_buf.getvalue())
            set_res_headers(response)
            return response
        except KeyError as e:
            logger.error(str(e))
            abort(make_json_error(400, str(e)))
        except Exception as e:
            logger.error(str(e))
            abort(make_json_error(500, str(e)))


@record.route('/item/<string:key>')
class RecordItem(Resource):

    def get(self, key):
        global FILE_INTERFACE
        try:
            item = FILE_INTERFACE.get_item(key, True)
            return item, 200
        except (KeyError, FileNotFoundError) as e:
            logger.error(str(e))
            abort(make_json_error(400, str(e)))
        except Exception as e:
            logger.error(str(e))
            abort(make_json_error(500, str(e)))

    def delete(self, key):
        try:
            FILE_INTERFACE.remove_recorded_audio(key)
            return {'status': 'ok'}, 201
        except (KeyError, FileNotFoundError) as e:
            logger.error(str(e))
            abort(make_json_error(400, str(e)))
        except Exception as e:
            logger.error(str(e))
            abort(make_json_error(500, str(e)))

    def post(self, key):
        try:
            bin_wav = request.files['file']
            FILE_INTERFACE.write_audio_buffer(key, BytesIO(bin_wav.read()))
            return {'status': 'ok'}, 202
        except (ValueError, AssertionError) as e:
            logger.error(str(e))
            abort(make_json_error(400, str(e)))
        except Exception as e:
            logger.error(str(e))
            abort(make_json_error(500, str(e)))


# main func
def run_api(port=8888, debug=False):
    global APP, API

    loglevel = logging.DEBUG if debug else logging.INFO
    logger.setLevel(loglevel)

    APP.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    # run api
    fire.Fire(run_api)
