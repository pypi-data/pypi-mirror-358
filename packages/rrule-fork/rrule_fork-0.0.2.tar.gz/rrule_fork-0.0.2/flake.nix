{
  description = "rrule";

  inputs.nixpkgs.url = "github:nixos/nixpkgs";
  inputs.flake-parts.url = "github:hercules-ci/flake-parts";

  outputs = inputs @ { self, nixpkgs, flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      perSystem = { system, pkgs, lib, ... }: {
        packages.default = pkgs.python3.pkgs.buildPythonPackage rec {
          pname = "rrule";
          version = "0.1.0";
          src = lib.cleanSource ./.;
          format = "pyproject";
          cargoDeps = pkgs.rustPlatform.importCargoLock {
            lockFile = ./Cargo.lock;
          };
          nativeBuildInputs = with pkgs.rustPlatform; [
            maturinBuildHook
            cargoSetupHook
            pkgs.python3.pkgs.pythonOutputDistHook
          ];
          buildInputs = lib.optionals pkgs.stdenv.isDarwin [
            pkgs.libiconv
          ];
        };

        devShells.default = pkgs.mkShell {
          nativeBuildInputs = [ pkgs.maturin pkgs.libiconv ];
        };
      };
    };
}
