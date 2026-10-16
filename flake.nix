{
  description = "Development environment personal website";

  inputs = {
    # Pinned to a specific rev instead of tracking nixos-unstable: in October
    # 2026, unstable pairs quarto 1.10.18 with pandoc 3.7.0.2, while quarto
    # 1.10 requires pandoc 3.10.0. The mismatch breaks rendering.
    #
    # This rev (September 2025) ships the consistent pair quarto 1.7.33 + pandoc
    # 3.6. Re-pin to unstable once nixpkgs ships pandoc >= 3.10.
    nixpkgs.url = "github:nixos/nixpkgs/d0fc30899600b9b3466ddb260fd83deb486c32f1";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        system = system;
      };
    in
    {
      formatter.${system} = pkgs.nixfmt-rfc-style;
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          quarto

          # Python with Jupyter, so Quarto can execute code cells in posts.
          (python313.withPackages (ps: [ ps.jupyter ]))

          # Pre-commit hook dependencies
          exiftool
        ];
      };
    };
}
