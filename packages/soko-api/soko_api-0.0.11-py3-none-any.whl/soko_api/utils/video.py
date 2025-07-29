import logging
import os
import subprocess
import traceback

from .files import uncompress_sequence, get_sequences


def convert(path, quality=15, fps=25):
    mp4_path = None

    _path = path.replace('/', '\\')

    _startFileName = sorted([f for f in os.listdir(os.path.dirname(_path)) if not "_filelist.txt" in f])[0]

    _outputFileName = _startFileName.split('.')[0]

    _newDir = os.path.dirname(_path) + "_mp4"

    try:
        os.makedirs(_newDir)
    except:
        pass

    _newPath = os.path.sep.join([_newDir, '{}.mp4'.format(_outputFileName)])

    number = 1
    while os.path.exists(_newPath):
        _newPath = os.path.sep.join([_newDir, '{}_{}.mp4'.format(_outputFileName, number)])
        number += 1

    if os.path.exists(_newPath):
        raise Exception("Output file alredy exists.")

    _video = (".mp4", ".mov", ".avi", ".mpeg")
    _args = ["ffmpeg"]
    _filelist = None
    if _path.endswith(_video):
        _args += ["-i", _path,
                  "-vf",
                  "crop=trunc(iw/2)*2:trunc(ih/2)*2:(in_w-out_w)/2:(in_h-out_h)/2",
                  "-preset", "slow",
                  "-crf", "{quality}".format(quality=quality),
                  "-r", "{fps}".format(fps=fps), _newPath]
    else:
        _files = uncompress_sequence(_path)
        _filelist = os.path.dirname(_path) + "\_filelist.txt"
        with open(_filelist, "wb") as outfile:
            for filename in _files:
                outfile.write(f"file '{filename}'\n".encode())

        if _path.endswith(".exr"):
            _args += ["-y", "-apply_trc", "iec61966_2_1",
                      "-r",
                      "{fps}".format(fps=fps),
                      "-f",
                      "concat",
                      "-safe", "0", "-i", _filelist,
                      "-vcodec",
                      "libx264",
                      "-preset", "slow",
                      "-crf", "{quality}".format(quality=quality),
                      "-vf",
                      "crop=trunc(iw/2)*2:trunc(ih/2)*2:(in_w-out_w)/2:(in_h-out_h)/2,scale=in_range=full:in_color_matrix=bt709:out_range=tv:out_color_matrix=bt709, format=yuv420p",
                      _newPath]
        else:
            _args += ["-y", "-r", "{fps}".format(fps=fps), "-f", "concat", "-safe", "0", "-i", _filelist,
                      "-vcodec",
                      "libx264",
                      "-preset", "slow",
                      "-crf", "{quality}".format(quality=quality),
                      "-vf",
                      "crop=trunc(iw/2)*2:trunc(ih/2)*2:(in_w-out_w)/2:(in_h-out_h)/2,colormatrix=bt601:bt709, format=yuv420p",
                      _newPath]

    try:
        subprocess.check_output(_args)
        mp4_path = _newPath
    except subprocess.CalledProcessError as e:
        raise Exception(e.output)
    finally:
        if _filelist:
            try:
                os.remove(_filelist)
            except:
                logging.error(traceback.format_exc())

    return mp4_path


