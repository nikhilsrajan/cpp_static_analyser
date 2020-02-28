import preprocess as pp

testfiles = [
    'testfiles/Controller.h',
    'testfiles/Controller.cpp',
]

pp.strip_comments(testfiles[0], '__temp__.cpp')