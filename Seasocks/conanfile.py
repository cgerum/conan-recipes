from conans import CMake, ConanFile, tools
from conans.errors import ConanException, ConanInvalidConfiguration
import os
import re
import shutil
import textwrap


class SeasocksConan(ConanFile):
    name = "Seasocks"
    version = "1.4.4"
    topics = ("seasocks", "embeddable", "webserver", "websockets")
    homepage = "https://github.com/mattgodbolt/seasocks"
    url = "https://github.com/mattgodbolt/seasocks"
    description = "Simple, small, C++ embeddable webserver with WebSockets support"
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_zlib": True,
    }
    no_copy_source = True
    generators = "cmake", "cmake_find_package"

    exports_sources = "src/main/c/*"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def source(self):
        self.run("git clone https://github.com/mattgodbolt/seasocks.git .")
        self.run("git checkout tags/v1.4.4")

    def build(self):
        if self.source_folder == self.build_folder:
            raise ConanException("Cannot build in same folder as sources")
        tools.save(os.path.join(self.build_folder, "CMakeLists.txt"), textwrap.dedent("""\
            cmake_minimum_required(VERSION 3.0)
            project(cmake_wrapper)

            include("{install_folder}/conanbuildinfo.cmake")
            conan_basic_setup(TARGETS)

            add_subdirectory("{source_folder}" seasocks)
        """).format(
            source_folder=self.source_folder.replace("\\", "/"),
            install_folder=self.install_folder.replace("\\", "/")))
        cmake = CMake(self)
        cmake.definitions["DEFLATE_SUPPORT"] = self.options.with_zlib
        cmake.configure(source_folder=self.build_folder)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # Set the name of the generated `FindSeasocks.cmake` and `SeasocksConfig.cmake` cmake scripts
        self.cpp_info.names["cmake_find_package"] = "Seasocks"
        self.cpp_info.names["cmake_find_package_multi"] = "Seasocks"
        self.cpp_info.components["libseasocks"].libs = ["seasocks"]
        # Set the name of the generated seasocks target: `Seasocks::seasocks`
        self.cpp_info.components["libseasocks"].names["cmake_find_package"] = "seasocks"
        self.cpp_info.components["libseasocks"].names["cmake_find_package_multi"] = "seasocks"
        if self.options.with_zlib:
            self.cpp_info.components["libseasocks"].requires = ["zlib::zlib"]
