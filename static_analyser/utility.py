from myglobals import DEBUG, debug_read1_file, debug_logs, NOT_UTF_8

# -------------------------------
# ----- character functions -----
# -------------------------------

def ischar(c:str) -> bool:
    return len(c) == 1


def isalpha(c:str) -> bool:
    if not ischar(c):
        return False
    elif ord('A') <= ord(c) <= ord('Z') or ord('a') <= ord(c) <= ord('z') or c == '_':
        return True
    else:
        return False


def isnum(c:str) -> bool:
    if not ischar(c):
        return False
    elif ord('0') <= ord(c) <= ord('9'):
        return True
    else:
        return False


def isalnum(c:str) -> bool:
    if isalpha(c) or isnum(c):
        return True
    else:
        return False


def iswhitespace(c:str) -> bool:
    if not ischar(c):
        return False
    elif c == ' ' or c == '\t' or c == '\n':
        return True
    else:
        return False


# ----------------------------------
# ----- file related functions -----
# ----------------------------------

import re
from typing import List, IO

def getcurpos(fin:IO) -> int:
    return fin.tell()


def setcurpos(fin:IO, pos:int) -> None:
    fin.seek(pos)


def read1(fin:IO, debug:bool=DEBUG) -> str:
    try:
        c = fin.read(1)
    except:
        print('Warning: character unsupported by \'utf-8\' codec encountered.')
        c = NOT_UTF_8

    if debug:
        with open(debug_read1_file, 'a+') as debug:
            debug.write(c)

    return c


def debug(fin:IO, message:str, execute:bool=DEBUG) -> None:
    if not execute:
        return

    curpos = getcurpos(fin)
    with open(debug_logs, 'a+') as debug:
        debug.write('[' + str(curpos) + '] : ' + message  + '\n')


def clear_file(filepath:str) -> None:
    with open(filepath, 'w+'):
        pass


def peek1(fin:IO) -> str:
    curpos = getcurpos(fin)
    try:
        c = fin.read(1)
    except:
        print('Warning: character unsupported by \'utf-8\' codec encountered.')
        c = NOT_UTF_8
    setcurpos(fin, curpos)
    return c


def skip1(fin:IO) -> None:
    fin.read(1)
    return


def skipwhitespaces(fin:IO) -> str:
    whitespaces = ''
    c = peek1(fin)

    while iswhitespace(c):
        whitespaces += c
        read1(fin)
        c = peek1(fin)

    return whitespaces


def extract_word(fin:IO) -> str:
    word = ''
    c = peek1(fin)
    while isalnum(c):
        word += c
        read1(fin)
        c = peek1(fin)
    return word


def write(fout:IO, to_write:str) -> None:
    fout.write(to_write)


def mysplit(string:str) -> List[str]:
    return re.split(r'[/\\]', string)


def get_filename_from_path(filepath:str) -> str:
    return mysplit(filepath)[-1]
