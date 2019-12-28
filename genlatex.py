#! /usr/bin/python3
import getpass
import os
import sys
import csv
import argparse
import shutil

from pathlib import Path

den_vals = {'i':1,'v':5,'x':10,'l':50,'c':100,'d':500,'m':1000}

def isroman(string):
	i=0
	string = string.lower()
	while i < len(string):
		if string[i] in den_vals:
			pass
		else:
			return False
		i += 1
	return True

def arabic(ro):
	if(ro == 'None'):
		return 0
	# val_dens = {1:'i',5:'v',10:'x',50:'l',100:'c',500:'d',1000:'m'}
	roman = ro.lower()
	output = 0
	largest_den = 0
	i = -1
	while i >= -len(roman):
		if(roman[i] == '-'):
			assert(i == -len(roman))
			output = -output
			break
		
		ch = roman[i]
		assert(ch in den_vals)
		current_val = den_vals[ch]
		
		if(current_val < largest_den):
			output -= current_val
		else:
			largest_den = current_val
			output += current_val
			
		i -= 1
	return output

def roman(i):
	groups = [('x','v','i'),('c','l','x'),('m','d','c')]
	ret = ''
	num = int(i)
	if(i == 0):
		return 'None'
	negative = False
	if(num < 0):
		negative = True
		num = -num
	for current_group in range(0,len(groups)):
		one = 10**current_group
		five = one*5
		ten = one*10
		s_ten, s_five, s_one = groups[current_group]
		ones = num % 10
		num = int((num-ones)/10)
		# print(str(ones) + " " + str(num))
		if(ones == 0):
			pass
		elif(ones == 9):
			ret = s_one+s_ten+ret
		elif(ones == 4):
			ret = s_one+s_five+ret
		elif(ones < 5):
			tallies = ''
			for _ in range(0,ones):
				tallies += s_one
			ret = tallies+ret
		else:
			tallies = s_five
			for _ in range(0,ones-5):
				tallies += s_one
			ret = tallies+ret
	ret = ret.lower()
	if(negative):
		ret = '-'+ret
	return ret
	
class Roman:
	num = 0
	
	def __str__(self):
		return roman(self.num)
	
	def __int__(self):
		return self.num
	
	def __float__(self):
		return self.num
	
	def __double__(self):
		return self.num
	
	def __repr__(self):
		return str(self)
	
	def __init__(self,k):
		newnum = 0
		try:
			newnum = int(k)
		except ValueError:
			newnum = arabic(k)
		# if(type(k) == int or type(k) == float):
		# 	newnum = int(k)
		# elif(type(k) == str):
		# 	newnum = arabic(k)
		# elif(type(k) == Roman):
		# 	newnum = k.num
		self.num = newnum
	
	def __add__(self,other):
		return Roman(self.num+Roman(other).num)
	
	def __sub__(self,other):
		return Roman(self.num-Roman(other).num)
		
	def __mul__(self,other):
		return Roman(self.num*Roman(other).num)
	
	def __neg__(self):
		return Roman(-self.num)
		
	def __radd__(self,other):
		return Roman(self.num+Roman(other).num)
	
	def __rsub__(self,other):
		return Roman(self.num-Roman(other).num)
		
	def __rmul__(self,other):
		return Roman(self.num*Roman(other).num)

def roman_range(a,b):
	minimum = int(a)
	maximum = int(b)
	return [Roman(i) for i in range(minimum,maximum)]
	
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
	minimum = int(a)
	maximum = int(b)
	return [zpad(i,length) for i in range(minimum,maximum)]

def indents(num):
	return ' '.join(['\t' for _ in range(0,int(num))])

def gen_enumerate(lst,indent=0):
	if(lst == []):
		return []
	tabs = indents(indent)
	output = [tabs+"\\begin{enumerate}"]
	for i in lst:
		if(type(i) == list or type(i) == tuple):
			if(len(i) >= 2):
				output.append(tabs+'\t'+"\\item["+str(i[0])+".]")
				if(type(i[1]) == list or type(i[1]) == tuple):
					output.append(gen_enumerate(i[1],indent+1))
				else:
					output.append(tabs+'\t\t'+"\\input{"+str(i[1])+"}")
		else:
			output.append(tabs+'\t'+"\\item["+str(i)+".]")
	output.append(tabs+"\\end{enumerate}")
	return output

def print_list(lst,file=sys.stdout):
	for i in lst:
		if(type(i) == list):
			print_list(i,file)
		else:
			print(i,file=file)

def lastslash(arg):
	string = str(arg)
	i = len(string)-1
	while(i >= 0):
		if(string[i] == '/'):
			return string[i+1:]
		i -= 1
	return string

def getwd():
	return lastslash(os.getcwd())

def read_file(path):
	path = os.path.realpath(path)
	file = open(path,'r')
	ret = [word for line in file for word in line.split()]
	file.close()
	return ret

def chr_range(a,b):
	first = ord(a)
	last = ord(b)
	return [chr(i) for i in range(first,last+1)]
	
