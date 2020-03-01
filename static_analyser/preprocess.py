from myglobals import debug_logs, debug_read1_file
from utility import clear_file, read1, debug, peek1, write, skip1, setcurpos, getcurpos, skipwhitespaces, extract_word, isalpha

# --------------------------------------------
# ----- function to pre-process the file -----
# --------------------------------------------

def strip_cpp(in_filepath:str, 
              out_filepath:str,
              single_line_comments:bool=True,
              multiline_comments:bool=True, 
              strings:bool=True,
              ppd_includes:bool=True,
              ppd_defines:bool=True,
              skip_newline:bool=False,
              qt_macros=True) -> None:
    ''' Function to remove certain tokens from the cpp file '''

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
                                if c == '/':    # /*
                                    read1(fin)
                                    if not multiline_comments:
                                        write(fout, '*/')
                                    debug(fin, 'multiline comment exited due to  */')
                                    
                                    # if there is newline right after multiline comment, ignore it
                                    if skip_newline:
                                        c = peek1(fin)
                                        if c == '\n':
                                            skip1(fin)
                                    
                                    break       # */
                                
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

