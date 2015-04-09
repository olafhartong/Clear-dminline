#!/usr/bin/env python

# requires BeautifulSoup4 (will not work with older versions)
# $ sudo easy_install BeautifulSoup4
# or use distro packagemanager

# README:
#
# plain output
# ./clear-dminline.py old.xml > new.xml
#
# pretty output
# ./clear-dminline.py old.xml | xmllint --format - > new.xml

from sys import stderr, argv, exit
from bs4 import BeautifulSoup
from pprint import pprint
from re import compile

input_file = 'running-config.xml'
net_obj_prefix = compile('^dm_inline_network_')
service_obj_prefix = compile('^dm_inline_(tcp|udp)')
service_prefix = compile('^(tcp|udp)-')

class ASAfix:
  def __init__(self, input_file):
    self._input_file = input_file

  def _debug(self, msg):
    stderr.write('%s\n' % msg)

  def read_input_file(self):
    self._debug('Reading file: %s' % self._input_file)

    with open(self._input_file) as f:
      self._input_content = f.read()  

  def parse_xml(self):
    self._xmlobj = BeautifulSoup(self._input_content, features='xml')
    return True

  def get_service_groups(self):
    self._service_groups = dict()

    for service_groups in self._xmlobj.findAll('service-group'):
     for entry in service_groups.findAll('entry', attrs={'name':service_obj_prefix}):
       service_group_name = None
       members = [] 

       # awkward, name is a preserved keyword in xml parser
       group_name = entry.attrs.get('name')

       # Get all address-group members
       for member in entry.findAll('member'):
        self._debug('Add service %s to replace-group %s' % (member.contents[0], group_name))
        members.append(member.contents[0])

       # Add all members to list
       if group_name is not None:
         self._service_groups[group_name] = members


  def get_address_groups(self):
    self._address_groups = dict()

    for address_groups in self._xmlobj.findAll('address-group'):
      for entry in address_groups.findAll('entry', attrs={'name':net_obj_prefix}):
       group_name = None
       members = []
 
       # awkward, name is a preserved keyword in xml parser
       group_name = entry.attrs.get('name')

       # Get all address-group members
       for member in entry.findAll('member'):
         self._debug('Add address %s to replace-group %s' % (member.contents[0], group_name))
         members.append(member.contents[0])

       # Add all members to list
       if group_name is not None:
         self._address_groups[group_name] = members 
      
  def cleanup(self):
    for address_groups in self._xmlobj.findAll('address-group'):
      for entry in address_groups.findAll('entry', attrs={'name':net_obj_prefix}):
        # Delete group from xml
        deleted = entry.extract()
        self._debug('Deleted tag "%s"' % deleted)
    
    for address_groups in self._xmlobj.findAll('service-group'):
      for entry in address_groups.findAll('entry', attrs={'name':service_obj_prefix}):
        # Delete group from xml
        deleted = entry.extract()
        self._debug('Deleted tag "%s"' % deleted)
    

  def replace_service_groups(self):
    for element in self._xmlobj.findAll('service'):
      for member in element.findAll('member', text = service_obj_prefix ):
        # Delete old object
        deleted = member.extract()
        self._debug('Deleted tag "%s"' % deleted)

        # add new objects
        for member_obj in self._service_groups[member.contents[0]]:
          new_membertag = self._xmlobj.new_tag('member')
          new_membertag.string = member_obj
          element.append(new_membertag)
	  self._debug('Appended tag "%s"' % new_membertag)
 
  def replace_address_groups(self, group_type):
    for element in self._xmlobj.findAll(group_type):
      for member in element.findAll('member', text = net_obj_prefix ):
        # Delete old object
        deleted = member.extract()
        self._debug('Deleted tag "%s"' % deleted)

        # add new objects
        for member_obj in self._address_groups[member.contents[0]]:
          new_membertag = self._xmlobj.new_tag('member')
          new_membertag.string = member_obj
          element.append(new_membertag)
	  self._debug('Appended tag "%s"' % new_membertag)
        
      
if __name__ == '__main__':
  try:
    input_file = argv[1]
  except:
    print 'Usage: %s <filename>' % (argv[0])
    exit(1)

  bro = ASAfix(input_file)
  bro.read_input_file()
  bro.parse_xml()
  bro.get_address_groups()
  bro.get_service_groups()
  bro.replace_address_groups('source')
  bro.replace_address_groups('destination')
  bro.replace_service_groups()
  bro.cleanup()
  
  # New xml to stdout
  print bro._xmlobj
