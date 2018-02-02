from conans import ConanFile, CMake, tools
import os

class RttrConan(ConanFile):
    name = "rttr"
    version = "0.9.5"
    license = "MIT"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Rttr here>"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "rtti" : [True, False]}
    default_options = "shared=False", "rtti=True"
    generators = "cmake"
    requires = "boost_chrono/1.66.0@bincrafters/testing","boost_system/1.66.0@bincrafters/testing"
    exports_sources = "CMakeLists.txt"
    exports = ["README.md"]
    
    sha256 = "caa8d404840b0e156f869a947e475b09f7b602ab53c290271f40ce028c8d7d91"


    
    def source(self):
        tools.get("http://www.rttr.org/releases/rttr-%s-src.tar.gz"
                  % self.version, sha256=self.sha256)
        
    def build(self):
        cmake = CMake(self)
        sf = os.path.join(self.source_folder,"rttr-%s-src" % self.version)

        cmake.definitions["BUILD_BENCHMARKS"] = "OFF"
        cmake.definitions["BUILD_WITH_RTTI"] = "ON" if self.options.rtti else "OFF"

        cmake.configure(source_folder=sf)
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include", src="hello")
        self.copy("*hello.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["hello"]
