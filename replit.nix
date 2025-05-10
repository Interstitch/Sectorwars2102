{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.venv
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.wheel
    pkgs.python311Packages.fastapi
    pkgs.python311Packages.uvicorn
    pkgs.python311Packages.sqlalchemy
    pkgs.python311Packages.psycopg2
    pkgs.python311Packages.pydantic
    pkgs.nodejs_20
    pkgs.nodePackages.typescript-language-server
    pkgs.yarn
    pkgs.nodePackages.npm
    pkgs.bash
  ];
}