## Originally from http://code.activestate.com/recipes/496942/

## Updated to fit DrawRawr's Python 3 profile & 
## made various language enhancements - Promiskuous 6/23

from html import parser, entities
from cgi import escape
from urllib import parse
from formatter import AbstractFormatter
from xml.sax.saxutils import quoteattr

def xssescape(text):
    """Gets rid of < and > and & and, for good measure, :"""
    return escape(text, quote=True).replace(':','&#58;')

class XssClean(parser.HTMLParser):
  
  result = ""
  open_tags = []
  permitted_tags = ['a', 'b', 'blockquote', 'br', 'i',
                    'li', 'ol', 'ul', 'p', 'cite']
  
  requires_no_close = ['img', 'br']
  
  allowed_attributes = {
                        'a': ['href', 'title'],
                        'img': ['src', 'alt'],
                        'blockquote': ['type']  
                       }
  
  allowed_schemes = ['http', 'https', 'ftp']
  
  
  def __init__(self, fmt=AbstractFormatter):
    super(XssClean, self).__init__(fmt)
    
  def handle_data(self, data):
    if data: self.result += xssescape(data)
    
  def handle_charref(self, ref):
    if len(ref) < 7 and ref.isdigit():
      self.result += '&#{0};'.format(ref)  
    else:
      self.result += xssescape('&#{0}'.format(ref))
      
  def handle_entityref(self, ref):
    if ref in entities.entitydefs:
      self.result += '&{0};'.format(ref)
    else:
      self.result += xssescape('&{0}'.format(ref))
      
  def handle_comment(self, comment):
    if comment: self.result += xssescape("<!--{0}-->".format(comment))
      
  def handle_starttag(self, tag, attrs):
    if tag not in self.permitted_tags:
      self.result += xssescape("<{0}>".format(tag))
      
    else:
      bt = "<" + tag
      
      if tag in self.allowed_attributes:
        attrs = dict(attrs)
        self.allowed_attributes_here = \
          [x for x in self.allowed_attributes[tag] if x in attrs and len(attrs[x]) > 0]
          
        for attribute in self.allowed_attributes_here:
          if attribute in ['href', 'src', 'background']:
            
            if self.url_is_acceptable(attrs[attribute]):
              bt += ' {attr}="{val}"'.format(attr=attribute, val=attrs[attribute])
            else:
              bt += ' {attr}={val}'.format(attr=xssescape(attribute), val=quoteattr(attrs[attribute]))
              
          if bt == "<a" or bt == "<img": return
          
          if tag in self.requires_no_close:
            bt += "/"
            
          bt += ">"
          self.result += bt
          self.open_tags.insert(0, tag)
          
  def handle_endtag(self, tag):
    bracketed = "</{0}>".format(tag)
    if tag not in self.permitted_tags:
      self.result += xssescape(bracketed)
    elif tag in self.open_tags:
      self.result += bracketed
      self.open_tags.remove(tag)
      
  def unknown_starttag(self, tag, attributes):
    self.handle_starttag(tag, None, attributes)
    
  def unknown_endtag(self, tag):
    self.handle_endtag(tag, None)
    
  def url_is_acceptable(self,url):
    ### Requires all URLs to be "absolute."
    parsed = parse.urlparse(url)
    return parsed[0] in self.allowed_schemes and '.' in parsed[1]
  
  def strip(self, rawstring):
    """Returns the argument stripped of potentially harmful HTML or Javascript code"""
    self.result = ""
    self.feed(rawstring)
    
    for endtag in self.open_tags:
      if endtag not in self.requires_no_close:
        self.result += "</{0}>".format(endtag)
        
    return self.result
  
  def xtags(self):
    """Returns a printable string informing the user which tags are allowed"""
    self.permitted_tags.sort()
    tg = ""
    for x in self.permitted_tags:
      tg += "<" + x
      if x in self.allowed_attributes:
        for y in self.allowed_attributes[x]:
          tg += ' {attr}=""'.format(attr=y)
          
      tg += "> "
      
      return xssescape(tg.strip())

