import io
import librosa
import soundfile
from typing import Dict, Any
from flask import jsonify


def make_wave_buf(wave_data, origin_sr: int, sr: int = 44100):
    if origin_sr != sr:
        wave_data = librosa.resample(wave_data, origin_sr, sr)
    # make buf
    buf = io.BytesIO()
    soundfile.write(buf, wave_data, sr, format='WAV', subtype='PCM_16')
    return buf


def get_res_headers(file_name: str = 'sound'):
    return {
        'Content-Type': 'audio/wav',
        'Content-Disposition': f'attachment; filename={file_name}.wav'
    }


def make_json_error(status_code: int, message: str) -> Dict[str, Any]:
    res = jsonify({
        'status': status_code,
        'message': message
    })
    res.status_code = status_code
    return res
