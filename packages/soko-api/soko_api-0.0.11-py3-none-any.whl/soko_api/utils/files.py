import os
import platform
import re
import subprocess
import traceback
import shutil


def copy_native_win(src, dst, buffer_size=10485760, preserve_file_date=True):
    """
    Copies a file to a new location.
    Much faster performance than Apache Commons due to use of larger buffer.

    :param src:    Source file path
    :param dst:    Destination file path
    :param buffer_size:    Buffer size to use during copy
    :param preserve_file_date:    Preserve the original file date
    """
    # Check to make sure destination directory exists. If it doesn't create the directory
    dst_parent, dst_file_name = os.path.split(dst)
    if not os.path.exists(dst_parent):
        os.makedirs(dst_parent)

    # Optimize the buffer for small files
    buffer_size = min(buffer_size, os.path.getsize(src))
    if buffer_size == 0:
        buffer_size = 1024

    if shutil._samefile(src, dst):
        raise shutil.Error("`{0}` and `{1}` are the same file".format(src, dst))
    for fn in [src, dst]:
        try:
            st = os.stat(fn)
        except OSError:  # File most likely does not exist
            pass
        else:  # XXX What about other special files? (sockets, devices...)
            if shutil.stat.S_ISFIFO(st.st_mode):
                raise shutil.SpecialFileError("`{}` is a named pipe".format(fn))
    with open(src, 'rb') as fsrc:
        with open(dst, 'wb') as fdst:
            shutil.copyfileobj(fsrc, fdst, buffer_size)

    if preserve_file_date:
        shutil.copystat(src, dst)


def copy(src, dst, buffer_size=10485760, preserve_file_date=True):
    """
    Copies a file to a new location.
    Much faster performance than Apache Commons due to use of larger buffer.

    :param src:    Source file path
    :param dst:    Destination file path
    :param buffer_size:    Buffer size to use during copy
    :param preserve_file_date:    Preserve the original file date
    """
    # Check to make sure destination directory exists. If it doesn't create the directory
    dst_parent, dst_file_name = os.path.split(dst)
    if not os.path.exists(dst_parent):
        os.makedirs(dst_parent)

    # Optimize the buffer for small files
    buffer_size = min(buffer_size, os.path.getsize(src))
    if buffer_size == 0:
        buffer_size = 1024

    if shutil._samefile(src, dst):
        raise shutil.Error("`{0}` and `{1}` are the same file".format(src, dst))
    for fn in [src, dst]:
        try:
            st = os.stat(fn)
        except OSError:  # File most likely does not exist
            pass
        else:  # XXX What about other special files? (sockets, devices...)
            if shutil.stat.S_ISFIFO(st.st_mode):
                raise shutil.SpecialFileError("`{}` is a named pipe".format(fn))
    with open(src, 'rb') as fsrc:
        with open(dst, 'wb') as fdst:
            shutil.copyfileobj(fsrc, fdst, buffer_size)

    if preserve_file_date:
        shutil.copystat(src, dst)


def xcopy(src, dst):
    try:
        os.makedirs(os.path.dirname(dst))
    except:
        pass

    if not os.path.isfile(dst):
        try:
            with open(dst, 'w') as f:
                pass
        except:
            pass
    try:
        subprocess.call(["xcopy", src.replace("/", "\\"), dst.replace("/", "\\"), "/Q/Y/F"])
    except:
        print(traceback.format_exc())


def get_windows_short_path(dos_path, encoding=None):
    if (not isinstance(dos_path, str) and
            encoding is not None):
        dos_path = dos_path.decode(encoding)
    path = os.path.abspath(dos_path).replace('/', '\\')
    if path.startswith(u"\\\\"):
        return u"\\\\?\\UNC\\" + path[2:]
    return u"\\\\?\\" + path


def trim_path_for_dropbox(path):
    res = path.replace(":", "").replace('\\', '/').replace('//', '/')

    if not res.startswith("/"):
        res = "/" + res

    return res


def uncompress_sequence_dropbox(path, files):
    path = path.replace("\\", "/").replace(":", "")

    frame_pattern = re.findall('%\\d+d', path)

    if frame_pattern:
        frame_pattern = int(frame_pattern[-1].replace("%", "").replace("d", ""))
    else:
        frame_pattern = None

    filtered_files = []
    if frame_pattern:
        _regex = "/".join(
            [os.path.dirname(path), re.sub('%\\d+d', '\\\d{%d}' % frame_pattern, os.path.basename(path))]).replace('//',
                                                                                                                   '/')
    else:
        _regex = path.replace('//', '/')
    for file in files:
        if re.search(_regex.lower().replace(" ", "_"), file.lower().replace(" ", "_")) and file.endswith(
                os.path.splitext(path)[-1]):
            filtered_files.append(file)

    return filtered_files


