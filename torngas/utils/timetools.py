#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re, sys, time, threading, itertools, traceback, os
try:
    import datetime
except ImportError:
    pass


class TimeoutError(Exception): pass


def timelimit(timeout):
    """
    A decorator to limit a function to `timeout` seconds, raising `TimeoutError`
    if it takes longer.
    
        >>> import time
        >>> def meaningoflife():
        ...     time.sleep(.2)
        ...     return 42
        >>> 
        >>> timelimit(.1)(meaningoflife)()
        Traceback (most recent call last):
            ...
        TimeoutError: took too long
        >>> timelimit(1)(meaningoflife)()
        42

    _Caveat:_ The function isn't stopped after `timeout` seconds but continues 
    executing in a separate thread. (There seems to be no way to kill a thread.)

    inspired by <http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/473878>
    """

    def _1(function):
        def _2(*args, **kw):
            class Dispatch(threading.Thread):
                def __init__(self):
                    threading.Thread.__init__(self)
                    self.result = None
                    self.error = None

                    self.setDaemon(True)
                    self.start()

                def run(self):
                    try:
                        self.result = function(*args, **kw)
                    except:
                        self.error = sys.exc_info()

            c = Dispatch()
            c.join(timeout)
            if c.isAlive():
                raise TimeoutError, 'took too long'
            if c.error:
                raise c.error[0], c.error[1]
            return c.result

        return _2

    return _1


def datestr(then, now=None):
    """
    Converts a (UTC) datetime object to a nice string representation.

        >>> from datetime import datetime, timedelta
        >>> d = datetime(1970, 5, 1)
        >>> datestr(d, now=d)
        '0 microseconds ago'
        >>> for t, v in {
        ...   timedelta(microseconds=1): '1 microsecond ago',
        ...   timedelta(microseconds=2): '2 microseconds ago',
        ...   -timedelta(microseconds=1): '1 microsecond from now',
        ...   -timedelta(microseconds=2): '2 microseconds from now',
        ...   timedelta(microseconds=2000): '2 milliseconds ago',
        ...   timedelta(seconds=2): '2 seconds ago',
        ...   timedelta(seconds=2*60): '2 minutes ago',
        ...   timedelta(seconds=2*60*60): '2 hours ago',
        ...   timedelta(days=2): '2 days ago',
        ... }.iteritems():
        ...     assert datestr(d, now=d+t) == v
        >>> datestr(datetime(1970, 1, 1), now=d)
        'January  1'
        >>> datestr(datetime(1969, 1, 1), now=d)
        'January  1, 1969'
        >>> datestr(datetime(1970, 6, 1), now=d)
        'June  1, 1970'
        >>> datestr(None)
        ''
    """

    def agohence(n, what, divisor=None):
        if divisor: n = n // divisor

        out = str(abs(n)) + ' ' + what       # '2 day'
        if abs(n) != 1: out += 's'           # '2 days'
        out += ' '                           # '2 days '
        if n < 0:
            out += 'from now'
        else:
            out += 'ago'
        return out                           # '2 days ago'

    oneday = 24 * 60 * 60

    if not then: return ""
    if not now: now = datetime.datetime.utcnow()
    if type(now).__name__ == "DateTime":
        now = datetime.datetime.fromtimestamp(now)
    if type(then).__name__ == "DateTime":
        then = datetime.datetime.fromtimestamp(then)
    elif type(then).__name__ == "date":
        then = datetime.datetime(then.year, then.month, then.day)

    delta = now - then
    deltaseconds = int(delta.days * oneday + delta.seconds + delta.microseconds * 1e-06)
    deltadays = abs(deltaseconds) // oneday
    if deltaseconds < 0: deltadays *= -1 # fix for oddity of floor

    if deltadays:
        if abs(deltadays) < 4:
            return agohence(deltadays, 'day')

        try:
            out = then.strftime('%B %e') # e.g. 'June  3'
        except ValueError:
            # %e doesn't work on Windows.
            out = then.strftime('%B %d') # e.g. 'June 03'

        if then.year != now.year or deltadays < 0:
            out += ', %s' % then.year
        return out

    if int(deltaseconds):
        if abs(deltaseconds) > (60 * 60):
            return agohence(deltaseconds, 'hour', 60 * 60)
        elif abs(deltaseconds) > 60:
            return agohence(deltaseconds, 'minute', 60)
        else:
            return agohence(deltaseconds, 'second')

    deltamicroseconds = delta.microseconds
    if delta.days: deltamicroseconds = int(delta.microseconds - 1e6) # datetime oddity
    if abs(deltamicroseconds) > 1000:
        return agohence(deltamicroseconds, 'millisecond', 1000)

    return agohence(deltamicroseconds, 'microsecond')

from numtools import denumify
def dateify(datestring):
    """
    Formats a numified `datestring` properly.
    """
    return denumify(datestring, "XXXX-XX-XX XX:XX:XX")

