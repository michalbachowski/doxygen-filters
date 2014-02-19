#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
from pprint import pprint
"""
Source:
    http://stackoverflow.com/questions/4325224/doxygen-how-to-describe-class-member-variables-in-php
"""

def main():
    source = read_source(sys.argv[1])
    source = fix_class_members(source)
    source = fix_function_array_type(source)
    source = fix_function_variables(source)
    return source

def read_source(path):
    with open(path) as f:
        return f.read()

def fix_class_members(source):
    """
    Makes the following:
        /**
        * @var VarType
        * @brief Description
        */
        (public|protected|private|var) $paramName = 'value';

    recongizable as valid variable documentation
    """
    def cb(matches):
        print matches.groups()
        return ''
    return re.sub(
        r'(?mis)\@var\s+([^\s]+)(.+?)\*/\s+(var|public|protected|private)\s+(\$[^\s;=]+)',
        r'\2*/ \3 \1 \4',
        source
    )

def fix_function_array_type(source):
    """
    Change the following:
        /** @param VarType[] $pParamName Description **/
        function name(array $pParamName) {

    Into:
        /** @param array $pParamName Description **/
        function name(VarType[] $pParamName) {
    """
    return re.sub(
        r'(?s)\@param\s+([^\s]+)\[\]\s+(\$[^\s]+)\s+([^/]+)/\s+(public|protected|private)?\s+function\s+([^\s]+)\s*\(([^)]*)array\s+\2([^)]*)\)(\s+){',
        r'@param array \2 \3/ \4 function \5 (\6 \1[] \2\7)\8{',
        source
    )

def fix_function_variables(source):
    """
    Change the following:
        /** @param (bool|int|float|double|string) $pParamName Description **/
        function name($pParamName) {

    Into:
        /** @param (bool|int|float|double|string) $pParamName Description **/
        ReturnType function name((bool|int|float|double|string) $pParamName) {
    """

    def callback(matches):
        pprint(matches.groups())
        lines = matches.group(2).splitlines()
        return_arg_type = ''
        params = []

        for line in lines:
            line = line.strip("\t *")
            if '@return' in line:
                return_arg_type = filter(None, line.split(' ')).pop()
                continue

            if '@param' not in line:
                continue
            tmp = filter(None, line.split(' '))
            # remove '@param'
            tmp.pop(0)
            arg_type = tmp.pop(0)
            arg_name = tmp.pop(0)
            params.append(arg_type + ' ' + arg_name)

        output = matches.group(1) + ','.join(params) + matches.group(3)
        if return_arg_type:
            output = output.replace('function', return_arg_type + ' function')
        return output

    return re.sub(r"""(?misx)                   # multiline, ignorecase, dottal, verbose
                (                               # start first group (comment + function name + opening bracket)
                    /\*\*(.+?)\*/\s+            # match comment
                    (?:public|protected|private)# match visibility qualifier
                    \s+function\s+[^\s]+\s*\(   # match "function" + method name + "("
                )                               # end first group
                (?:[^\)]*?)?                    # match function attributes
                (\)\s*[{;]?\s*$)                # match closing bracked ")" + opening "{" or ";" (for interfaces)
                """,
                callback,
                source)

if '__main__' == __name__:
    print main()
