import xml.etree.ElementTree as etree 
import bpy

tree = etree.parse('/Users/emanueldemetrescu/Desktop/test.graphml')
test = tree.findall('.//{http://www.yworks.com/xml/graphml}NodeLabel')
for n in test:
    print(n.text)
    print(n.tag)