{ pkgs }: {
  deps = [
    pkgs.bash
    pkgs.python3
    pkgs.python310Packages.pip
    pkgs.python310Packages.setuptools
    pkgs.python310Packages.wheel
    pkgs.nodejs-16_x
    pkgs.nodePackages.npm
  ];
}