def alpha_numeric_sort(l):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def uncompress_sequence(path):
    path = path.replace("\\", "/")
    if os.path.isfile(path):
        return [path]

    listed_files = []
    for (d, r, f) in os.walk(os.path.dirname(path)):
        for file in f:
            listed_files.append(os.path.join(d, file).replace("\\", "/"))

    frame_pattern = re.findall('%\\d+d', path)

    if frame_pattern:
        frame_pattern = int(frame_pattern[-1].replace("%", "").replace("d", ""))
    else:
        return [path]

    files = []
    _basename = os.path.basename(path)
    _file_parts = list(os.path.splitext(_basename))
    _basename = "".join(_file_parts[:-1] + [_file_parts[-1].lower()])

    _regex = "/".join([os.path.dirname(path), re.sub('%\\d+d', '\\\d{%d}' % frame_pattern, _basename)])
    for file in listed_files:
        _file_parts = list(os.path.splitext(file))
        file = "".join(_file_parts[:-1] + [_file_parts[-1].lower()])
        if re.match(_regex, file):
            files.append(file)

    return alpha_numeric_sort(files)


def replace_between(start, end, replace, string):
    return string[:start] + replace + string[end:]


def starts_ends_with_any(suffixes, string):
    return string.endswith(suffixes) or string.startswith(suffixes)


def get_paddding(number):
    return '%0{}d'.format(number)


def get_sequences(files):
    DIGITS_RE = re.compile(r'\d+')
    separators = ('.', '_')

    separatorsEndRe = "[{}]+$".format("|".join(separators))
    separatorsStartRe = "^[{}]+".format("|".join(separators))

    sequences = []
    for file in files:
        if is_sequence2(file, files):
            dirname = os.path.dirname(file).replace('\\', '/')
            basename = os.path.basename(file)
            ext = os.path.splitext(file)[-1]

            digits = []

            for match in re.finditer(DIGITS_RE, basename):
                digits.append({
                    'match': match[0],
                    'start': match.start(),
                    'end': match.end()
                })

            frame = None
            if digits:
                frame = digits[-1]

            if frame:
                head = basename[0:frame["start"]]
                tail = basename[frame["end"]:]

                if starts_ends_with_any(separators, tail):
                    tail = re.sub(separatorsEndRe, '', tail)

                filename = head + '<frame_number>' + tail

                if filename:
                    key = filename.replace('<frame_number>', get_paddding(len(frame["match"])))

                    if starts_ends_with_any(separators, key):
                        key = re.sub(separatorsStartRe, '', key)
                else:
                    key = get_paddding(len(frame["match"]))
            else:
                key = basename + ext.lower()
            sequences.append('/'.join([dirname, key]))
        else:
            sequences.append(file.replace('\\', '/'))

    return list(set(sequences))


def is_sequence3(frames):
    if len(frames) == 1:
        return True
    a = [int(f) for f in frames]
    b = list(range(int(frames[0]), int(frames[-1])))
    return a == b


def is_sequence2(file, files):
    basename = os.path.basename(file)

    DIGITS_RE = re.compile(r'(\_|\.)((?!\d+>)\d+)')

    file_re = basename
    x = re.search(DIGITS_RE, file_re)
    while x:
        file_re = replace_between(x.start() + 1, x.end(), r'\d+', file_re)
        x = re.search(DIGITS_RE, file_re)

    p = re.compile(file_re.replace('.', '\.'))
    matches_num = 0
    for f in files:
        m = p.search(os.path.basename(f))

        if m:
            matches_num += 1

    if matches_num > 1:
        return True
    else:
        return False


def is_sequence(file, files):
    basename = os.path.basename(file)

    DIGITS_RE = re.compile(r'\d+')

    file_re = basename
    x = re.search(DIGITS_RE, file_re)
    while x:
        file_re = replace_between(x.start(), x.end(), r'\d+', file_re)
        x = re.search(DIGITS_RE, file_re)

    p = re.compile(file_re.replace('.', '\.'))
    matches_num = 0
    for f in files:
        m = p.search(os.path.basename(f))

        if m:
            matches_num += 1

    if matches_num > 1:
        return True
    else:
        return False

def get_component_path_for_current_os(paths):
    platform_name = str(platform.system()).lower()

    componentPath = None
    for _path in paths:
        if _path["os"] == platform_name:
            componentPath = _path['path']
            break

    return componentPath


def get_component_path_data_for_current_os(paths):
    platform_name = str(platform.system()).lower()

    componentData = None
    for _path in paths:
        if _path["os"] == platform_name:
            componentData = _path
            break

    return componentData