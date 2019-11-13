import fire
import os
import glob
from joblib import Parallel, delayed, cpu_count
from tqdm import tqdm


def write_text(file_path: str, text: str):
    with open(file_path, 'w') as w:
        w.write(text)


def copy_file(in_path: str, out_path: str):
    with open(in_path, 'rb') as rb:
        with open(out_path, 'wb') as wb:
            wb.write(rb.read())


def prepare_kss(master_path: str, text_file_name: str = 'transcript.v.1.3.txt'):
    """
    This function to handle script of KSS Dataset.
    url : https://www.kaggle.com/bryanpark/korean-single-speaker-speech-dataset
    :param master_path: kss directory
    :param text_file_name: script path
    """
    # prepare directories
    glob_path = os.path.join(master_path, '*', '*.wav')
    wave_path = os.path.join(master_path, 'waves')
    text_path = os.path.join(master_path, 'texts')

    os.makedirs(wave_path, exist_ok=True)
    os.makedirs(text_path, exist_ok=True)

    # copy waves
    print('Copy waves ...')
    wave_list = glob.glob(glob_path)
    wave_out_paths = [os.path.join(wave_path, os.path.basename(wave_file)) for wave_file in wave_list]
    Parallel(n_jobs=cpu_count() // 2)(
        delayed(copy_file)(in_path, out_path)
        for in_path, out_path in tqdm(zip(wave_list, wave_out_paths))
    )

    # prepare texts
    # read text
    print('Read text files ...')
    text_file_list = []
    with open(os.path.join(master_path, text_file_name), 'r') as r:
        for line in r.readlines():
            filename, _, text, *_ = line.split('|')
            filename = filename.split('/')[1].split('.')[0] + '.txt'
            text_file_list.append((filename, text))

    # write all
    print('Write text files ...')
    Parallel(n_jobs=cpu_count() // 2)(
        delayed(write_text)(os.path.join(text_path, filename), text)
        for filename, text in tqdm(text_file_list)
    )


if __name__ == '__main__':
    fire.Fire(prepare_kss)
