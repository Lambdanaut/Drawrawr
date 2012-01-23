import markdown
import re

def parse(text):
  t = text.replace("\r\n","<br>")
  return markdown.markdown(t,output_format="html4")
