import preprocess as pp

testfiles = [
    '../testfiles/Controller.h',
    '../testfiles/Controller.cpp',
]

pp.strip_cpp(in_filepath=testfiles[0],
             out_filepath='../__temp__.cpp',
             single_line_comments=True,
             multiline_comments=True,
             strings=True,
             ppd_includes=True,
             ppd_defines=True,
             skip_newline=True,
             qt_macros=True)