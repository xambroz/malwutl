#!/bin/env python
"""
Extract OLE object from ActiveMime, based on hints from @decalage2

See:
	https://twitter.com/decalage2/status/573175912612687873
	https://isc.sans.edu/forums/diary/XML+A+New+Vector+For+An+Old+Trick/19423/
	http://sanesecurity.blogspot.nl/2015/03/remittance-advice-rem-xml.html
	http://www.file-extensions.org/mso-file-extension-activemime-object-file

Author:        Michal Ambroz <rebus@seznam.cz>
License:       Gnu General Public License

    Copyright (C) 2015  Michal Ambroz <rebus@seznam.cz>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys
import zlib

def am2ole(activemime):
	try:
		#This should work for Word
		return zlib.decompress(activemime[0x32:])
	except:
		None


	try:
		#This should work for Excel
		return zlib.decompress(activemime[0x22A:])
	except:
		return ""



#==== Main ===============================
def main():
        filename = sys.argv[1]

        i=0
        f=open(filename,'r')
        activemime=f.read()

        print "%s" % am2ole(activemime)


#===============================================================================
if __name__ == '__main__':
        main()

