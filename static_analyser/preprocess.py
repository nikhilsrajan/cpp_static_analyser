# -------------------------------
# ----- character functions -----
# -------------------------------

def ischar(c:str) -> bool:
    return len(c) == 1


def isalpha(c:str) -> bool:
    if not ischar(c):
        return False
    elif (ord('A') <= ord(c) <= ord('Z')) or (ord('a') <= ord(c) <= ord('z')) or c == '_':
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
from typing import List

def getcurpos(fin) -> int:
    return fin.tell()


def setcurpos(fin, pos:int) -> None:
    fin.seek(pos)


NOT_UTF_8 = '[?]'


def read1(fin) -> str:
    try:
        c = fin.read(1)
    except:
        print('Warning: character unsupported by \'utf-8\' codec encountered.')
        c = NOT_UTF_8
    return c


def peek1(fin) -> str:
    curpos = getcurpos(fin)
    try:
        c = fin.read(1)
    except:
        print('Warning: character unsupported by \'utf-8\' codec encountered.')
        c = NOT_UTF_8
    setcurpos(fin, curpos)
    return c


def skip1(fin) -> None:
    fin.read(1)
    return


def write(fout, to_write:str) -> None:
    fout.write(to_write)


def mysplit(string:str) -> List[str]:
    return re.split(r'[/\\]', string)


def get_filename_from_path(filepath:str) -> str:
    return mysplit(filepath)[-1]


# --------------------------------------------
# ----- function to pre-process the file -----
# --------------------------------------------

def strip_comments(in_filepath:str, out_filepath:str) -> None:
    with open(out_filepath, 'w+') as fout:
        with open(in_filepath) as fin:
            while True:
                c = read1(fin)
                if not c:
                    break
                elif c == '/':
                    c = read1(fin)
                    if c == '/':                # single line comment
                        while c != '\n':
                            c = read1(fin)
                        write(fout, c)
                    elif c == '*':              # multi-line comment
                        while True:
                            c = read1(fin)
                            if c == '*':
                                c = peek1(fin)
                                if c == '/':
                                    skip1(fin)
                                    break
                            elif c == '\n':
                                write(fout, c)
                    else:
                        write(fout, '/' + c)
                elif c == '"':                  # strings
                    write(fout, c)
                    while True:
                        c = read1(fin)
                        write(fout, c)
                        if c == '\\':
                            write(fout, read1(fin))
                        elif c == '"':
                            break
                else:
                    write(fout, c)

