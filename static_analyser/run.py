import preprocess as pp
import extract as ex

testfiles = [
    '../testfiles/Controller.h',
    '../testfiles/Controller.cpp',
]

temp = '../__temp__.cpp'

# pp.strip_cpp(in_filepath=testfiles[0],
#              out_filepath=temp,
#              single_line_comments=True,
#              multiline_comments=True,
#              strings=True,
#              ppd_includes=True,
#              ppd_defines=True,
#              skip_newline=True,
#              qt_macros=True)

ex.extract_cpp(in_filename=temp)