# import datetime

def allowed_file(filename,extensions):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in extensions

def fileType(filename):
  return filename.rsplit('.', 1)[1]

def print_list(l):
  newL = ""
  end = len(l)
  for item in range(0, end):
    if item == (end - 2):
      spaceWord = ", and "
    elif item == (end - 1):
      spaceWord = ""
    else: spaceWord = ", "
    newL += l[item] + spaceWord
  return newL

def unsplit(listOfStrings):
  if listOfStrings != []: return reduce(lambda prior, new: prior + " " + new ,listOfStrings)
  else: return ""

def dict_to_list(d):
  l = []
  for k in d:
    l.append(d[k])
  return l

def all_in_list (list1, list2):
  """Returns true if all of the elements from list1 are in list2"""
  return all(map(lambda c: c in list2, list1) )

def parse_comment_map(cMap):
  '''
  Returns a string that can be used in mongodb to find a comment reply

  Input:  "1,2,3,4,5"
  Output: "r.1.r.2.r.3.r.4.r.5.r"
  '''
  if cMap == "": return "r"
  validMap = "r."
  currentObject = ""
  for c in cMap:
    if c == ",":
      int(currentObject)
      validMap += currentObject + ".r."
      currentObject = ""
    else: currentObject += c
  int(currentObject)
  validMap += currentObject + ".r"
  return validMap  

def compare_dicts(d1,d2):
  '''
  Despite the name, this just checks to make sure every key in d1 has a counterpart in d2 that's value is the same. 
  '''
  for key in d1:
    if key in d2:
      if not d1[key] == d2[key]: return False
    else: return False
  return True

def compare_dict_keys(d1,d2):
  '''
  Same as above, but compares the key names rather than the key values. 
  '''
  for key in d1:
    if not key in d2: return False
  return True

def conc_dict_values(d1,d2):
  ''' Takes two dicts with the same keys and puts the key's values together like this: conc_dict_values({1:"o",2:"tw"},{1:"ne",2:"o"}) == {1:["o","ne"],2:["tw","o"]} '''
  newD = {}
  for key in d1:
    if key in d2:
      newD[key] = [d1[key], d2[key] ]
  return newD

def url_decode(string):
  '''
  Decodes a URL string to a dict of strings
  Example: url_decode("name=lambdanaut&age=20&") = {"name" : "lambdanaut", "age" : "20"}
  Note: Last character in string must be ampersand
  '''
  result = {}
  curVal  = ""
  curName = ""
  isName=True
  for letter in string:
    if isName:
      if letter != "=": curName += letter
      else: isName=False
    else:
      if letter != "&": curVal += letter
      else:
        result[curName] = curVal
        curVal = curName = ""
        isName=True
  return result

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago" 