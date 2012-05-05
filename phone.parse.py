#!/usr/bin/python

import commands
import re
import shutil
import datetime
import csv

#Used to see when report from last updated/generated
curDate = datetime.datetime.now()
curDate = curDate.strftime("%Y-%m-%d")

#Start reporting file
reportFile = "/var/www/html/listing/index.html"
try:
  report = open(reportFile, "w")
  report.write("<HTML>\n\t<HEAD>\n")
  report.write("\t\t<style type=\"text/css\">\n")
  report.write("\t\t\t\ta { text-decoration: none; }\n")
  report.write("\t\t\t\ta:hover { text-decoration: underline; }\n")
  report.write("\t\t</style>\n")
  report.write("<TITLE> Phone listing - last generated " + curDate + "</TITLE>\n\t</HEAD>\n\t<BODY>\n")
  report.write("<BR><a href=\"#freenum\">Jump to free number list</a><BR>\n")

except:
  print "Unable to open report file."

###############################################
# Create bulleted list of names and hyperlinks#
###############################################

#write rep name and column headers
report.write("\t\t<TABLE style='border: 1px #d79900 solid; text-align: center'><BR>\n")
report.write("\t\t<TR style='background-color: #CCCCCC'><TD><B> Phone Listing </B></TD></TR><TR><TD>Display Name</TD><TD>Phone #</TR></TD>\n")

#open rep data call file
registrations = commands.getoutput("ls /var/ftp/*reg*.cfg")

phoneListing = {}

for phone in registrations.split('\n'):
  print "Opening: " + phone
  config = open(phone, "r").read()

  #Grab phone user's name
  displayName = re.search('reg.1.displayName="(.+)[^"]', config)

  #Grab phone user's extension
  address = re.search('reg.1.address="(\d+)"', config)

  #If the address is blank, skip this file
  if (address is None):
    continue

  #Add address to associative array/dictionary
  phoneListing[displayName.group(1)[:-1]] = address.group(1)

#List of all phone registration files in tftp directory
registrations = commands.getoutput("ls /tftpboot/*reg*.cfg")

#Loop through registrations, building a name : address dictionary
for phone in registrations.split('\n'):
  if (phone == "/tftpboot/reg.cfg"):
    continue
  print "Opening: " + phone
  config = open(phone, "r").read()
  displayName = re.search('reg.1.displayName="(.+)[^"]', config)

  address = re.search('reg.1.address="(\d+)"', config)
  phoneListing[displayName.group(1)[:-1]] = address.group(1)

#Write entries to report in alphabetical order
for k, v in sorted(phoneListing.iteritems()):
  report.write("\t\t<TR><TD>"  + k + "</TD><TD>" + v + "</TD></TR>\n")

report.write("<TR><TD colspan=2><HR></TD></TR>\n")
report.write("<TR><TD colspan=2><a name=freenum>Numbers available from 3402 - 3479</a></TD></TR>\n")
report.write("<TR><TD colspan=2><HR></TD></TR>\n")

phoneRange = range(3400, 3480)

commands.getoutput("rm -f /tmp/inboundroutes.csv")

mysql_query = 'mysql -u root -e "use asterisk; select extension from incoming into outfile \'/tmp/inboundroutes.csv\'" --password=xxxxxxx'
commands.getoutput(mysql_query)

routesUsed = []
route_reader = csv.reader(open("/tmp/inboundroutes.csv", "rb"), delimiter=',')

#populate routesUsed list with inbound routes from mysql
for row in route_reader:
  try:
    routesUsed.append(row[-1])
  except:
    print "skipping."

#remove all routes found in used inbound routes list
for ext in routesUsed:
  try:
    print "Removing " + str(ext[6:]) + " from phoneRange."
    phoneRange.remove(int(ext[6:]))
  except:
    print "skipping"

for freeNum in phoneRange:
  report.write("<TR><TD colspan=2>" + str(freeNum) + "</TD></TR>\n")

report.write("\t\t</TABLE>\n")

report.write("\t</BODY>\n</HTML>")
report.close()
