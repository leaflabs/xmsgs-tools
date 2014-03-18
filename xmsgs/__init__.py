#!/usr/bin/env python
"""
..
    Copyright: LeafLabs, LLC, 2014
    License: MIT License
    Author: bnewbold@leaflabs.com
    Date: Feb 2014

Module with helper functions for dealing with Xilinx ISE .xmsgs output log
files.
"""

from __future__ import print_function
import xml.etree.ElementTree as ET
import re
import os
import glob

DISABLE_COLOR = False

SEVERE_WARNINGS = [
    413,    # "N-bit expression truncated into M-bit target"
    ]

IGNORE_LIST = []
USE_TYPES = ['error', 'warning', 'severe', 'info']
SKIP_PATHS = []


def colorize(what, how, bold=False):
    """
    See also: https://pypi.python.org/pypi/colorama
    """
    if DISABLE_COLOR:
        return what

    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    BGRED = '\033[41m'
    BGGREEN = '\033[42m'
    BGYELLOW = '\033[43m'
    BGBLUE = '\033[44m'
    BGWHITE = '\033[47m'
    DIM = '\033[2m'
    ENDC = '\033[0m'

    if bold:
        BOLD = '\033[1m'
    else:
        BOLD = ''

    if how in ['red', 'error', 'fail']:
        return RED + BOLD + what + ENDC
    elif how in ['green', 'ok', 'success']:
        return GREEN + BOLD + what + ENDC
    elif how in ['magenta', 'severe']:
        return MAGENTA + BOLD + what + ENDC
    elif how in ['yellow', 'warning']:
        return YELLOW + BOLD + what + ENDC
    elif how in ['info']:
        return CYAN + BOLD + what + ENDC
    elif how in ['bgred']:
        return BGRED + BLACK + BOLD + what + ENDC
    elif how in ['bggreen']:
        return BGGREEN + BLACK + BOLD + what + ENDC
    elif how in ['bgwhite']:
        return BGWHITE + BLACK + BOLD + what + ENDC
    elif how in ['bgblue']:
        return BGBLUE + BLACK + BOLD + what + ENDC
    else:
        return BOLD + what + ENDC


def strlim(s, l):
    if len(s) > l:
        return s[:l-3] + "..."
    else:
        return s


def msg2dict(msg):
    raw = msg.text
    if not raw:
        raw = ''
    for child in msg:
        raw += child.text
        raw += child.tail
    raw = raw.strip()
    fullpath = None
    path = None
    linenum = None
    text = raw
    r = re.compile('\"(\S+)\" [Ll]ine (\d+): (.+)')
    m = r.match(raw)

    if m is not None:
        fullpath = m.group(1)
        path = os.path.relpath(fullpath)
        linenum = int(m.group(2))
        text = m.group(3)
        for pattern in SKIP_PATHS:
            if glob.fnmatch.fnmatch(path, pattern):
                return None

    num = int(msg.attrib['num'])
    type = msg.attrib['type']

    if num in SEVERE_WARNINGS:
        type = 'severe'

    if num in IGNORE_LIST or not type in USE_TYPES:
        return None

    # 'key' is basically fulltext without the line number
    key = "%s|%s" % (path, text)

    # remember, "dict.get()" defaults to None
    return {'type': type,
            'source': msg.get('file'),
            'num': num,
            'delta': msg.get('delta'),
            'fulltext': raw,
            'text': text,
            'key': key,
            'fullpath': fullpath,
            'path': path,
            'count': 1,
            'linenum': linenum}


def parse(files):
    counts = {'duplicate': 0,
              'error': 0,
              'warning': 0,
              'severe': 0,
              'info': 0}
    the_dict = {}

    for f in files:
        tree = ET.parse(f)
        for msg in tree.iter('msg'):
            m = msg2dict(msg)
            if not m:
                continue
            t = m['type']
            if m['key'] in the_dict:
                counts['duplicate'] += 1
                m['count'] += 1
            the_dict[m['key']] = m
            counts[t] += 1

    return (the_dict.values(), counts)


