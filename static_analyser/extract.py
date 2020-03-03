from typing import Any, IO
from utility import read1, extract_word, isalpha, skipwhitespaces, skip1until, debug, peek1, skip1, getcurpos, iswhitespace, isalnum

def stackpush(fin:IO, stack:list, item:Any) -> None:
    stack.append(item)
    debug(fin, stack)


def stackpop(fin:IO, stack:list) -> Any:
    popped = '[Empty]'
    if len(stack) > 0:
        popped = stack.pop()
    debug(fin, stack)
    return popped

def stackpopN(fin:IO, stack:list, N:int) -> None:
    debug(fin, 'stackpopN')
    while N != 0:
        N -= 1
        stackpop(fin, stack)

def queuepush(queue:list, item:Any) -> None:
    queue.append(item)


def queuepop(queue:list) -> Any:
    popped = '[Empty]'
    if len(queue) > 0:
        popped = queue.pop()
    return popped

def normalise_spaces(string:str) -> str:
    ''' normalise spaces '''
    normalised = ''
    prev_char = ''
    for c in string:
        if iswhitespace(c):
            if prev_char == '':
                pass
            else:
                prev_char = ' '
        elif not isalnum(c):
            normalised += c
            prev_char = c
        else:
            if iswhitespace(prev_char):
                normalised += ' '
            normalised += c
            prev_char = c

    return normalised

def clean_function_parameters(function_params:str) -> str:
    ''' clean the function parameters string captured to meet a standard format
        useful only in function declaration and definition. '''
    comma_splits = function_params.split(',')
    normalised_comma_splits = []

    for c_split in comma_splits:
        normalised_comma_splits.append(normalise_spaces(c_split))

    default_values_removed = []
    for nc_split in normalised_comma_splits:
        default_values_removed.append(nc_split.split('=')[0])
    
    variable_rms = []
    for dv_rem in default_values_removed:
        variable_rms.append(' '.join(dv_rem.split(' ')[0:-1]))
    
    cleaned_string = ', '.join(variable_rms)

    return cleaned_string

def extract_cpp(in_filename:str):
    ''' Function to extract list of functions in a class
        and the position of their definition if found. '''

    namespace_stack = []
    class_stack = []
    block_count = 0
    
    extracts = dict()
    
    with open(in_filename, 'r') as fin:
        while True:
            c = read1(fin)
            if not c:
                break
            
            elif c == '{':
                block_count += 1

            elif c == '}':
                if block_count > 0:
                    block_count -= 1
                else:
                    stackpop(fin, namespace_stack)
                    stackpop(fin, class_stack)

            elif isalpha(c):
                word = c + extract_word(fin)

                if word == 'namespace':
                    skipwhitespaces(fin)
                    word = extract_word(fin)
                    skipwhitespaces(fin)
                    c = read1(fin)

                    if c == ';':
                        ''' using namespace word; '''

                    elif c == '{':
                        ''' namespace word { ... '''
                        stackpush(fin, namespace_stack, word)
                
                elif word == 'class':
                    skipwhitespaces(fin)
                    word = extract_word(fin)
                    skipwhitespaces(fin)
                    c = read1(fin)

                    if c == ';':
                        ''' class word; '''
                    
                    elif c == ':':
                        ''' class word : public base { ... '''
                        c = read1(fin)
                        skip1until(fin, '{')
                        stackpush(fin, namespace_stack, word)
                        stackpush(fin, class_stack, word)

                    elif c == '{':
                        ''' class word { ... '''
                        stackpush(fin, namespace_stack, word)
                        stackpush(fin, class_stack, word)
                
                else:
                    skipwhitespaces(fin)
                    c = read1(fin)

                    if c == ':':
                        ''' word: '''
                        c = peek1(fin)
                        if c == ':':
                            ''' word:: '''
                            stackpush(fin, namespace_stack, word)
                            push_count = 1
                            while True:
                                skipwhitespaces(fin)
                                c = read1(fin)
                                
                                if c == ';':
                                    ''' word::word::word; '''
                                    stackpopN(fin,namespace_stack, push_count)
                                    break

                                elif c == '(':
                                    function_params = '('
                                    param_count = 1
                                    while param_count != 0:
                                        c = read1(fin)
                                        function_params += c
                                        if c == '(':
                                            param_count += 1
                                        elif c == ')':
                                            param_count -= 1
                                    skipwhitespaces(fin)
                                    c = read1(fin)
                                    
                                    if c == ';':
                                        ''' word::word::word(...);
                                            Function being declared but with namespace colons
                                            That is function being declared outside the class
                                            But such a case shouldn't be possible ... '''
                                        print('Warning: Undefined case 1 encountered.')
                                        exit(1)

                                    elif c == '{':
                                        ''' word::word::word(...) { ... '''
                                        if len(class_stack) > 0:
                                            ''' function is being declared with namespace colons
                                                but this is happening inside a class block
                                                But such a case shouldn't be possible ... '''
                                            print('Warning: Undefined case 2 encountered.')
                                            exit(1)
                                        
                                        elif len(class_stack) == 0:
                                            ''' function is being declared with namespace colons
                                                but this is happening inside a class block '''
                                            function_name = stackpop(fin, namespace_stack)
                                            push_count -= 1
                                            inner_block_count = 1
                                            curpos = getcurpos(fin)


                                    elif c == ':':
                                        c = peek1(fin)
                                        if c == ':':
                                            ''' word:: '''
                                            skip1(fin)
                                            skipwhitespaces(fin)
                                            c = peek1(fin)
                                            if not isalpha(c):
                                                ''' word::<not word> '''
                                                print('Warning: Undefined case 3 encountered.')
                                                exit(1)
                                            word = extract_word(fin)
                                            stackpush(fin, namespace_stack, word)
                                            push_count += 1

                                        else:
                                            ''' word : '''
                                            print('Warning: Undefined case 4 encountered.')
                                            exit(1)