def convert_to_prores(path, profile=5, fps=25, convert_linear_to_sRGB=False, alpha=False):
    mov_path = None

    _path = path.replace('/', '\\')

    _startFileName = sorted([f for f in os.listdir(os.path.dirname(_path)) if not "_filelist.txt" in f])[0]

    _outputFileName = _startFileName.split('.')[0]

    _newDir = os.path.dirname(_path) + "_prores"

    try:
        os.makedirs(_newDir)
    except:
        pass

    _newPath = os.path.sep.join([_newDir, '{}.mov'.format(_outputFileName)])

    number = 1
    while os.path.exists(_newPath):
        _newPath = os.path.sep.join([_newDir, '{}_{}.mov'.format(_outputFileName, number)])
        number += 1

    if os.path.exists(_newPath):
        raise Exception("Output file alredy exists.")

    _args = ["ffmpeg"]
    _filelist = None

    _files = uncompress_sequence(_path)
    _filelist = os.path.dirname(_path) + "\_filelist.txt"
    with open(_filelist, "wb") as outfile:
        for filename in _files:
            outfile.write(f"file '{filename}'\n".encode())

    if profile == 0:
        pix_fmt = ""
    if profile == 1:
        pix_fmt = ""
    if profile == 2:
        pix_fmt = "-pix_fmt yuv422p10le"
    if profile == 3:
        pix_fmt = "-pix_fmt yuv422p10le"
    if profile == 4:
        if alpha:
            pix_fmt = "-pix_fmt yuva444p10le"
        else:
            pix_fmt = "-pix_fmt yuv444p10le"
    if profile == 5:
        if alpha:
            pix_fmt = "-pix_fmt yuva444p12le"
        else:
            pix_fmt = "-pix_fmt yuv444p12le"

    if _path.endswith(".exr"):
        _args += ["-y",
                  "-r",
                  "{fps}".format(fps=fps),
                  "-f",
                  "concat",
                  "-safe", "0", "-i", _filelist,
                  "-c:v",
                  "prores_ks", "-profile:v", "{profile}".format(profile=profile),
                  "-vf",
                  "crop=trunc(iw/2)*2:trunc(ih/2)*2:(in_w-out_w)/2:(in_h-out_h)/2,scale=in_range=full:in_color_matrix=bt709:out_range=tv:out_color_matrix=bt709 {}".format(
                      pix_fmt),
                  "-c:a", "pcm_s16le",
                  _newPath]

    if convert_linear_to_sRGB:
        _args = _args[:2] + ["-apply_trc", "iec61966_2_1"] + _args[2:]

    try:
        subprocess.check_output(_args)
        mov_path = _newPath
    except subprocess.CalledProcessError as e:
        raise Exception(e.output)
    finally:
        if _filelist:
            try:
                os.remove(_filelist)
            except:
                logging.error(traceback.format_exc())

    return mov_path


def convert_to_sequence(path, target_format="jpg", convert_linear_to_sRGB=False):
    new_path = None

    _path = path.replace('/', '\\')

    _startFileName = sorted([f for f in os.listdir(os.path.dirname(_path)) if not "_filelist.txt" in f])[0]

    _outputFileName = _startFileName.split('.')[0]

    _newDir = os.path.dirname(_path) + "_{}".format(target_format)

    try:
        os.makedirs(_newDir)
    except:
        pass

    _args = ["ffmpeg"]

    if os.path.isfile(_path):
        # video

        _newPath = os.path.sep.join([_newDir, '{}.%04d.{}'.format(_outputFileName, target_format)])

        # number = 1
        # while os.path.exists(_newPath):
        #     _newPath = os.path.sep.join([_newDir, '{}_{}.%04d.{}'.format(_outputFileName, number, target_format)])
        #     number += 1

        if os.path.exists(_newPath):
            raise Exception("Output file alredy exists.")

        _args += ["-i", _path,
                  _newPath]

        try:
            subprocess.check_output(_args)
            new_path = _newPath
        except subprocess.CalledProcessError as e:
            raise Exception(e.output)

    else:
        _filelist = None
        _files = uncompress_sequence(_path)

        converted_files = []
        for file_path in _files:
            _args = ["ffmpeg"]

            _frame = file_path.split(".")[-2]
            _newPath = os.path.sep.join([_newDir, '{}.{}.{}'.format(_outputFileName, _frame, target_format)])

            number = 1
            while os.path.exists(_newPath):
                _newPath = os.path.sep.join([_newDir, '{}_{}.{}.{}'.format(_outputFileName, number, _frame, target_format)])
                number += 1

            if os.path.exists(_newPath):
                raise Exception("Output file alredy exists.")

            if file_path.endswith(".exr") or convert_linear_to_sRGB:
                _args += ["-y", "-apply_trc", "iec61966_2_1", "-i", file_path,
                          _newPath]
            else:
                _args += ["-i", file_path,
                          _newPath]

            try:
                subprocess.check_output(_args)
            except subprocess.CalledProcessError as e:
                raise Exception(e.output)

            converted_files.append(_newPath)

        new_path = get_sequences(converted_files)
        if len(new_path):
            new_path = new_path[0]

    return new_path