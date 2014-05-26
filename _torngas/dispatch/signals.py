#!/usr/bin/env python
# -*- coding: utf-8 -*-
from torngas.dispatch import Signal

call_started = Signal()
handler_started = Signal()
handler_finished = Signal()
call_finished = Signal()
# got_request_exception = Signal(providing_args=["request"])