{
  description = "Development environment personal website";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        system = system;
        config = {
          allowUnfree = true;
        };
      };
    in
    {
      formatter.${system} = pkgs.nixfmt-rfc-style;
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          # Python version to use.
          python312

          # Python package and project manager
          uv

          # Pandoc
          pandoc
        ];
        shellHook = ''
          uv venv
          uv pip sync requirements.txt
          source .venv/bin/activate
        '';
      };
    };
}
