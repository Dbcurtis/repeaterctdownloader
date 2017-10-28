#!/usr/bin/env python3
""" removeTrailingSpacesonLines
it does what its name is.
Intended to be used on .py files, but should be usable for any text file
"""
import os

def __main():
    """TBD"""
    files_in_dir = [n for n in os.listdir(".")]
    pyfiles = [n for n in files_in_dir if n.endswith(".py")]
    txtfiles = [n for n in files_in_dir if n.endswith(".txt")]

    def __jj(line):
        return line.rstrip() + '\n'

    for pyf in pyfiles:
        lines = None
        with open(pyf, 'r', encoding='utf-8') as ifile:
            lines = ifile.readlines()
        newlines = [__jj(l) for l in lines]
        with open(pyf, 'w', encoding='utf-8') as ofile:
            ofile.writelines(newlines)

        print('processed %s' % pyf)

if __name__ == '__main__':
    __main()
    print('done!')
