cd ./GOTCHA//
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=${PYFLOT_ROOTDIR}/external-deps/install/ -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON ../
make install
