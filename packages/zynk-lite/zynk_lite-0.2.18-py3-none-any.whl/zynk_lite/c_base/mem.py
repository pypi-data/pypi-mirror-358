# SPDX-FileCopyrightText: 2025-present Guille <guilleleiratemes@gmail.com>
#
# SPDX-License-Identifier: GPLv3

from . import templates
import inspect

class MemoryManager:
    def emit_nenv(self):
        stack = inspect.stack()
        print("[DEBUG emit_nenv] call stack:")
        for frame in stack[1:4]:
            print(f"  [DEBUG] {frame.function} at {frame.filename}:{frame.lineno}")
        return 'env = cynkEnvCreate(env, CYNK_ENV_CAP, &sysarena);'
    def emit_ret_env(self):
        stack = inspect.stack()
        print("[DEBUG emit_ret_env] call stack:")
        for frame in stack[1:4]:
            print(f"  [DEBUG] {frame.function} at {frame.filename}:{frame.lineno}")
        return 'env = cynkEnvBack(env, &sysarena);'
    def emit_set(self, name, stack):
        stackinfo = inspect.stack()
        print("[DEBUG emit_set] call stack:")
        for frame in stackinfo[1:4]:
            print(f"  [DEBUG] {frame.function} at {frame.filename}:{frame.lineno}")
        return f'zynkTableSet(&sysarena, env, "{name}", {stack.spop()});'
    def emit_new(self, name, stack):
        stackinfo = inspect.stack()
        print("[DEBUG emit_new] call stack:")
        for frame in stackinfo[1:4]:
            print(f"  [DEBUG] {frame.function} at {frame.filename}:{frame.lineno}")
        return f'zynkTableNew(env, "{name}", {stack.spop()}, &sysarena);'
    def emit_get(self, name):
        stackinfo = inspect.stack()
        print("[DEBUG emit_get] call stack:")
        for frame in stackinfo[1:4]:
            print(f"  [DEBUG] {frame.function} at {frame.filename}:{frame.lineno}")
        return f'zynkTableGet(env, "{name}")'
    def emit_pget(self, name, stack):
        stackinfo = inspect.stack()
        print("[DEBUG emit_pget] call stack:")
        for frame in stackinfo[1:4]:
            print(f"  [DEBUG] {frame.function} at {frame.filename}:{frame.lineno}")
        return stack.spush(self.emit_get(name))
