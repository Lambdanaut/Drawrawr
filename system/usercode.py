import re
from xssclean import XssClean

try:
  import markdown
  def __parse(text):
    t = text.replace("\r\n","<br>")
    return markdown.markdown(t,output_format="html4")
except:
  def __parse(text):
    return text

def parse(text):
  ## Clean out possibilities for javascript: links, unauthorized styling,
  ## inline Javascript, and inline malicious HTML.
  
  return XssClean().strip(__parse(text))