#!/usr/bin/env python
# -*- coding: utf-8  -*-
# Created by mqingyn on 2015/1/16.
from dispatch import Signal

call_started = Signal(providing_args=["request"])
handler_started = Signal(providing_args=["handler"])
handler_response = Signal(providing_args=["handler", "chunk"])
call_finished = Signal(providing_args=["handler"])
handler_render = Signal(providing_args=["handler", "template_name", "kwargs"])