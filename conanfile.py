import os

from conans import ConanFile
from conans.tools import download
from conans.tools import unzip
from conans.tools import replace_in_file
from conans import CMake

class LuajitRocksConan(ConanFile):
    name = "luajit-rocks"
    version = "2.0.5"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    url = "http://github.com/gsage/conan-luajit-rocks"
    license = "https://opensource.org/licenses/mit-license.php"
    unzipped_name = "luajit-rocks-master"
    zip_name = "%s.zip" % unzipped_name
    description = "Luajit with luarocks"
    options = {
        "shared": [True, False]
    }

    default_options = (
        "shared=True"
    )

    def source(self):
        url = "https://github.com/unix4ever/luajit-rocks/archive/master.zip"
        download(url, self.zip_name)
        unzip(self.zip_name)
        os.unlink(self.zip_name)
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        replace_in_file("{}/CMakeLists.txt".format(self.unzipped_name), "PROJECT(luajit-rocks)", '''PROJECT(luajit-rocks)
include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        options = {
            'CMAKE_INSTALL_PREFIX': '../install'
        }
        if self.settings.os != "Windows":
            options['CMAKE_CXX_FLAGS'] = '-fPIC -O0 ${CMAKE_CXX_FLAGS}'
            options['CMAKE_C_FLAGS'] = '-fPIC ${CMAKE_C_FLAGS}'

        cmake.configure(defs=options, build_dir='_build', source_dir="../{}".format(self.unzipped_name))
        cmake.build(target='install')

    def package(self):
        bin_folder = "bin"
        lib_folder = "lib"
        share_folder = "share"
        etc_folder = "etc"

        if self.settings.os == "Windows":
            bin_folder = lib_folder = share_folder = etc_folder = ""
            self.copy(pattern="*.*", dst="tools", src="install/tools", keep_path=True)

        # Headers
        self.copy(pattern="*.h", dst="include", src="install/include", keep_path=False)
        self.copy(pattern="*.hpp", dst="include", src="install/include", keep_path=False)

        lib_folder = os.path.join("install", lib_folder)
        # libs
        self.copy(pattern="*.a", dst="lib", src=lib_folder, keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=lib_folder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=lib_folder, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=lib_folder, keep_path=False)
        self.copy(pattern="*.so", dst="lib", src=lib_folder, keep_path=False)

        share_folder = os.path.join("install", share_folder)
        # share
        self.copy(pattern="*.lua", dst="share", src=share_folder, keep_path=True)

        etc_folder = os.path.join("install", etc_folder)
        # etc
        self.copy(pattern="*.lua", dst="etc", src=etc_folder, keep_path=True)

        bin_folder = os.path.join("install", bin_folder)
        # binaries
        self.copy(pattern="lua*", dst="bin", src=bin_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.resdirs = ["etc", "share"]

        if self.options.shared:
            self.cpp_info.libs = ["libluajit"] if self.settings.os == "Windows" else ["luajit"]
        else:
            self.cpp_info.libs = ["luajit-static"]

        if self.settings.os == 'Macos' and self.settings.arch == 'x86_64':
            self.cpp_info.exelinkflags.append("-pagezero_size 10000")
            self.cpp_info.exelinkflags.append("-image_base 100000000")
            self.cpp_info.exelinkflags.append("-image_base 7fff04c4a000")
