cd ./GOTCHA//
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=/global/cscratch1/sd/hbrunie/tools/precisiontuning/external-deps/install/ -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON ../
make install
