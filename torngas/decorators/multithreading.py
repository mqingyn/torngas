#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
multithreading support for tornado
come from whirlwind
"""
from __future__ import with_statement
from tornado.web import *
import threading

from Queue import Queue


def threadedhandler(method):
    @asynchronous
    def wrapper(self, *args, **kwargs):
        self._is_threaded = True
        self._auto_finish = False
        action = ThreadedHandler(method, self, *args, **kwargs)
        ThreadPool.instance().add_task(action.do_work)

    return wrapper


class ThreadedHandler():
    def __init__(self, method, handler, *args, **kwargs):
        self._method = method
        self._handler = handler
        self._args = args
        self._kwargs = kwargs


    def do_work(self):
        try:
            # TODO: handle handlers that return a value.
            # (think tornado considers that a json response)
            self._method(self._handler, *self._args, **self._kwargs)
            if not self._handler._is_torngas_finished:
                self._handler.finish()
        except Exception, e:
            self._handle_request_exception(e)


def threadedfunc(method):
    @asynchronous
    def wrapper(*args, **kwargs):
        action = ThreadedFunction(method, *args, **kwargs)
        ThreadPool.instance().add_task(action.do_work)

    return wrapper


class ThreadedFunction():
    def __init__(self, method, *args, **kwargs):
        self._method = method
        self._args = args
        self._kwargs = kwargs

    def do_work(self):
        try:
            self._method(*self._args, **self._kwargs)
        except Exception, e:
            raise


class ThreadPool():
    """
        Pool of threads consuming tasks from a queue

        Note: I'm not crazy about the fixed threadpool implementation.
        TODO: should have a max_threads argument, then we can build up to that as needed and
        reap unused threads.
        -dustin
    """

    def __init__(self, num_threads=10):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): ThreadPoolWorker(self.tasks)

    """
        Submits a task to the threadpool
        callback will be called once the task completes.
    """

    def add_task(self, func, callback=None):
        """Add a task to the queue"""
        self.tasks.put((func, callback))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()

    """
        Returns the global threadpool.  Use this in almost all cases.
    """
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls):

        if not hasattr(cls, "_instance"):
            with ThreadPool._instance_lock:
                #singleon
                cls._instance = cls()
        return cls._instance


class ThreadPoolWorker(threading.Thread):
    """Thread executing tasks from a given tasks queue"""

    def __init__(self, tasks):
        threading.Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, callback = self.tasks.get()
            try:
                func()
            except Exception, e:
                print e
            if callback:
                callback()
            self.tasks.task_done()