from conans import ConanFile
import os
from conans.tools import download
from conans.tools import unzip

class LuajitRocksConan(ConanFile):
    name = "luajit-rocks"
    version = "2.0.5"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    url="http://github.com/gsage/conan-luajit-rocks"
    license="https://opensource.org/licenses/mit-license.php"
    exports="FindLuajit.cmake"
    unzipped_name = "luajit-rocks-master"
    zip_name = "%s.zip" % unzipped_name
    description = "Luajit with luarocks"

    def source(self):
        url = "https://github.com/unix4ever/luajit-rocks/archive/master.zip"
        download(url, self.zip_name)
        unzip(self.zip_name)
        os.unlink(self.zip_name)

    def build(self):
        if str(self.settings.os) in ["Macos", "Linux"]:
            make = "make install"
        else:
            make = "nmake install"

        cmd = "cd %s && mkdir -p bin && cd bin && cmake ../ -DCMAKE_INSTALL_PREFIX=../install && %s" % (self.unzipped_name, make)
        self.run(cmd)

    def package(self):
        # Headers
        self.copy(pattern="*.h", dst="include", src="%s/install/include" % self.unzipped_name, keep_path=False)
        self.copy(pattern="*.hpp", dst="include", src="%s/install/include" % self.unzipped_name, keep_path=False)

        # libs
        self.copy(pattern="*.a", dst="lib", src="%s/install/lib" % self.unzipped_name, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="%s/install/lib" % self.unzipped_name, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="%s/install/lib" % self.unzipped_name, keep_path=False)
        self.copy(pattern="*.so", dst="lib", src="%s/install/lib" % self.unzipped_name, keep_path=False)

        # share
        self.copy(pattern="lua*", dst="share", src="%s/install/share" % self.unzipped_name, keep_path=True)

        # etc
        self.copy(pattern="lua*", dst="etc", src="%s/install/etc" % self.unzipped_name, keep_path=False)

        # binaries
        self.copy(pattern="lua*", dst="bin", src="%s/install/bin" % self.unzipped_name, keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.resdirs = ["etc", "share"]
        self.cpp_info.libs = ["luajit-static"]

        if self.settings.os == 'Macos' and self.settings.arch == 'x86_64':
            self.cpp_info.exelinkflags.append("-pagezero_size 10000")
            self.cpp_info.exelinkflags.append("-image_base 100000000")
            self.cpp_info.exelinkflags.append("-image_base 7fff04c4a000")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
