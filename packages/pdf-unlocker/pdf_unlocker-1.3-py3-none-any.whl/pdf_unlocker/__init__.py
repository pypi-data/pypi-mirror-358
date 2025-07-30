#!/usr/bin/env python
from pikepdf import Pdf
import shutil

def unlock(pdf_input, pdf_output = None, stdin_password = None, backup = None, pdf_password=""):
  dst = Pdf.new()
  password = pdf_password
  output = "output.pdf"
  if backup:
    output = pdf_input
    new_input = f"{pdf_input}.bak"
    shutil.move(pdf_input, new_input)
    pdf_input = new_input
  if pdf_output:
    output = pdf_output
  if stdin_password:
    password = input("Warning, the password is visible if it is typed\nPassword: ")
  with Pdf.open(pdf_input, password=password) as pdf:
    for page in pdf.pages:
      dst.pages.append(page)
    dst.save(output)

