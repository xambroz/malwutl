#!/bin/env python
"""
Try to deobfuscate VBA scripts obfuscated mainly with the CharW() substitutions.

See:
	http://pastebin.com/BBzXzM13
	https://malwr.com/analysis/NTQzNDUwMDNiY2I5NGQyMGI3NGZhNjNkYTA4YmI5Mzc/
	https://www.hybrid-analysis.com/sample/cf0dd5702544e1cf6976dcddf4cdae0b9be17a3f170c2c514e5dd746bbb97e6e?environmentId=4
	https://www.hybrid-analysis.com/sample/90c6fe2008be9a24cc4a4842a91132259453b2ea1c831513c68514e30f083ee2?environmentId=2

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
	- limit max iterations
	- do some real parsing instead of regular expressions :D

"""



import re
import sys


def re_reverse(matchobj):
	"""
	Return the string in reverse order.
	"""
	return matchobj.group(1)[::-1]

def re_chr(matchobj):
	"""
	Print plain string instead of chrw(#).
	For example "o" instead of ChrW$(111)
	"""
	return '"' + chr(int(matchobj.group(1))) + '"'


def re_ltrim(matchobj):
	"""
	Perform the LTrim, for example: LTrim("   string   ") => "string   "
	"""
	return '"' + matchobj.group(1).lstrip() + '"'

def re_rtrim(matchobj):
	"""
	Perform the RTrim, for example: RTrim("   string   ") => "string   "
	"""
	return '"' + matchobj.group(1).rstrip() + '"'

def re_escape(string):
	"""
	Escape string to be used as RE pattern
	"""
	result = re.sub(r'([\[\]{}()\\?"])',r'\\\1',string)
	return result


def deobfuscate_step(vbascript):
        """
	Process one iteration of deobfuscation of VBA script.
	"""

	plain = vbascript

	#Join strings - "aaa" & "bbb" => "aaabbb"
	plain = re.sub(r'"\s*[&+]\s*"','',plain)

	#Replace things like ChrW$(111) => "s", case insensitive
	plain = re.sub(r'Chr[WB]*[$]*\(\s*([+-]*\d+)\s*\)', re_chr, plain, 0, re.I)

	#Replace things like LTrim("  111  ") => "111   ", case insensitive
	plain = re.sub(r'LTrim\(\s*"([^"]*)"\s*\)', re_ltrim, plain, 0, re.I)

	#Replace things like RTrim("  111  ") => "111   ", case insensitive
	plain = re.sub(r'RTrim\(\s*"([^"]*)"\s*\)', re_rtrim, plain, 0, re.I)

        #Reverse strings - StrReverse("asdf") => "fdsa"
        plain = re.sub(r'StrReverse\(\s*("[^"]*")\s*\)',re_reverse,plain)

	#Replace instances of the string variables with the string itself
	while re.search('\n\s*(\w+)\s*=\s*("[^"]*")\s*\n',plain):
		#Match line with something like: variable = "string"
		m=re.search('\n\s*(\w+)\s*=\s*("[^"]*")\s*\n',plain)
		expression=m.group(0)
		variable=m.group(1)
		value=m.group(2)

		#Remove the line with the expression
		plain = re.sub(re_escape(expression),r'\n\n',plain)

		#Search for DIM declarations of the variable
		#Delete: DIM variable As String
		m=re.search(r'\n(DIM\s+[^\n]*)' + variable + '([^\n]*\sAs\s+String)\s*\n',plain,re.I)
		if None != m:
			plain = re.sub(r'\n(DIM\s+[^\n]*)' + variable + '([^\n]*\sAs\s+String)\n',r'\n\1\2\n', plain, 0, re.I)
			plain = re.sub(r'\n(DIM\s+),',r'\n\1', plain, 0, re.I)
			plain = re.sub(r',(\s*As\s+String)\s*\n',r'\n\1', plain, 0, re.I)
			plain = re.sub(r'\n(DIM\s+[^\n]*),,([^\n]*\sAs\s+String)\n',r'\n\1,\2\n', plain, 0, re.I)
			plain = re.sub(r'\n(DIM\s+As\s+String)\n',r'\n\n', plain, 0, re.I)

		#Replace variables with the value string
		plain = re.sub(re_escape(variable), value, plain, 0, re.I)


		#print "===== DEBUG ==================================================="
		#print "Expression='%s' , Variable='%s', Value='%s'" % ( expression, variable, value )
		#print plain
		#print "====================================================="


	#Replace double empty lines
	plain =	re.sub(r'\n\n+\n',r'\n\n',plain)

	return plain


def deobfuscate(vbascript):
	"""
	Iterate with the deobfuscation of the VBA script until the input is same as the output
	"""

	new_text=vbascript
	old_text=""

	while old_text != new_text:
		old_text=new_text
		new_text=deobfuscate_step(old_text)

	return new_text




#==== Main ===============================
def main():
	filename = sys.argv[1]

	i=0
	f=open(filename,'r')
	vba=f.read()

	plain=deobfuscate(vba)
	print "%s" % plain


#===============================================================================
if __name__ == '__main__':
        main()


