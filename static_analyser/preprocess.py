# -------------------
# ----- globals -----
# -------------------

DEBUG = False
debug_read1_file = '../debug_read1.cpp'
debug_logs = '../debug.txt'

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


NOT_UTF_8 = '[?]'


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


# --------------------------------------------
# ----- function to pre-process the file -----
# --------------------------------------------

def strip_stuff(in_filepath:str, 
                out_filepath:str,
                single_line_comments:bool=True,
                multiline_comments:bool=True, 
                strings:bool=True,
                ppd_includes:bool=True,
                ppd_defines:bool=True,
                skip_newline:bool=False,
                qt_macros=True) -> None:

    QT_Macros = ['Q_OBJECT', 'Q_ENUM']

    clear_file(debug_logs)
    clear_file(debug_read1_file)

    with open(out_filepath, 'w+') as fout:
        with open(in_filepath) as fin:
            while True:
                c = read1(fin)
                if not c:
                    break
                
                # possible comment ahead
                elif c == '/':
                    debug(fin, 'possible comment ahead')
                    c = peek1(fin)

                    # single line comment
                    if c == '/':
                        read1(fin)
                        debug(fin, 'single line comment starts')
                        
                        if not single_line_comments:
                            write(fout, '//')
                        while c != '\n' and not not c:
                            c = read1(fin)
                            if c == '\n' and not skip_newline:
                                write(fout, '\n')
                            elif not single_line_comments:
                                write(fout, c)
                        debug(fin, 'single line comment ends')

                    # multi-line comment 
                    elif c == '*':
                        read1(fin)
                        debug(fin, 'multiline comment starts')
                        if not multiline_comments:
                            write(fout, '/*')
                        while True:
                            c = read1(fin)
                            if not multiline_comments:
                                write(fout, c)
                            if c == '*':
                                c = peek1(fin)
                                if c == '/':
                                    read1(fin)
                                    if not multiline_comments:
                                        write(fout, '*/')
                                    debug(fin, 'multiline comment exited due to  */')
                                    break
                                else:
                                    if not multiline_comments:
                                        write(fout, '*')
                            elif c == '\n':
                                if not skip_newline:
                                    write(fout, c)
                            elif not c:
                                debug(fin, 'multiline comment exited due to EOF')
                                break

                    # false alarm
                    else:
                        debug(fin, 'false alarm')
                        write(fout, '/' + c)

                # string
                elif c == '"':
                    debug(fin, 'string starts')

                    if not strings:
                        write(fout, '"')
                    
                    debug(fin, 'entering infinite loop')
                    while True:
                        c = read1(fin)
                        if not strings:
                            write(fout, c)
                        if c == '\\':
                            c = read1(fin)
                            if not strings:
                                write(fout, '\\' + c)
                        elif c == '"':
                            if not strings:
                                write(fout, '"')
                            debug(fin, 'exiting infinite loop')
                            debug(fin, 'string ends')
                            break
                        elif not c:
                            if not strings:
                                write(fout, '"')
                            debug(fin, 'exiting infinite loop')
                            debug(fin, 'EOF')
                            break
                
                # preprocessor directives
                elif c == '#':
                    debug(fin, 'possible preprocessor directive ahead')

                    curpos = getcurpos(fin)

                    whitespaces = skipwhitespaces(fin)
                    word = extract_word(fin)
                    
                    # include directive
                    if word == 'include':
                        if not ppd_includes:
                            write(fout, '#' + whitespaces + 'include')
                        while True:
                            c = read1(fin)
                            if c == '\\':
                                c = read1(fin)
                                if not ppd_includes:
                                    write(fout, '\\' + c)
                            elif c == '\n':
                                if not skip_newline:
                                    write(fout, '\n')
                                break
                            elif not ppd_includes:
                                write(fout, c)

                    # define directive
                    elif word == 'define':
                        if not ppd_defines:
                            write(fout, '#' + whitespaces + 'define')
                        while True:
                            c = read1(fin)
                            if c == '\\':
                                c = read1(fin)
                                if not ppd_defines:
                                    write(fout, '\\' + c)
                            elif c == '\n':
                                if not skip_newline:
                                    write(fout, '\n')
                                break
                            elif not ppd_defines:
                                write(fout, c)
                    
                    # false alarm
                    else:
                        debug(fin, 'false alarm -- resetting position')
                        setcurpos(fin, curpos)
                        write(fout, '#')

                # possible qt enum
                elif isalpha(c):
                    word = c + extract_word(fin)

                    if word in QT_Macros:
                        if not qt_macros:
                            write(fout, word)
                    else:
                        write(fout, word)

                # meets no specified category
                else:
                    write(fout, c)

