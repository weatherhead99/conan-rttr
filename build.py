#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default

def valid_compiler(build):
    compiler = build.settings["compiler"]
    if compiler == "clang" or compiler == "apple-clang":
        return False

    return True

def valid_runtime(build):
    os = build.settings["os"]
    runtime = build.settings["compiler.runtime"]

    if os == "Windows" and runtime == "MD":
        return False

    return True

if __name__ == "__main__":

    builder = build_template_default.get_builder()

    filter(valid_compiler, builder.items)
    filter(valid_runtime, builder.items)
    
    builder.run()
