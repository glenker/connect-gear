with import <nixpkgs> { lib, buildPythonPackage, fetchPypi , fetchFromGitHub , pytools , pytest , cudatoolkit , python , mkDerivation};
#{ lib , buildPythonPackage , fetchPypi , fetchFromGitHub , pytools , pytest , cudatoolkit , python , mkDerivation }:
let
  compyte = import ./compyte.nix {
    inherit mkDerivation fetchFromGitHub;
  };
in
buildPythonPackage rec {
  pname = "pycuda";
  version = "2020.1";

  # src = fetchPypi {
  #   inherit pname version;
  #   sha256 = "effa3b99b55af67f3afba9b0d1b64b4a0add4dd6a33bdd6786df1aa4cc8761a5";
  # };

  preConfigure = with lib.versions; ''
    ${python.interpreter} configure.py --boost-inc-dir=${boost.dev}/include \
                          --boost-lib-dir=${boost.dev}/lib \
                          --no-use-shipped-boost \
                          --boost-python-libname=boost_python${major python.version}${minor python.version} \
                          --cuda-root=${cudatoolkit}
  # '';

  postInstall = ''
    ln -s ${compyte} $out/${python.sitePackages}/pycuda/compyte
  '';

  Requires access to libcuda.so.1 which is provided by the driver
  doCheck = false;

  checkPhase = ''
    py.test
  '';
  
  propagatedBuildInputs = [
    pytools
    pytest
    cudatoolkit
    compyte
    python
  ];

  meta = with lib; {
    homepage = "https://github.com/inducer/pycuda/";
    description = "CUDA integration for Python.";
    license = licenses.mit;
    maintainers = with maintainers; [ satoshinakamoto ];
  };

}
