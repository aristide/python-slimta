# Copyright (c) 2012 Ian C. Good
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""Utilities to make logging consistent and easy in :mod:`slimta` packages."""

import threading
threading._DummyThread._Thread__stop = lambda x: 42

import re
import repr
import logging
from ast import literal_eval

from slimta.logging.socket import SocketLogger
from slimta.logging.subprocess import SubprocessLogger
from slimta.logging.queuestorage import QueueStorageLogger

__all__ = ['getSocketLogger', 'getSubprocessLogger', 'getQueueStorageLogger']


def getSocketLogger(name):
    """Wraps the result of :func:python:`logging.getLogger()` in a
    :class:`SocketLogger` object to provide limited and consistent logging
    output for socket operations.

    :param name: ``name`` as passed in to :func:python:`logging.getLogger()`.
    :rtype: :class:`SocketLogger`

    """
    logger = logging.getLogger(name)
    return SocketLogger(logger)


def getSubprocessLogger(name):
    """Wraps the result of :func:python:`logging.getLogger()` in a
    :class:`SubprocessLogger` object to provide limited and consistent
    logging output for subprocess operations.

    :param name: ``name`` as passed in to :func:python:`logging.getLogger()`.
    :rtype: :class:`SubprocessLogger`

    """
    logger = logging.getLogger(name)
    return SubprocessLogger(logger)


def getQueueStorageLogger(name):
    """Wraps the result of :func:python:`logging.getLogger()` in a
    :class:`QueueStorageLogger` object to provide limited and consistent logging
    output for |QueueStorage| operations.

    :param name: ``name`` as passed in to :func:python:`logging.getLogger()`.
    :rtype: :class:`QueueStorageLogger`

    """
    logger = logging.getLogger(name)
    return QueueStorageLogger(logger)


log_repr = repr.Repr()
log_repr.maxstring = 100


def logline(log, type, typeid, operation, **data):
    if not data:
        log('{0}:{1}:{2}'.format(type, typeid, operation))
    else:
        data_str = ' '.join(['='.join((key, log_repr.repr(val)))
                             for key, val in sorted(data.iteritems())])
        log('{0}:{1}:{2} {3}'.format(type, typeid, operation, data_str))


parseline_pattern = re.compile(r'^([^:]+):([^:]+):(\S+) ?(.*)$')
data_item_pattern = re.compile('^([^=]+)=')

def _parseline_data(remaining, data):
    match = data_item_pattern.match(remaining)
    if not match:
        return data
    key = match.group(1)
    end_i = space_i = match.end(0)
    while True:
        space_i = remaining.find(' ', space_i+1)
        if space_i == -1:
            try:
                data[key] = literal_eval(remaining[end_i:])
            except Exception:
                pass
            return data
        else:
            try:
                data[key] = literal_eval(remaining[end_i:space_i])
            except Exception:
                pass
            else:
                return _parseline_data(remaining[space_i+1:], data)

def parseline(line):
    match = parseline_pattern.match(line)
    if not match:
        raise ValueError(line)
    type, id, op, data_str = match.groups()
    return type, id, op, _parseline_data(data_str, {})


# vim:et:fdm=marker:sts=4:sw=4:ts=4
