#!/usr/bin/env python3
import os

localvars_table = '<table>'
for key, value in os.environ.items():
  localvars_table += '<tr><td>%s: %s</td></tr>' %(key, value)
localvars_table += '</table>'

print("Content-type: text/html")
print("")
print("""<html><body>
<p>Hello World! Your custom CGI script is working. Here are your current Python local variables.</p>
%s
<p>NOTE: If you want to write useful CGI script, try the Python 'cgi' module. See cgitest.py script.</p>
</body></html>""" % (localvars_table))
