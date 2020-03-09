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
    double_colon_push_count = 0
    
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
                
                elif word == 'class' or word == 'struct':
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

                    if c == '(':
                        ''' word ( '''
                        function_name = word
                        function_params = ''
                        param_count = 1
                        while param_count != 0:
                            c = read1(fin)
                            if c == '(':
                                param_count += 1
                            elif c == ')':
                                param_count -= 1
                            if param_count != 0:
                                function_params += c
                        function_params = clean_function_parameters(function_params)
                        skipwhitespaces(fin)
                        if len(class_stack) == 0:
                            ''' function declaration or defintion is not a member of a class '''
                            c = read1(fin)
                            if c == ';':
                                ''' non class member function declaration '''
                                pass
                            elif c == '{':
                                ''' non class member function definition '''
                                inner_block_count = 1
                                while inner_block_count != 0:
                                    c = read1(fin)
                                    if c == '{':
                                        inner_block_count += 1
                                    elif c == '}':
                                        inner_block_count -= 1

                        elif len(class_stack) > 0:
                            ''' function declaration or definition is a member of a class '''
                            print(function_name, function_params)

                            c = read1(fin)
                            if c == ';':
                                ''' member function declaration '''
                            
                            elif c == '{':
                                ''' member function definition '''
                                curpos = getcurpos(fin)
                                inner_block_count = 1
                                while inner_block_count != 0:
                                    c = read1(fin)
                                    if c == '{':
                                        inner_block_count += 1
                                    elif c == '}':
                                        inner_block_count -= 1

                    elif c == ':':
                        ''' word: '''
                        c = peek1(fin)
                        if c == ':':
                            ''' word:: '''
                            stackpush(fin, namespace_stack, word)
                            double_colon_push_count = 1
                            while True:
                                ''' loop to capture namespace colons '''
                                ''' word::word::word::word '''
                                skipwhitespaces(fin)
                                c = peek1(fin)
                                if c == ':':
                                    read1(fin)
                                    c = peek1(fin)
                                    if c == ':':
                                        read1(fin)
                                        word = extract_word(fin)
                                        stackpush(fin, namespace_stack, word)
                                        double_colon_push_count += 1
                                    else:
                                        break
