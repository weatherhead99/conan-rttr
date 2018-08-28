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
    exports = "conan_cmake_integration.patch"
    exports_sources = "conan_cmake_integration.patch"
    sha256 = "f62caee43016489320f8a69145c9208cddd72e451ea95618bc26a49a4cd6c990"

    def source(self):
        tools.get("http://www.rttr.org/releases/rttr-%s-src.tar.gz"
                  % self.version, sha256=self.sha256)

        tools.patch(patch_file="conan_cmake_integration.patch")
        

    def patch_cmake_config_windows(self, cmake, file_to_patch):
        prefix = cmake.definitions.get("CMAKE_INSTALL_PREFIX")
        pdrive, ppath = os.path.splitdrive(prefix)
        cmakefilepath = pdrive.upper() + ppath.replace(os.path.sep,"/")
        self.output.info("replace string: %s" % cmakefilepath)
        replstr = "${CONAN_%s_ROOT}" % self.name.upper()
        tools.replace_in_file(file_to_patch, cmakefilepath, replstr, strict=True)

    def get_patched_libpath(self, build_folder):
        libfolder = os.path.join(build_folder, "lib")
        if self.settings.os == "Windows":
            varname = "PATH"
            curval = os.environ[varname]
            newval = "%s;%s" % (curval, libfolder)
        elif self.settings.os == "Macos":
            varname = "DYLD_LIBRARY_PATH"
            newval = libfolder
        else:
            varname = "LD_LIBRARY_PATH"
            newval = libfolder

        return varname, newval

    def compiler_version_major(self):
        return int(str(self.settings.compiler.version).split(".")[0])
    
    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_BENCHMARKS"] = "OFF"
        cmake.definitions["BUILD_DOCUMENTATION"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_WITH_RTTI"] = "ON" if self.options.rtti else "OFF"

        if self.settings.os == "Linux" and self.settings.compiler == "gcc" \
           and self.compiler_version_major() < 5 :
            self.output.info("gcc < 5, setting cxx11 standard")
            cmake.definitions["CMAKE_CXX_STANDARD"] = "11"

        if self.settings.os == "Macos" \
           and self.compiler_version_major() < 9 :
            self.output.info("appleclang <9, setting cxx11 standard")
            cmake.definitions["CMAKE_CXX_STANDARD"] = "11"
        
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
            if self.settings.os == "Windows":
                self.output.info("patching absolute paths out of cmake config files...")
                cmake_dir = os.path.join(self.package_folder,"cmake")
                config_file = os.path.join(cmake_dir,"rttr-config.cmake")
                if not os.path.exists(config_file):
                    self.output.error("can't find cmake file!")
                self.patch_cmake_config_windows(cmake,config_file)

    def package(self):
        pass

    def package_info(self):
        suffix = "_d" if self.settings.build_type == "Debug" else ""
        prefix = "lib" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = ["%srttr_core%s" % (prefix, suffix)]

        #add lib64 folder, for 64 bit platforms GNUInstalldirs will put libraries here
        self.cpp_info.libdirs.append("lib64")

        #fix missing -ldl needed on old ABI gcc-7
        if self.settings.os == "Linux" \
           and self.settings.compiler == "gcc" \
           and not self.options.shared \
           and self.settings.compiler.libcxx == "libstdc++":
            self.output.info("adding -ldl linkage")
            self.cpp_info.libs.append("-ldl")
