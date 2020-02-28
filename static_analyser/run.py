import preprocess as pp

testfiles = [
    '../testfiles/Controller.h',
    '../testfiles/Controller.cpp',
]

pp.DEBUG = False
pp.strip_stuff(in_filepath=testfiles[1],
               out_filepath='../__temp__.cpp',
               single_line_comments=True,
               multiline_comments=True,
               strings=True,
               ppd_includes=True,
               ppd_defines=False,
               skip_newline=True)