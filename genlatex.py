#! /usr/bin/python3
import getpass
import os
import sys
import csv
import argparse
import shutil
import datetime

from pathlib import Path


## Roman Numerals

roman_characters = {'i':1,'v':5,'x':10,'l':50,'c':100,'d':500,'m':1000}

def check_roman_characters(string):
	if(string == "None"):
		return True
	
	string = string[1:].lower() if (string[0] == '-') else string.lower()
	
	for char in string:
		if not char in roman_characters:
			return False
	
	return True

def arabic(ro):
	if(ro == "None" or not check_roman_characters(ro)):
		return 0
	
	negative = ro[0] == '-'
	
	ro = ro[1:] if negative else ro
	
	roman = ro.lower()
	
	output = 0
	largest_den = 0
	
	for ch in reversed(roman):
		current_val = roman_characters[ch]
		
		if(current_val < largest_den):
			output -= current_val
		else:
			largest_den = current_val
			output += current_val
	
	return -output if negative else output

def roman_string_from_num(num):
	groups = [('x','v','i'),('c','l','x'),('m','d','c')]
	ret = ''
	num = int(num)
	
	if(num == 0):
		return 'None'
	
	negative = num < 0
	num = -num if negative else num
	
	for current_group in range(0,len(groups)):
		one = 10**current_group
		five = one*5
		ten = one*10
		
		s_ten, s_five, s_one = groups[current_group]
		
		ones = num % 10
		num = int((num-ones)/10)
		
		if(ones == 0):
			pass
		elif(ones == 9):
			ret = s_one+s_ten+ret
		elif(ones == 4):
			ret = s_one+s_five+ret
		else:
			tallies = ''if (ones<5) else s_five
			for _ in range(0,ones - (0 if (ones<5) else 5)):
				tallies += s_one
			ret = tallies+ret
			
	if(negative):
		ret = '-'+ret
	return ret
	
class Roman:
	value = 0
	
	def __str__(self):
		return roman_string_from_num(self.value)
	
	def __int__(self):
		return self.value
	
	def __float__(self):
		return self.value
	
	def __double__(self):
		return self.value
	
	def __repr__(self):
		return str(self)
	
	def __init__(self,k):
		newvalue = 0
		try:
			newvalue = int(k)
		except ValueError:
			newvalue = arabic(k)
		self.value = newvalue
	
	def __add__(self,other):
		return Roman(self.value+Roman(other).value)
	
	def __sub__(self,other):
		return Roman(self.value-Roman(other).value)
		
	def __mul__(self,other):
		return Roman(self.value*Roman(other).value)
	
	def __neg__(self):
		return Roman(-self.value)
		
	def __radd__(self,other):
		return Roman(self.value+Roman(other).value)
	
	def __rsub__(self,other):
		return Roman(self.value-Roman(other).value)
		
	def __rmul__(self,other):
		return Roman(self.value*Roman(other).value)

# Ranges

def roman_range(a,b):
	return map(lambda x: Roman(x),range(int(a),int(b)))
	
def zpad(i,pad):
	num = int(i)
	string = str(num)
	assert(len(string) <= pad)
	zrs = ''
	while(len(string)+len(zrs) < pad):
		zrs += '0'
	return zrs+string

def zpad_range(a,b):
	length = len(str(b))
	return map(lambda x: zpad(x,length),range(int(a),int(b)))

def chr_range_inclusive(a,b):
	return [chr(i) for i in range(ord(a),ord(b)+1)]

# Misc. String Tools

def concat_list_of_strings(lst):
	output = ""
	for entry in lst:
		output += entry
		
	return output

def indents(num):
	return concat_list_of_strings(map(lambda x: '\t',range(0,num)))

def getwd():
	return lastslash(os.getcwd())
	
def getdate():
	date = datetime.datetime.now()
	return date.strftime("%d %B %Y")
	
def lastslash(arg):
	string = str(arg)
	i = len(string)-1
	while(i >= 0):
		if(string[i] == '/'):
			return string[i+1:]
		i -= 1
	return string
	
# Printing

def print_list(lst,file=sys.stdout):
	if(type(lst) == list):
		map(lambda x: print_list(x,file),lst)
	else:
		print(lst,file=file)

# OS Tools

def mkdir_p(path):
	try:
		os.mkdir(path)
	except FileExistsError:
		pass

