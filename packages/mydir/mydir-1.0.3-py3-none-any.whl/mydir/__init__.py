"""mydir – directory tree visualiser & code bundler."""
from ._core import mydir          # re‑export
__all__ = ["DirTree"]
def main():  # console entry‑point
    from ._core import build_cli
    build_cli()