def parse_diff(before_files, after_files):
    tmpl = {'add': 0,
            'remove': 0,
            'before': 0,
            'after': 0}
    counts = {'duplicate': 0,
              'error': tmpl.copy(),
              'warning': tmpl.copy(),
              'severe': tmpl.copy(),
              'info': tmpl.copy()}

    before_dict = {}
    for before in before_files:
        before_tree = ET.parse(before)
        for msg in before_tree.iter('msg'):
            m = msg2dict(msg)
            if not m:
                continue
            t = m['type']
            if m['key'] in before_dict:
                counts['duplicate'] += 1
                m['count'] += 1
            before_dict[m['key']] = m
            counts[t]['before'] += 1

    add_list = []
    after_dict = {}
    for after in after_files:
        after_tree = ET.parse(after)
        for msg in after_tree.iter('msg'):
            m = msg2dict(msg)
            if not m:
                continue
            t = m['type']
            if m['key'] in after_dict:
                counts['duplicate'] += 1
                m['count'] += 1
            after_dict[m['key']] = m
            if m['key'] in before_dict.keys():
                before_dict.pop(m['key'])
            else:
                add_list.append(m)
                counts[t]['add'] += 1
            counts[t]['after'] += 1

    for m in before_dict.values():
        t = m['type']
        counts[t]['remove'] += 1
    return (add_list, before_dict.values(), counts)


def print_msgs(msgs, difftype=None, full=False, everything=False,
               show_path=False):
    if difftype is 'add':
        lineprefix = colorize("+", 'bggreen')
    elif difftype is 'remove':
        lineprefix = colorize("-", 'bgred')
    else:
        lineprefix = ""

    for m in msgs:
        prefix = m['source'] + ":" + str(m['num']) + ": "
        if show_path and m['path']:
            prefix += m['path'] + ':' + str(m['linenum']) + "\n "
        if everything:
            body = '\n'
            for k, v in m.iteritems():
                body += "\t%s: %s\n" % (k, v)
        elif full:
            body = m['text']
        else:
            body = strlim(m['text'], 77 - len(prefix))
        print(lineprefix +
              colorize(prefix, m['type'], bold=True) +
              colorize(body, m['type']))


def print_by_file(add, remove=None, full=False, everything=False,
                  show_path=False):
    """
    For non-diff output, set 'remove' to None and pass message list as 'add'.
    """
    fdict = {'<unknown>': {'add': [], 'remove': []}}

    for m in add:
        if not m['path']:
            fdict['<unknown>']['add'].append(m)
            continue
        if not m['path'] in fdict:
            fdict[m['path']] = {'add': [], 'remove': []}
        fdict[m['path']]['add'].append(m)

    if remove is not None:
        for m in remove:
            if not m['path']:
                fdict['<unknown>']['add'].append(m)
                continue
            if not m['path'] in fdict:
                fdict[m['path']] = {'add': [], 'remove': []}
            fdict[m['path']]['remove'].append(m)

    printargs = dict(full=full, everything=everything, show_path=show_path)

    for key in sorted(fdict.keys()):
        print(colorize("--- " + key, 'bgwhite'))
        if remove is not None:
            print_msgs(fdict[key]['add'], 'add', **printargs)
            print_msgs(fdict[key]['remove'], 'remove', **printargs)
        else:
            print_msgs(fdict[key]['add'], None, **printargs)


def xmsgs_configure(disable_color, ignore_list, types, skip_paths):
    global DISABLE_COLOR
    global IGNORE_LIST
    global USE_TYPES
    global SKIP_PATHS

    if disable_color:
        DISABLE_COLOR = True
    if ignore_list:
        IGNORE_LIST.extend(ignore_list)
    if types:
        USE_TYPES = types
    if skip_paths:
        SKIP_PATHS = skip_paths


def print_counts(counts, diff=False):
    if diff:
        def helper(name, c, color=None):
            print("%s %s (%s, %s)" % (
                colorize("%020s" % name, color) + ':',
                colorize(str(c['after']), '', bold=True),
                colorize("+" + str(c['add']), 'green', bold=True),
                colorize("-" + str(c['remove']), 'red', bold=True)))
    else:
        def helper(name, c, color=None):
            print("%s %s" % (
                colorize("%020s" % name, color) + ':',
                colorize(str(c), '', bold=True)))

    print(("\n=== Summary " + "=" * 79)[:79])
    if 'error' in USE_TYPES:
        helper('Errors', counts['error'], color='error')
    if 'severe' in USE_TYPES:
        helper('Severe Warnings', counts['severe'], color='severe')
    if 'warning' in USE_TYPES:
        helper('Warnings', counts['warning'], color='warning')
    if 'info' in USE_TYPES:
        helper('Infos', counts['info'], color='info')