def make_recursive_directories(lst,path="problems/",genboxes=False):
	i = 0
	
	mkdir_p(path)
	
	while i < len(lst):
		if(type(lst[i])==list or type(lst[i])==tuple):
			if(type(lst[i][1])==list or type(lst[i][1])==tuple):
				make_recursive_directories(lst[i][1],path+lst[i][0]+"/")
			else:
				Path(lst[i][1]).touch(exist_ok=True)
		else:
			name = path + lst[i]+".tex"
			Path(name).touch(exist_ok=True)
			if(genboxes and os.stat(name).st_size == 0):
				tempfile = open(name,'w')
				print("\\begin{mdframed}\n\n\\end{mdframed}",file=tempfile)
				tempfile.close()
		i += 1

def check_defaults_dir(defaults_dir):
	optional_dir = defaults_dir + "/optional"
	defaults_file = defaults_dir + "/defaults.tex"
	mkdir_p(defaults_dir)
	mkdir_p(optional_dir)
	Path(defaults_file).touch(exist_ok=True)
	if(os.stat(defaults_file).st_size == 0):
		tempfile = open(defaults_file,'w')
		print("% Note: if you want to \\input{[filename]} in this directory, then you must write \\input{defaults/[filename]}.",file=tempfile)
		tempfile.close()
	
def check_localinfo(mainfile):
	Path(".genlatex_project_info").touch(exist_ok=True)
	localinfo = open(".genlatex_project_info",'w')
	print(mainfile+"\n0",file=localinfo)
	localinfo.close()

def copytree(src, dst, symlinks=True, ignore=None):
	# Credit: https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth/31039095
	for item in os.listdir(src):
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isdir(s):
			shutil.copytree(s, d, symlinks, ignore)
		else:
			shutil.copy2(s, d)

def read_words_from_file(path):
	path = os.path.realpath(path)
	file = open(path,'r')
	ret = [word for line in file for word in line.split()]
	file.close()
	return ret

# Enumerate Generation

def gen_enumerate(lst,indent=0):
	if(lst == []):
		return []
	
	tabs = indents(indent)
	
	output = [tabs+"\\begin{enumerate}"]
	
	for i in lst:
		if(type(i) == list or type(i) == tuple):
			# If entry is a list/tuple, then there are two cases.
			#	1) The entry represents an element with a file path to input
			#	2) The entry represents an element with a nested enumerate
			assert(len(i) == 2)
			
			output.append(tabs+'\t'+"\\item["+str(i[0])+".]")
			
			if(type(i[1]) == list or type(i[1]) == tuple):
				output.append(gen_enumerate(i[1],indent+1))
				
			else:
				output.append(tabs+'\t\t'+"\\input{"+str(i[1])+"}")
				
		else:
			output.append(tabs+'\t'+"\\item["+str(i)+".]")
	
	output.append(tabs+"\\end{enumerate}")
	return output
	
def gen_tex_file_rec(lst,i,genfiles,path):
	output = []
	while(i < len(lst)):
		if(lst[i].lower() == 'end'):
			break
			
		elif(lst[i].lower() == 'list'):
			if(type(output[-1]) == list or type(output[-1]) == tuple):
				output[-1] = output[-1][0]
				
			get, i = gen_tex_file_rec(lst,i+1,genfiles,path+output[-1]+"/")
			output[-1] = (output[-1],get)
		
		elif(lst[i] == ".."):
			output.pop()
			
			temp = []
			
			first = lst[i-1]
			last = lst[i+1]
			
			if(check_roman_characters(first) and check_roman_characters(last)):
				temp = roman_range(Roman(first),Roman(last)+1)
				
			elif(first.isnumeric() and last.isnumeric()):
				temp = [str(x) for x in range(int(first),int(last)+1)]
				
			elif(first.isalpha() and len(first) == 1 and last.isalpha() and len(last) == 1):
				temp = chr_range_inclusive(first,last)
				
			else:
				assert(False)
				
			if(genfiles):
				output += [(str(t),path+str(t)+".tex") for t in temp]
				
			else:
				output += temp
				
			i += 1
			
		else:
			if(genfiles):
				output.append((lst[i],path+lst[i]+".tex"))
				
			else:
				output.append(lst[i])
				
		i += 1
		
	return (output,i)

def tex_from_lst(lst,genfiles=False):
	output = []
	i=0
	while(i < len(lst)):
		if(lst[i].lower() == 'end'):
			break
		elif(lst[i].lower() == 'list'):
			get, i = gen_tex_file_rec(lst,i+1,genfiles,"problems/")
			output += get

		i += 1

	return output
	
def tex_from_file(path,genfiles=False):
	lst = read_words_from_file(path)
	return tex_from_lst(lst,genfiles)

def tex_from_str(string,genfiles=False):
	lst = string.split()
	return tex_from_lst(lst,genfiles)

# Main

