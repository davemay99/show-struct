#!/usr/bin/env python
# vim: ts=4 sw=4 et

# https://github.com/ilyash/show-struct.git
from __future__ import unicode_literals
import argparse
import collections
import json
import sys


class Outliner(object):

    def __init__(self):
        self.paths = {}
        self.values_for_path = collections.defaultdict(dict)

    def _outline(self, data, path):
        p = ''.join(path)
        self.paths[p] = True
        if isinstance(data, dict):
            if not data:
                self.values_for_path[p]['(Empty hash)'] = True
            for k, v in data.items():
                if "." in k or " " in k or "/" in k:
                    newpath = '["' + k + '"]'
                    if len(path) == 0:
                        newpath = '.' + newpath
                else:
                    newpath = '.' + k
                self._outline(v, path + [newpath])
            return
        if isinstance(data, list):
            for v in data:
                self._outline(v, path + ['[]'])

            sentence = '(Array of {0} elements)'.format(len(data))
            self.values_for_path[p][sentence] = True
            return
        # scalar assumed
        self.values_for_path[p][data] = True

    def outline(self, data):
        self._outline(data, [])
        del self.paths['']

        ret = []
        for path in sorted(self.paths):
            ret.append({
                'path': path,
                'values': sorted(self.values_for_path[path].keys())
            })
        return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='show_struct.py', description='Show structure of JSON file')
    parser.add_argument(
        'file', default='-', nargs='?',
        help="The filename to read or '-' to read from stdin.  Defaults to '-'")
    args = parser.parse_args()

    if args.file == "-":
        if sys.stdin.isatty():
            parser.print_help()
            parser.exit(1)
            # parser.error("Must provide either a filename or pipe to stdin")

        try:
            rawdata = sys.stdin.read()
            if len(rawdata) == 1:
                parser.error("Stdin cannot be empty if no file specified")

            data = json.loads(rawdata)
        except Exception as ex:
            parser.error(ex)

    else:
        with open(args.file) as f:
            data = json.loads(f.read())

    outline = Outliner().outline(data)
    for path in outline:
        l = len(path['values'])
        if l == 0:
            print(path['path'])
            continue
        if l == 1:
            print("{0} -- {1}".format(path['path'], path['values'][0]))
            continue
        print("{0} -- {1} .. {2} ({3} unique values)".format(
            path['path'],
            path['values'][0],
            path['values'][-1],
            l,
        ))
