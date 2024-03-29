import io
import librosa
import soundfile
import logging
from typing import Dict, Any
from flask import jsonify


def make_wave_buf(wave_data, origin_sr: int, sr: int = 44100):
    if origin_sr != sr:
        wave_data = librosa.resample(wave_data, origin_sr, sr)
    # make buf
    buf = io.BytesIO()
    soundfile.write(buf, wave_data, sr, format='WAV', subtype='PCM_16')
    return buf


def set_res_headers(res, file_name: str = 'sound'):
    res.headers['Content-Type'] = 'audio/wav'
    res.headers['Content-Disposition'] = f'attachment; filename={file_name}.wav'


def make_json_error(status_code: int, message: str) -> Dict[str, Any]:
    res = jsonify({
        'status': status_code,
        'message': message
    })
    res.status_code = status_code
    return res


def get_logger(name: str):
    """
    Get formatted logger instance
    :param name: logger's name
    :return: instance of logger
    """
    # setup logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