def main():
	
	local_defaults_path = "defaults"
	
	parsed = []
	
	output_file = sys.stdout
	
	# CMD Arguments
	
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-f","--file",
		dest="filepath",
		default='',
		help="Specify document structure input file path.")
	parser.add_argument(
		"-s","--string",
		dest="string",
		default='',
		help="Specify document structure as a string (overrides file input).")
	parser.add_argument(
		"-o","--output-file",
		dest="output_file",
		default='',
		help="Specify output file (by default, "+sys.argv[0]+" outputs to standard output).")
	parser.add_argument(
		"-a","--author",
		dest="author",
		default="Anonymous",
		help="Specify author (default is 'Anonymous').")
	parser.add_argument(
		"-t","--title",
		dest="title",
		default=getwd(),
		help="Specify title (default is the working directory name -- '"+getwd()+"' in this case).")
	parser.add_argument(
		"-d","--date",
		dest="date",
		default=getdate(),
		help="Specify date string (default is the current system date -- '"+getdate()+"' in this case).")
	parser.add_argument(
		"-g","--generate-files",
		dest="genfiles",
		default=False,
		action="store_true",
		help="Make the script generate individual problem files stored in the 'problems' directory according to the document structure.  Input statements are auto-generated for all problems.")
	parser.add_argument(
		"-b","--generate-files-boxes",
		dest="boxes",
		default=False,
		action="store_true",
		help="Same as -g/--generate-files, except it puts mdframed boxes in each file.")
	parser.add_argument(
		"--defaults",
		dest="defaults_path",
		default=str(Path.home())+"/latexdefaults",
		help="Specify directory containing 'defaults.tex' and 'options/[OPTION].tex', your default preambles (default is '"+str(Path.home())+"/latexdefaults').  Creates directory if it does not already exist.")
	parser.add_argument(
		"-n","--no-symlink",
		dest="no_symlink",
		default=False,
		action="store_true",
		help="By default, "+sys.argv[0]+" symlinks your defaults directory to your local directory.  This is so you don't have tens of copies of the same files that are inputted into every document.  However, if you'd like to be able to compile this project on a different computer, then you'll need to copy the defaults directory into the local project directory.  This tag does that.")
	parser.add_argument(
		"--optional",
		dest="options",
		default = [],
		nargs='+',
		help="Add optional preambles stored in the 'options' subdirectory of your defaults directory.  For example, if I wrote a file '[DEFAULTS_DIR]/options/physics.tex', I could run `"+sys.argv[0]+" [ARGS] --optional physics` to input that file into the project.  Useful for files containing domain specific LaTeX commands or libraries.")

	args = parser.parse_args()
	
	# Make Defaults Directory if it Doesn't Exist
	
	check_defaults_dir(args.defaults_path)
	
	# Link/copy Defaults Directory Locally
	
	if not Path(local_defaults_path).exists():
		if(args.no_symlink):
			copytree(args.defaults_path,local_defaults_path)
		else:
			if os.path.realpath(args.defaults_path) != os.path.realpath(local_defaults_path):
				os.symlink(args.defaults_path,local_defaults_path)
	
	# Read Structure Input, if Any
	
	if(len(args.filepath) != 0):
		parsed = tex_from_file(args.filepath,args.genfiles)
	elif(len(args.string) != 0):
		parsed = tex_from_str(args.string,args.genfiles)
	
	if(args.genfiles or args.boxes):
		make_recursive_directories(parsed,genboxes=args.boxes)
	
	# Set Output File, if Any
	
	if(args.output_file != ''):
		output_file = open(args.output_file,'w')
		check_localinfo(args.output_file)
	
	# Print Document
	
	print("\\documentclass[a4paper]{article}",file=output_file)
	print("\\input{"+local_defaults_path+"/defaults.tex}",file=output_file)
	
	for option in args.options:
		# Link Optional Defaults Files
		
		option_path = local_defaults_path+"/optional/"+option+".tex"
		
		if(not Path(option_path).exists()):
			print("Error: option '" + option + "' at " + option_path + " does not exist. Omitted from output.",file=sys.stderr)
			
		else:
			print("\\input{"+option_path+"}",file=output_file)
			
	print("\\title{"+args.title+"}",file=output_file)
	print("\\author{"+args.author+"}",file=output_file)
	print("\\date{"+args.date+"}",file=output_file)
	print("\\begin{document}\n\t\\maketitle",file=output_file)
	
	print_list(gen_enumerate(parsed,1),file=output_file)
	
	print("\\end{document}",file=output_file)
	
	if(args.output_file != ''):
		output_file.close()

main()