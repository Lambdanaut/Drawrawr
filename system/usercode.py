import re
try:
  import markdown
  def parse(text):
    t = text.replace("\r\n","<br>")
    return markdown.markdown(t,output_format="html4")
except:
  def parse(text):
    return text
