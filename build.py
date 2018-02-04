#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default

def valid_compiler(build):
    compiler = build.settings["compiler"]
    if compiler == "clang" or compiler == "apple-clang":
        return False

    return True


if __name__ == "__main__":

    builder = build_template_default.get_builder()

    filter(valid_compiler, builder.items)

    builder.run()
