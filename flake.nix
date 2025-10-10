{
  description = "Django development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python313
            redis

            python313Packages.redis
            python313Packages.django
            python313Packages.djangorestframework
            python313Packages.djangorestframework-simplejwt
            python313Packages.django-filter
            python313Packages.celery
            python313Packages.pillow
            python313Packages.requests
            python313Packages.python-dotenv

            # Development tools
            python313Packages.pip
            python313Packages.virtualenv

            git
          ];

          shellHook = ''
            echo "Django development environment loaded"
            echo "Python version: $(python --version)"
            echo "Django version: $(python -c 'import django; print(django.get_version())')"

            # Python environment
            export PYTHONPATH="$PWD:$PYTHONPATH"

            # Create virtualenv for pip packages not in Nix
            if [ ! -d .venv ]; then
              python -m venv .venv
            fi
            source .venv/bin/activate

            echo ""
            echo "To run Django: python manage.py runserver"
          '';
        };
      }
    );
}
