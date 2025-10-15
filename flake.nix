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
            docker
            docker-compose
            postgresql

            python313Packages.django
            python313Packages.django-filter
            python313Packages.django-stubs
            python313Packages.django-stubs-ext
            python313Packages.djangorestframework
            python313Packages.djangorestframework-simplejwt
            python313Packages.djangorestframework-stubs
            python313Packages.drf-spectacular
            python313Packages.drf-spectacular-sidecar
            python313Packages.pillow
            python313Packages.psycopg2-binary
            python313Packages.python-dotenv
            python313Packages.requests

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

            # PostgreSQL environment variables with defaults
            export POSTGRES_DB=''${POSTGRES_DB:-marketplace}
            export POSTGRES_USER=''${POSTGRES_USER:-postgres}
            export POSTGRES_PASSWORD=''${POSTGRES_PASSWORD:-postgres}

            export PGDATA=$PWD/pgdata
            export PGHOST=localhost
            export PGPORT=5432

            echo ""
            echo "To run Django: python manage.py runserver"
          '';
        };
      }
    );
}
