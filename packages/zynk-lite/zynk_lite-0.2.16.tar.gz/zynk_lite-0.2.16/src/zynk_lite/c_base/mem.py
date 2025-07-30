# SPDX-FileCopyrightText: 2025-present Guille <guilleleiratemes@gmail.com>
#
# SPDX-License-Identifier: GPLv3

from . import templates
import inspect

class MemoryManager:
    def emit_nenv(self):
        print(f"[DEBUG] {inspect.stack()}")
        return 'env = cynkEnvCreate(env, CYNK_ENV_CAP, &sysarena);'
    def emit_ret_env(self):
        print(f"[DEBUG] {inspect.stack()}")
        return 'env = cynkEnvBack(env, &sysarena);'
    def emit_set(self, name, stack):
        print(f"[DEBUG] {inspect.stack()}")
        return f'zynkTableSet(&sysarena, env, "{name}", {stack.spop()});'
    def emit_new(self, name, stack):
        print(f"[DEBUG] {inspect.stack()}")
        return f'zynkTableNew(env, "{name}", {stack.spop()}, &sysarena);'
    def emit_get(self, name):
        print(f"[DEBUG] {inspect.stack()}")
        return f'zynkTableGet(env, "{name}")'
    def emit_pget(self, name, stack):
        print(f"[DEBUG] {inspect.stack()}")
        return stack.spush(self.emit_get(name))
