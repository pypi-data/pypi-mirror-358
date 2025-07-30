import sys
from textwrap import dedent

__version__ = "1.0.0"


def main():
    if "--version" in sys.argv[1:]:
        print(__version__)
        exit(0)
    elif "--help" in sys.argv[1:]:
        print("pyfrogsay MESSAGE [MESSAGE]")
        exit(0)

    phrase = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Ộp ộp!"
    topbar = "-" * len(phrase)
    bottombar = "-" * len(phrase)
    output = dedent(
        """
  %s
< %s >
  %s
   \\
    @..@
   (----)
  ( >__< )
  ^^    ^^
"""
        % (topbar, phrase, bottombar)
    )
    print(output)


if __name__ == "__main__":
    main()
