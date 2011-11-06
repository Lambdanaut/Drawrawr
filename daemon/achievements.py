#!/usr/bin/python2
#  ____                _____                  ___   ___
# |    \ ___ ___ _ _ _| __  |___ _ _ _ ___   |_  | |   |
# |  |  |  _| .'| | | |    -| .'| | | |  _|  |  _|_| | | 
# |____/|_| |__,|_____|__|__|__,|_____|_|    |___|_|___|
# ------------ A social website for artists ------------
# Achievements daemon - because everyone wants to be special.

def onCommentPost(user, commentContent):
  if commentContent.lower()[0:12].strip() is 'no one cares':
    pass
    # MySQL query count of occurances for user.