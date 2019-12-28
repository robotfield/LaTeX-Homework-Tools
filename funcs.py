def arabic(roman):
	# val_dens = {1:'i',5:'v',10:'x',50:'l',100:'c',500:'d',1000:'m'}
	den_vals = {'i':1,'v':5,'x':10,'l':50,'c':100,'d':500,'m':1000}
	output = 0
	largest_den = 0
	i = -1
	while i >= -len(roman):
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