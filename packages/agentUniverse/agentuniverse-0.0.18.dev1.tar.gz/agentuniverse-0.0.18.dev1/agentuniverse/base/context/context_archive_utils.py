# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/17 11:00
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: context_archive_utils.py
import re
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


def get_current_context_archive():
    context_archive = FrameworkContextManager().get_context(
        'context_archive', None)
    if not context_archive:
        context_archive = {}
        FrameworkContextManager().set_context('context_archive', {})

    return context_archive


def update_context_archive(name, data, description):
    react_memory = get_current_context_archive()
    react_memory[name] = {
        'data': data,
        'description': description
    }