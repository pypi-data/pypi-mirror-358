# PDF Unlocker
This is a simple Python script that converts PDF files into versions without any permission restrictions

This script utilizes [pikepdf](https://pikepdf.readthedocs.io/en/latest/) to make a clean copy of each page

# Usage

## Install the Requirements

To install the necessary requirements, run the following command:

```sh
pip install pdf-unlocker
```

## Typical Usage

```sh
pdf-unlocker input.pdf -o output.pdf
pdf-unlocker input.pdf -o output.pdf --password 1234
pdf-unlocker input.pdf -o output.pdf --stdin-password
echo 1234 | pdf-unlocker input.pdf -o output.pdf --stdin-password
pdf-unlocker input.pdf -b
```

The resulting PDF file should not have any permission restrictions, nor should it require a password for usage (the password is required only to read the source PDF)

## Arguments

| Argument || Description |
|-|-|-|
| (Required) | | input PDF file |
| -p PASSWORD | --password PASSWORD | password for the input PDF file |
| | --stdin-password | read password from stdin (this will override the --password or -p argument) |
| -o OUTPUT | --output OUTPUT | output PDF file <br> _default: output.pdf_ |
| -b | --backup | the original file will be saved with the extension .bak, and the default output will be the original one |