# SPDX-FileCopyrightText: 2025-present Guille <guilleleiratemes@gmail.com>
#
# SPDX-License-Identifier: GPLv3

from .. import tokens
from .. import errors
from . import stack
from . import mem
from . import translator
from . import initialize

class FuncMk:
    def __init__(self, evaler):
        self.evaler=evaler
        self.tables=evaler.tables
        self.stack=evaler.stack
    def func_init(self, name):
        print(f"[DEBUG] emit_nenv en func_init para {name}")
        return f"Value {self.evaler.prefix}_{name}(ArenaManager *manager, ZynkEnv *env, ZynkArray *args)" + " {" + f"\n \t {self.tables.emit_nenv()}\n\tValue ret;\n\t"
    def emit_func(self, expr):
        print(f"[DEBUG] emit_func para {expr.name}")
        self.evaler.program_header.add_func(expr.name)
        func_code = self.func_init(expr.name)
        func_code += self.unpack(expr.params)
        print(f"[DEBUG] visit_block en emit_func para {expr.name}")
        self.evaler.visit_block(expr.body, origin=False)
        func_code += self.evaler.pop_ctx()
        func_code += self.end_func()
        return func_code
    def end_func(self):
        print(f"[DEBUG] emit_ret_env en end_func")
        return f"{self.tables.emit_ret_env()}\n" + "return ret;" + "\n}"
    def unpack_first(self):
        print(f"[DEBUG] unpack_first (argumentos)")
        return "for (uint8_t i=0;i<args->len || i<256;i++) {\n\t\t" + self.stack.spush("args->value[i]") + "\n\t}\n\t"
    def unpack_second(self, names):
        print(f"[DEBUG] unpack_second (nombres: {names})")
        ret = ""
        for name in reversed(names):
            ret += self.tables.emit_new(name, self.stack)
            ret += "\n\t"
        return ret
    def unpack(self, names):
        print(f"[DEBUG] unpack (names: {names})")
        return self.unpack_first() + self.unpack_second(names)
