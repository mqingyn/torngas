#!/usr/bin/env python
# -*- coding: utf-8  -*-

__author__ = 'qingyun.meng'

"""
Created by qingyun.meng on 202014/8/28.
Modify by: qingyun.meng
Description: 利用队列来做BufferHandler
"""
import logging, logging.handlers
import Queue


class QueueBufferingHandler(logging.handlers.MemoryHandler):
    def __init__(self, capacity, flushLevel=logging.ERROR, target=None):

        super(QueueBufferingHandler, self).__init__(capacity)
        self.capacity = capacity
        self.buffer = Queue.Queue()
        self.flushLevel = flushLevel
        self.target = target


    def shouldFlush(self, record):

        return (self.buffer.qsize() >= self.capacity) or (record.levelno >= self.flushLevel)


    def emit(self, record):

        self.buffer.put_nowait(record)

        if self.shouldFlush(record):
            self.flush()


    def flush(self):
        if self.target:
            while 1:
                try:
                    size = self.buffer.qsize()
                    if size > 0 and size >= self.capacity:
                        self.target.handle(self.buffer.get_nowait())
                    else:
                        break

                except Queue.Empty, ex:
                    break


