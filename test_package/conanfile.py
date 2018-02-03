#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, RunEnvironment
from conans.errors import ConanException
import os
from io import StringIO

def run_test(conanfile,bin_path, args, output=None):
    if conanfile.settings.os == "Windows":
        conanfile.run("%s %s" % bin_path, args,output=output)
    elif conanfile.settings.os == "Macos":
        conanfile.run("DYLD_LIBRARY_PATH=%s %s %s" % (os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path, args),output=output)
    else:
        conanfile.run("LD_LIBRARY_PATH=%s %s %s" % (os.environ.get('LD_LIBRARY_PATH', ''), bin_path, args),output=output)
    

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        with tools.environment_append(RunEnvironment(self).vars):
            self.output.info("testing that rttr used via find_package works...")
            bin_path = os.path.join("bin", "test_package")
            run_test(self, bin_path, "")

            self.output.info("testing that rttr used via conan mechanism works...")
            bin_path = os.path.join("bin", "test_package_2")
            run_test(self, bin_path, "")
