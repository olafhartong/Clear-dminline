# Clear-dminline

This tool is intended to resolve all dminline groups and replace it to its containing objects. 

After migrating a Cisco ASA config to a Palo Alto config you remain with all these horrible DMINLINE objects, this tool resolves all members and replaces the ogroup object by its members, this works for Source/destination and services.

requires BeautifulSoup4 (will not work with older versions)
` $ sudo easy_install BeautifulSoup4`
 or use distro packagemanager



 plain output
`./clear-dminline.py old.xml > new.xml`

 pretty output
` ./clear-dminline.py old.xml | xmllint --format - > new.xml`
 
 
 //special thanks to shuizinga
