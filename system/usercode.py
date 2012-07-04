import re
import jinja2
import markdown

def parse(text):
  t = jinja2.escape(text.replace("\r\n","<br>"))
  return markdown.markdown(t,output_format="html4")
