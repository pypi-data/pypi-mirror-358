#!/usr/bin/env python
from . import unlock
import argparse

def main():
  example_text = (
    'examples:\n\n'
    '%(prog)s input.pdf -o output.pdf\n'
    '%(prog)s input.pdf -o output.pdf --password 1234\n'
    '%(prog)s input.pdf -o output.pdf --stdin-password\n'
    'echo 1234 | %(prog)s input.pdf -o output.pdf --stdin-password\n'
    '%(prog)s input.pdf -b\n'
  )
  parser = argparse.ArgumentParser(
    description="A simple script that converts PDFs to versions without permission restrictions",
    epilog=example_text,
    formatter_class=argparse.RawDescriptionHelpFormatter
  )
  parser.add_argument("input", help="input PDF file")
  parser.add_argument("-p", "--password", help="password for the input PDF file", default="")
  parser.add_argument("--stdin-password", help="read password from stdin (this will override the --password or -p argument)", action="store_true")
  parser.add_argument("-o", "--output", help="output PDF file, default: output.pdf", default=None)
  parser.add_argument("-b", "--backup", help="the original file will be saved with the extension .bak, and the default output will be the original one", action="store_true")
  args = parser.parse_args()
  unlock(args.input, args.output, args.stdin_password, args.backup, args.password)

if __name__ == "__main__":
  main()
