import os
from conans import ConanFile, CMake, tools


class RttrConan(ConanFile):
    name = "rttr"
    version = "0.9.6"
    license = "MIT"
    url = "https://github.com/weatherhead99/conan-rttr"
    description = "An open source library, which adds (dynamic) reflection to C++"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "rtti": [True, False]}
    default_options = "shared=False", "rtti=True"
    generators = "cmake"
    exports = "rttr_use_cxx11.patch"
    exports_sources = "rttr_use_cxx11.patch"
    sha256 = "f62caee43016489320f8a69145c9208cddd72e451ea95618bc26a49a4cd6c990"

    def config_options(self):
        runos = self.settings.os
        if runos == "Windows" and self.settings.compiler.runtime == "MD":
            self.output.error("MD runtime not supported for this version")
            del self.settings.compiler.runtime

    def source(self):
        tools.get("http://www.rttr.org/releases/rttr-%s-src.tar.gz"
                  % self.version, sha256=self.sha256)
        tools.patch(patch_file="rttr_use_cxx11.patch")

    def get_patched_libpath(self, build_folder):
        libfolder = os.path.join(build_folder, "lib")
        if self.settings.os == "Windows":
            varname = "PATH"
            curval = os.environ[varname]
            newval = "%s;%s" % (curval, libfolder)
        else:
            varname = "LD_LIBRARY_PATH"
            newval = libfolder

        return varname, newval

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_BENCHMARKS"] = "OFF"
        cmake.definitions["BUILD_DOCUMENTATION"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_WITH_RTTI"] = "ON" if self.options.rtti else "OFF"

        if self.options.shared:
            cmake.definitions["BUILD_RTTR_DYNAMIC"] = "ON"
            cmake.definitions["BUILD_UNIT_TESTS"] = "ON"
            cmake.definitions["BUILD_STATIC"] = "OFF"
        else:
            cmake.definitions["BUILD_STATIC"] = "ON"
            #note unit tests cannot be run against static build
            cmake.definitions["BUILD_UNIT_TESTS"] = "OFF"
            cmake.definitions["BUILD_RTTR_DYNAMIC"] = "OFF"

        sf = os.path.join(self.source_folder,"rttr-%s" % self.version)
        cmake.configure(source_folder=sf)

        #need to add lib dir to environment to make unit tests pass
        #otherwise, it can't find the shared lib to load in the tests
        varname, varvalue = self.get_patched_libpath(self.build_folder)

        with tools.environment_append({varname : varvalue}):
            cmake.build()
            cmake.install()

    def package(self):
        pass

    def package_info(self):
        suffix = "_d" if self.settings.build_type == "Debug" else ""
        prefix = "lib" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = ["%srttr_core%s" % (prefix, suffix)]

        #add lib64 folder, for 64 bit platforms GNUInstalldirs will put libraries here
        self.cpp_info.libdirs.append("lib64")
