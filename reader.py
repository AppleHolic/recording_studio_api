import glob
import os
from io import BytesIO
from typing import List, Tuple


def read_master_dir(master_dir: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Read master directory to construct wave and text pair.
    It should be seems like ...
    master_dir
    ㄴ texts
    ㄴ waves (optional)
    ㄴ recorded (It will be maked if it is not exists)
    And they must have same names.
    :param master_dir: Saved directory
    """
    # read texts
    text_list = glob.glob(os.path.join(master_dir, 'texts', '*.txt'))

    # check waves and load it if it is exists
    wave_dir = os.path.join(master_dir, 'waves')
    if os.path.exists(wave_dir):
        wave_list = glob.glob(os.path.join(wave_dir, '*.wav'))
    else:
        wave_list = []

    # check already recorded
    recorded_dir = os.path.join(master_dir, 'recorded')
    if os.path.exists(recorded_dir):
        recorded_list = glob.glob(os.path.join(recorded_dir, '*.wav'))
    else:
        recorded_list = []

    return text_list, wave_list, recorded_list


def parse_file_name(file_path: str) -> str:
    # parse file name
    filename = os.path.basename(file_path).split('.')[0]
    return filename


def read_audio_buffer(wave_file_path: str) -> BytesIO:
    """
    It returns binary information of wave file
    :param wave_file_path: wave file path
    :return:
    """
    with open(wave_file_path , 'rb') as rb:
        buf = BytesIO(rb.read())
        return buf


def read_text(text_file_path: str) -> str:
    """
    :param text_file_path: text file path
    :return: text
    """
    with open(text_file_path, 'r') as r:
        return r.read().strip()
