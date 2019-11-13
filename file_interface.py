import glob
import os
from enum import Enum

from natsort import natsorted
from io import BytesIO
from typing import Dict
from collections import deque

from utils import get_logger


logger = get_logger('main')


class ListType(Enum):

    ALL = 0
    REC = 1
    UNREC = 2


class FileInterface:

    def __init__(self, master_dir: str):
        self.master_dir = master_dir

        # define directory
        self.text_dir = os.path.join(self.master_dir, 'texts')
        self.wave_dir = os.path.join(self.master_dir, 'waves')
        self.recorded_dir = os.path.join(self.master_dir, 'recorded')

        # check and make dirs
        os.makedirs(self.wave_dir, exist_ok=True)
        os.makedirs(self.recorded_dir, exist_ok=True)

        # define file lists
        self.text_list = None
        self.wave_list = None
        self.recorded_list = None

        # main dict
        self.main_info = {}

        # init
        logger.info('Initialize ...')
        self.init_master_dir()
        logger.info('--- File Info ---')
        logger.info(f'{len(self.text_list)} Text Files')
        logger.info(f'{len(self.wave_list)} Wave Files')
        logger.info(f'{len(self.recorded_list)} Recorded Files')
        self.make_dict()

        # key list
        self.key_list = natsorted(self.main_info['texts'].keys())
        self.nb_pagination = 10

        # store splitted keys
        self.other_key_deque, self.recorded_key_deque = self.get_splitted_keys()

    def get_type_list(self, type: str):
        type = ListType[type.upper()]
        if type == ListType.ALL:
            key_list = self.key_list
        elif type == ListType.REC:
            key_list = self.recorded_key_deque
        elif type == ListType.UNREC:
            key_list = self.other_key_deque
        else:
            key_list = []
        return key_list

    def get_page(self, idx: int, type: str):
        # get key list
        key_list = self.get_type_list(type)
        # get number of pages
        nb_pages = len(key_list) // self.nb_pagination
        assert idx < nb_pages, f'{idx} is cannot over than {nb_pages} !'

        # slice page keys
        page_keys = key_list[self.nb_pagination * idx:self.nb_pagination * (idx + 1)]

        # get items
        page_items = [self.get_item(key, is_buffer=False) for key in page_keys]
        return page_items

    def get_nb_pages(self, type: str):
        return len(self.get_type_list(type))

    def get_item(self, key: str, is_buffer: bool = False) -> Dict[str, str]:
        # parse item
        text = self.main_info['texts'][key]
        wave = self.main_info['waves'].get(key, '')
        recorded = self.main_info['recorded'].get(key, '')

        # read text
        with open(text, 'r') as r:
            text = r.read().strip()

        if is_buffer:
            if wave:
                wave = self.read_audio_buffer(wave)

            if recorded:
                recorded = self.read_audio_buffer(recorded)

        return {
            'key': key,
            'text': text,
            'wave': wave,
            'recorded': recorded
        }

    def get_splitted_keys(self):
        # recorded key list
        recorded_key_deque = deque([key for key in self.key_list if key in self.main_info['recorded']])
        # un-recorded key list
        other_key_deque = deque([key for key in self.key_list if key not in recorded_key_deque])
        return other_key_deque, recorded_key_deque

    def init_master_dir(self):
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
        self.text_list = glob.glob(os.path.join(self.text_dir, '*.txt'))

        # check waves and load it if it is exists
        if os.path.exists(self.wave_dir):
            self.wave_list = glob.glob(os.path.join(self.wave_dir, '*.wav'))
        else:
            self.wave_list = []

        # check already recorded
        if os.path.exists(self.recorded_dir):
            self.recorded_list = glob.glob(os.path.join(self.recorded_dir, '*.wav'))
        else:
            self.recorded_list = []

    def make_dict(self):
        # text dict
        text_dict = {self.parse_file_name(text_path): text_path for text_path in self.text_list}
        self.main_info['texts'] = text_dict

        # wave dict
        wave_dict = {self.parse_file_name(wave_path): wave_path for wave_path in self.wave_list}
        self.main_info['waves'] = wave_dict

        # recorded dict
        rec_dict = {self.parse_file_name(rec_path): rec_path for rec_path in self.recorded_list}
        self.main_info['recorded'] = rec_dict

    @staticmethod
    def parse_file_name(file_path: str) -> str:
        # parse file name
        filename = os.path.basename(file_path).split('.')[0]
        return filename

    @staticmethod
    def read_audio_buffer(wave_file_path: str) -> bytes:
        """
        It returns binary information of wave file
        :param wave_file_path: wave file path
        :return:
        """
        with open(wave_file_path, 'rb') as rb:
            return str(rb.read())

    def write_audio_buffer(self, key: str, wave_buffer: BytesIO):
        wave_file_path = os.path.join(self.recorded_dir, f'{key}.wav')
        # write audio buffer
        with open(wave_file_path, 'wb') as wb:
            wb.write(wave_buffer.getvalue())
        # update info
        self.main_info['recorded'][key] = wave_file_path
        if key in self.other_key_deque:
            self.other_key_deque.remove(key)
            self.recorded_key_deque.appendleft(key)

    def remove_recorded_audio(self, key: str):
        os.remove(self.main_info['recorded'][key])

    @staticmethod
    def read_text(text_file_path: str) -> str:
        """
        :param text_file_path: text file path
        :return: text
        """
        with open(text_file_path, 'r') as r:
            return r.read().strip()
