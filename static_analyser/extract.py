from typing import Any, IO
from utility import read1, extract_word, isalpha, skipwhitespaces, skip1until, debug

def stackpush(fin:IO, stack:list, item:Any) -> None:
    stack.append(item)
    debug(fin, stack)


def stackpop(fin:IO, stack:list) -> Any:
    popped = '[Empty]'
    if len(stack) > 0:
        popped = stack.pop()
    debug(fin, stack)
    return popped


def queuepush(queue:list, item:Any) -> None:
    queue.append(item)


def queuepop(queue:list) -> Any:
    popped = '[Empty]'
    if len(queue) > 0:
        popped = queue.pop()
    return popped


def extract_cpp(in_filename:str):
    ''' Function to extract list of functions in a class
        and the position of their definition if found. '''

    namespace_stack = []
    class_stack = []
    block_count = 0
    
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