def form_file_rec(lst,i,genfiles,path):
	output = []
	while(i < len(lst)):
		if(lst[i].lower() == 'end'):
			break;
		elif(lst[i].lower() == 'list'):
			if(type(output[-1]) == list or type(output[-1]) == tuple):
				output[-1] = output[-1][0]
				
			get, i = form_file_rec(lst,i+1,genfiles,path+output[-1]+"/")
			output[-1] = (output[-1],get)
		
		elif(lst[i] == ".."):
			output.pop()
			first = lst[i-1]
			last = lst[i+1]
			if(isroman(first) and isroman(last)):
				temp = roman_range(Roman(first),Roman(last)+1)
			elif(first.isnumeric() and last.isnumeric()):
				temp = zpad_range(int(first),int(last)+1)
			elif(first.isalpha() and len(first) == 1 and last.isalpha() and len(last) == 1):
				temp = chr_range(first,last)
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
			break;
		elif(lst[i].lower() == 'list'):
			get, i = form_file_rec(lst,i+1,genfiles,"problems/")
			output += get

		i += 1

	return output
	
def tex_from_file(path,genfiles=False):
	lst = read_file(path)
	return tex_from_lst(lst,genfiles)

def tex_from_str(string,genfiles=False):
	lst = string.split()
	return tex_from_lst(lst,genfiles)

import datetime

def getdate():
	date = datetime.datetime.now()
	return date.strftime("%d %B %Y")

def mkdir_p(path):
	try:
		os.mkdir(path)
	except FileExistsError:
		pass

def make_recursive_directories(lst,path="problems/"):
	i = 0
	
	mkdir_p(path)
	
	while i < len(lst):
		if(type(lst[i])==list or type(lst[i])==tuple):
			if(type(lst[i][1])==list or type(lst[i][1])==tuple):
				make_recursive_directories(lst[i][1],path+lst[i][0]+"/")
			else:
				Path(lst[i][1]).touch(exist_ok=True)
		else:
			print("Creating entry for " + lst[i])
			Path(path + lst[i]+".tex").touch(exist_ok=True)
		i += 1

def check_defaults_dir(defaults_dir):
	optional_dir = defaults_dir + "/optional"
	defaults_file = defaults_dir + "/defaults.tex"
	mkdir_p(defaults_dir)
	mkdir_p(optional_dir)
	Path(defaults_file).touch(exist_ok=True)
	
def check_localinfo(mainfile):
	Path(".genlatex_project_info").touch(exist_ok=True)
	localinfo = open(".genlatex_project_info",'w')
	print(mainfile,file=localinfo)
	localinfo.close()

# Credit: https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth/31039095
def copytree(src, dst, symlinks=True, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-f","--file",
						dest="filepath",
						default='',
						help="Specify document structure input file path.")
	parser.add_argument("-s","--string",
						dest="string",
						default='',
						help="Specify document structure as a string (overrides file input).")
	parser.add_argument("-a","--author",
						dest="author",
						default="Anonymous",
						help="Specify author (default is 'Anonymous').")
	parser.add_argument("-t","--title",
						dest="title",
						default=getwd(),
						help="Specify title (default is the working directory name -- '"+getwd()+"' in this case).")
	parser.add_argument("-d","--date",
						dest="date",
						default=getdate(),
						help="Specify date string (default is the current system date -- '"+getdate()+"' in this case).")
	parser.add_argument("-g","--generate-files",
						dest="genfiles",
						default=False,
						action="store_true",
						help="Make the script generate individual problem files stored in the 'problems' directory according to the document structure.  Input statements are auto-generated for all problems.")
	parser.add_argument("--defaults",
						dest="defaults_path",
						default=str(Path.home())+"/latexdefaults",
						help="Specify directory containing 'defaults.tex' and 'options/[OPTION].tex', your default preambles (default is '"+str(Path.home())+"/latexdefaults').  Creates directory if it does not already exist.")
	parser.add_argument("-n","--no-symlink",
						dest="no_symlink",
						default=False,
						action="store_true",
						help="By default, "+sys.argv[0]+" symlinks your defaults directory to your local directory.  This is so you don't have tens of copies of the same files that are inputted into every document.  However, if you'd like to be able to compile this project on a different computer, then you'll need to copy the defaults directory into the local project directory.  This tag does that.")
	parser.add_argument("--optional",
						dest="options",
						default = [],
						nargs='+',
						help="Add optional preambles stored in the 'options' subdirectory of your defaults directory.  For example, if I wrote a file '[DEFAULTS_DIR]/options/physics.tex', I could run `"+sys.argv[0]+" [ARGS] --optional physics` to input that file into the project.  Useful for files containing domain specific LaTeX commands or libraries.")
	parser.add_argument("-o","--output-file",
						dest="output_file",
						default='',
						help="Specify output file (by default, "+sys.argv[0]+" outputs to standard output).")
	
	args = parser.parse_args()
	
	check_defaults_dir(args.defaults_path)
	
	local_defaults_path = "defaults"
	
	if not Path(local_defaults_path).exists():
		if(args.no_symlink):
			copytree(args.defaults_path,local_defaults_path)
		else:
			os.symlink(args.defaults_path,local_defaults_path)
	
	parsed = []
	
	if(len(args.filepath) != 0):
		parsed = tex_from_file(args.filepath,args.genfiles)
	elif(len(args.string) != 0):
		parsed = tex_from_str(args.string,args.genfiles)
	
	if(args.genfiles):
		make_recursive_directories(parsed)
	
	output_file = sys.stdout
	
	if(args.output_file != ''):
		output_file = open(args.output_file,'w')
		check_localinfo(args.output_file)
	
	print("\\documentclass[a4paper]{article}",file=output_file)
	print("\\input{"+local_defaults_path+"/defaults.tex}",file=output_file)
	
	for option in args.options:
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