def read_fasta(file_path: str) -> dict:
	"""
	Description:
	This function reads a fasta file
	and returns a list of features included in the fasta file.
	:param file_path: str # path to fasta file
	:return:  protein_dict:dict # dictionary of protein features. Such as 'sequence', 'sites'
	"""
	protein_dict = dict()
	with open(file_path, 'r') as f:
		for line in f:
			if line.startswith('>'):
				name = line.strip()
				first_feature = next(f).strip()
				features = []
				while not first_feature.startswith('>'):
					features.append(first_feature.strip())
					first_feature = next(f).strip()
				protein_dict[name] = features
	return protein_dict


def train_or_eval(features_num: int, 
                  eval_per: float, 
                  input_file: str, 
                  train_path: str, 
                  eval_path: str
                  ) -> None:
	"""
	Description:
	divide the total protein_datas into train and eval sets
	:param features_num:int # number of features in train set, except protein_name, including sequence, sites
	:param eval_per:float # proportion of protein to train set, for example, 0.1
	:param input_file:str # path to the total file
	:param train_path:str # path to save train set
	:param eval_path:str # path to save eval set
	:return:None
	"""
	import random
	
	def integrate_lines(start):
		temp_num: int = features_num
		temp_line: str = ''
		while temp_num > 0:
			temp_line += lines[start]
			temp_num -= 1
		return temp_line
		
	with open(input_file, 'r') as writer:
		lines = writer.readlines()
		length = len(lines) // (features_num+1)
		numbers = [(features_num+1)*x for x in range(length)]
		eval_length = int(len(numbers) * eval_per)
		selected = random.sample(numbers, eval_length)
		with open(eval_path, 'w') as writer_eval:
			for line_index in selected:
				line_index = line_index
				line = integrate_lines(line_index)
				writer_eval.write(line)
		with open(train_path, 'w') as writer_train:
			for line_index in numbers:
				if line_index in selected:
					continue
				else:
					line_index = line_index
					line = integrate_lines(line_index)
					writer_train.write(line)
			
			
def slice_fragment(
		input_file, 
		output_dir, 
		focus=None, 
		file_type: str = 'txt',
		csv_split: str = '\t'
) -> None:
	"""
	Description:
	A method orignated from ELECTRA thesis.
	slice length==25 fragemnt of protein sequence.
	the postive fragment is the central residue is bind site and focus
	:param input_file:
	:param output_dir:str # a catalogue path
	:param focus:list # list of focus residues. if None, focus=["C", "D", "E", "G", "H", "K", "N", "R", "S"]
	:return:None. Will create files named positive and nagative fragments.
	"""
	if focus is None:
		focus = ["C", "D", "E", "G", "H", "K", "N", "R", "S"]
	positive_fragment = ''
	negative_fragment = ''
	with open(input_file, 'r') as input_file:
		for line in input_file:
			if line.startswith('>'):
				if file_type == 'txt':
					name = line.strip().split("\t")[0]
					seq = next(input_file).strip()
					site = next(input_file).strip()
					
				elif file_type == 'csv':
					name, seq, site = line.strip().split(csv_split)
				for position in range(len(seq)):
					if seq[position] in focus:
						if max(0, position - 12) >= 0 and max(len(seq), position + 13) <= len(seq):
							if '1' not in site[position - 12:position] and '1' not in site[position + 1:position + 13]:
								label = site[position - 12:position + 13]
								fragment_line = seq[position - 12:position + 13]
								if len(fragment_line) == 25:
									if site[position] != "0":
										positive_fragment += name + "\n" + fragment_line + "\n" + label + "\n"
									else:
										negative_fragment += name + "\n" + fragment_line + "\n" + label + '\n'
	with open(f'{output_dir}/positive_fragment', 'w') as positive_file:
		positive_file.write(positive_fragment)
	with open(f'{output_dir}/negative_fragment', 'w') as negative_file:
		negative_file.write(negative_fragment)
		

if __name__ == '__main__':
	operation = 'train'
	if operation == 'read':
		read_fasta('negative_fragment')
	if operation == 'train':
		train_or_eval(features_num=2, eval_per=0.1, input_file='./negative_fragment', train_path='./train.txt', eval_path='./test.txt')
	