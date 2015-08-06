#!/bin/env python
"""
Try to deobfuscate PHP scripts obfuscated mainly with the usage of GLOBAL and some hexcoding substitutions.

See:
        http://atrack.h3x.eu/doc/presentation.pdf
	http://rebsnippets.blogspot.cz/asprox
	http://forum.directadmin.com/showthread.php?t=48038
	http://forums.modx.com/thread/91776/hacked-site-lang-php-and-assets-images-logo-php

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

TODO:
        - do some real parsing instead of regular expressions :D

"""



from binascii import hexlify
import re
import sys

file=sys.argv[1]
obfuscated=open(file).read()


def unhex(obfuscated):
	plain=obfuscated

	for i in range(0,256):
		what='\\x' + hexlify(chr(i))
		to=chr(i)
		plain=plain.replace(what, to)

        return plain

def unglobals(obfuscated):
	#Remove things like ${GLOBALS}["asdf"]="test"; ${${GLOBALS}["asdf"]}="value"
	#Into more readable ${test}="value"
	plain = obfuscated.replace('${"GLOBALS"}','$GLOBALS')

	s = re.search('\$GLOBALS\["([a-z]*)"\]="([^"]*)";',plain)
	while s != None:
		plain = plain.replace(s.group(),'')
		plain = plain.replace('$GLOBALS["' +  s.groups()[0] + '"]', s.groups()[1] )
		s = re.search('\$GLOBALS\["([a-z]*)"\]="([^"]*)";',plain)

	#Remove things like ${asdf} into $asdf (works better with code beautifiers)
	p1=re.compile("\\$\\{([a-z]*)\}")
	plain = p1.sub(r'$\1', plain)

	return plain

def unreference(obfuscated):
	#Remove references like $avqfonn="filename"; $filename=xnum_macros($ {$avqfonn});
	#Replace with $filename=xnum_macros("filename");
	
	p1=re.compile('\$([a-z]+)="([^"]+)"')
	s=p1.findall(obfuscated)
	plain=obfuscated

	for (key,value) in s:
		if value == '------------' or value == '------------':
			continue

		plain = plain.replace('$' + key + '="' + value + '";', '')
		plain = plain.replace('$' + key , '"' + value + '"' )
		plain = plain.replace('${"' + value + '"}', '$' + value )


	#Cosmetics
	plain = plain.replace('as$', 'as $')
	plain = plain.replace(')OR!', ') OR !')

	return plain



plain = unhex(obfuscated)
plain = unglobals(plain)
plain = unreference(plain)

print plain

