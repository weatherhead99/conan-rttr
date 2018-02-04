from conans import ConanFile, CMake, tools
import os
import shutil

class RttrConan(ConanFile):
    name = "rttr"
    version = "0.9.5"
    license = "MIT"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Rttr here>"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "rtti": [True, False]}
    default_options = "shared=False", "rtti=True"
    generators = "cmake"
    exports = "README.md"
    exports_sources = "LICENSE.txt", "conan_build.patch"
    sha256 = "caa8d404840b0e156f869a947e475b09f7b602ab53c290271f40ce028c8d7d91"

    def config_options(self):
        comp = self.settings.compiler
        if comp == "clang" or comp == "apple-clang":
            self.output.error("clang not supported for this version")

    def source(self):
        tools.get("http://www.rttr.org/releases/rttr-%s-src.tar.gz"
                  % self.version, sha256=self.sha256)
        tools.patch(patch_file="conan_build.patch")
        
    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_BENCHMARKS"] = "OFF"
        cmake.definitions["BUILD_WITH_RTTI"] = "ON" if self.options.rtti else "OFF"
        cmake.definitions["BUILD_STATIC"] = "ON" if not self.options.shared else "OFF"
        sf = os.path.join(self.source_folder,"rttr-%s-src" % self.version)
        cmake.configure(source_folder=sf)
        cmake.build()
        #need to do install here, otherwise cmake config files don't get
        #generated properly
        cmake.install()

    def package(self):
        pass

    def package_info(self):
        suffix = "_d" if self.settings.build_type == "Debug" else ""
        prefix = "lib" if self.settings.os == "Windows" else ""

        self.cpp_info.libs = ["%srttr_core%s" % (prefix, suffix)]


