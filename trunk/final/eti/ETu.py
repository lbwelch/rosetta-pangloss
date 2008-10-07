# ETu.py
# current version: 0.02
#
#Purposes of application:
# 1. provide a command-line interface for ETtheInterlinear.py application
# 2. allow operation of ETtheInterlinear.py without complex command-line arguments
# 3. manipulate interlinear texts using functions that will be called for the Pangloss OpenOffice.org extension/macros
#
# usage: python ETu.py
#
#author: Jeremy Fahringer
#for Rosetta Project, Pangloss

import os, sys
import ETtheInterlinear as ETI

#please keep these global variables updated
version = "0.01"

#configuration defaults
input_config = "boktu-short.xml"
output_config = "sampleout.odt"
sample_config = ["sample.xml", ""]

def loadInfo():
	#get path for input + output files
	path = raw_input("Please enter the path to the folder where the input file is located, from the current directory location: ").strip()
	if (len(path)<=2):
		path = ""
	if (path.count("!Config")==0):
		input_name= raw_input("Input file name: ").strip()
		output_path = None
		if (len(input_name)<=2):
			input_name = input_config
		input_name = path+input_name
		
		output_name = raw_input("ODF output file name (ends with .odt): ").strip()
		if (len(output_name)<=2):
			output_name = output_config
		
		if (output_name.count('.odt')==0):
			output_name = output_name+".odt"
		
		elif (output_name.count('.odt')>1):
			output_name.strip('.odt')
			output_name = output_name +".odt"
			
		if raw_input("Would you like the output file(s) to be created in the same folder as the input file? ").count('n'):
			output_path = raw_input("New path to output folder: ").strip()
			output_name = output_path+output_name
		
		if (raw_input("Would you like to have a sample archival xml output, as well? ").count("y") > 0):
			sample_name = raw_input("XML sample filename: ")
			if (output_path != None):
				sample_name = output_path+sample_name
			else:
				sample_name = path+sample_name
			sample = [sample_name, "y"]
		else:
			sample = [None, ""]
			
	else: 
		input_name = input_config
		output_name = output_config
		sample = sample_config
		
	return [input_name, output_name, sample]
	

def inputArgs(myIGT = None):
	#get arguments for functions in ETtheInterlinear 
	print "\n", "*"*6
	print "'v' : verbose running"
	print "'q' : quiet running"
	print "'p' : pretty printing"
	print
	print "'b' : demo build tree from scratch"
	print "'t' : ODF tree building notices"
	print "'x' : use chunk of IGT rather than tables"
	print "'a' : make parallel archival.xml file inside odf"
	print 
	print "'d' : run demo"
	#print
	#print "'Q' : exit program immediately after running task"
	
	args = raw_input("Which options would you like to use? ").strip()
	args = "-"+args
	print "*"*6, "\n"
	
	if myIGT != None:
		myIGT.setArgs(args)
		return args, myIGT
		
	return args

def manipulations(myIGT, args):
	# demonstrates interlinear text manipulation features of ETtheInterlinear
	# myIGT (InterlinearText object)
	

	action = ""
	selectedNode = None
	selectedNodeName = ""
	while (action.count("E")==0):
		print 
		print "\n","-"*6
		print "Manipulation Menu:"
		print "\t -- manipulate InterlinearText object from file", "'"+myIGT.filename+"'."
		if selectedNode != None:
			if selectedNodeName != None:
				selectedNodeName = selectedNodeName.strip()
			print "\t -- selected node is %s - %s"  % (selectedNode, selectedNodeName)
		print
		print "\t 1. Print current interlinear text tree"
		print "\t 2. Clean up tree + remove extraneous whitespace"
		print
		print "\t 3. Find node by text"
		print "\t 4. Find node by location"
		print
		if selectedNode != None:
			print "\t 5. Print selected node content(s)"
			print
			
			print "\t 6. Add element to node", 
			if selectedNodeName!=None:
				if len(selectedNodeName.strip())>0:
					print "-", selectedNodeName,
			if selectedNode.tag.count('morph') == 0:
				print "\n\t 7. Add element at location in node", 
				if selectedNodeName!=None:
					if len(selectedNodeName.strip())>0:
						print "-", selectedNodeName,
			else: print "\n"
			print
			print "\t 8. Change node contents", 
			if selectedNodeName!=None:
				if len(selectedNodeName.strip())>0:
					print "-", selectedNodeName,
			print "\n"
			print "\t 9. Remove element from within selected node", 
			if selectedNodeName!=None:
				if len(selectedNodeName.strip())>0:
					print "-", selectedNodeName,
			print "\n"
		else:
			print "\t -- Please select a node to manipulate, using one of the 'find' functions (3, 4)"
			print
		print "\t R. Reset arguments"
		print "\t S. Save to archival xml"
		print "\t E. Exit manipulation mode"
		print "\t Q. Quit program"
		print
		
		action = raw_input("\t make a choice: ").strip()
		print 
		
		if action.count('1')==1 and action.count('0')==0:
			# Print current interlinear text tree
			myIGT.printRoot()
		
		elif action.count('2')==1 and action.count('0')==0:
			# Clean up tree + remove extraneous whitespace
			myIGT.cleanup()
			
		elif action.count('3')==1 and action.count('0')==0:
			# Find node by text
			findText = raw_input("Search for string: ").strip()
			if len(findText) >0:
				foundNodes = myIGT.findContent(findText)
			else: 
				print "Please try again. \n"
				
			
			if (raw_input("Continue manipulating one of the found elements? ").count('y')!=0):
				selector = -1
				lastNode = len(foundNodes)-1
				while (0>selector or selector>lastNode):
					try:	
						selector = int(raw_input("Please enter the index number of node to select (0-%d): " % (lastNode)))
						if 0>selector or selector>lastNode:
							raise ValueError
					except ValueError:
						print "Please enter an integer between 0 and %d." % (lastNode)
					
				selectedNode = foundNodes[selector]
				selectedNodeName = myIGT.getContent(selectedNode)
				
		elif action.count('4')==1 and action.count('0')==0:
			# Find node by location
			print "Find node at this location: "
			affirm = ""
			while (affirm.count('y') == 0):
				phholder = myIGT.findPhrases()
				lastNode = len(phholder)-1
				ph, wr, mo = '', '', ''
				
				while (ph=='' or 0>ph or ph>lastNode):
					ph =raw_input("\t Phrase number (0-%d):\t" % ( lastNode )).strip()
					if len(ph)>0:
						try: 
							 ph = int(ph)
							 if 0>ph or ph>lastNode:
								 raise ValueError
							
						except ValueError:
							print "Please enter an integer between 0 and %d." % (lastNode)
							continue
							
				wrholder = myIGT.findWords(phholder[ph])
				lastNode = len(wrholder)-1
				while (wr=='' or 0>wr or wr>lastNode):
					wr = raw_input("\t Word number (0-%d):\t" % (lastNode)).strip()
						
					if len(wr)>0:
						try:
							wr = int(wr)
							if 0>wr or wr>lastNode:
								 raise ValueError
						except ValueError:
							if type(wr) == str:
								if wr.count('-')!=0:
									wr = ''
									mo = ''
									break
							print "Please enter an integer between 0 and %d." % (lastNode)
							continue
				if (wr!=''):
					moholder = myIGT.findMorphs(wrholder[wr])
					lastNode = len(moholder)-1
				while (mo=='' or 0>mo or mo>lastNode) and (wr!=''):
					mo = raw_input("\t Morph number (0-%d):\t" % (lastNode)).strip()

					if len(mo)>0:
						try:
							mo = int(mo)
							if 0>mo or mo>lastNode:
								 raise ValueError
						except ValueError:
							if type(mo) == str:
								if mo.count('-')!=0:
									mo = ''
									break
							print "Please enter an integer between 0 and %d." % (lastNode)
							continue
						
				print "Search at location [phrase, word, morph]: [ %s, %s, %s]" % (ph, wr, mo)
				affirm = raw_input("Is this correct? ")
				if affirm.count('n')!=0:
					if (raw_input("Would you like to manually input the location? ").count('y')!=0):
						ph = raw_input("\t Phrase: ").strip()
						wr = raw_input("\t Word: ").strip()
						mo = raw_input("\t Morph: ").strip()
						print "['%s', '%s', '%s']" % (ph, wr, mo)
						affirm = raw_input("Is this correct? ")
						
			selectedNode = myIGT.getNode(ph, wr, mo)
			selectedNodeName = myIGT.getContent(selectedNode)
			print
			
			
		elif action.count('5')==1 and action.count('0')==0:
			# print node content(s)
			oldargs = None
			
			#override verbose running
			if myIGT.args.count('v')!=0:
				oldargs = myIGT.args
				newargs = oldargs.strip('v')
				myIGT = myIGT.setArgs(newargs)
				
			if selectedNode != None:
				print "-"*6, "\n"
				print "Printing contents of node %s :" % selectedNode
				
				depth = 5
				progress = False
				while progress == False:
					depth = raw_input("How many sublevels would you like to print (0-2)? ")
					if len(depth.strip())<1:
						depth = 3
						progress = True
					else:
						try:
							depth = int(depth)
							if depth<0 or depth>2:
								raise ValueError
							progress = True
						except ValueError:
							print "Please enter a number between 0-2."
				
				print

				myIGT.printNode(selectedNode, depth)
				print 
			
			#replace old arguments
			if oldargs != None:
				myIGT = myIGT.setArgs(oldargs)
				
			print
			
		elif (action.count('6')==1 or action.count('7')==1) and action.count('0')==0:
			# Add element to node

			if selectedNode != None:
				if selectedNode.tag.count('phrase')!=0:
					tags = ["item", "word"]
					holder = myIGT.findWords(selectedNode)
				if selectedNode.tag.count('word')!=0:
					tags = ["item", "morph"]
					holder = myIGT.findMorphs(selectedNode)
				if selectedNode.tag.count('morph')!=0:
					tags = ["text", "gloss", "morphType"]
					holder=None
					
				newtag = ''
				insertindex = None
				while tags.count(newtag) == 0:
					newtag = raw_input("What type of new element would you like to add from %s to this %s? " % (tags, selectedNode.tag)).strip()
					if len(newtag)==1 and newtag.count('E'):
						break
					if action.count('7')==1:
						progress = False
						if holder!=None and (newtag.count('word')==1 or newtag.count('morph')==1):
							while progress== False:
								try:
									insertindex = raw_input("Please enter the index position where you would like to insert the new node (0-%s): " % len(holder))
									insertindex = int(insertindex)
									if insertindex > len(holder):
										raise ValueError
									progress = True
								except ValueError:
									print "Please enter a number in the correct range."
						else:
							print "It is not possible to add this '%s' element at a specific location in the selected node. Please choose another." % newtag
							break
								
				if myIGT.args.count('v') != 0:
					print selectedNode.tag
				
				if newtag.count('item')!=0:
					print "\n\t -- Adding new item to %s -- " % selectedNode
				
					newtype = ''
					newcontent = ''
					while len(newtype)<1 or len(newcontent)<1:
						try:
							newtype = raw_input("Item type: ").strip()
							newcontent = raw_input("Item content: ").strip()
							if len(newtype)<1 or len(newcontent)<1: 
								raise ValueError
						except ValueError:
							print "Please make sure that you have entered text for both type and content."
					myIGT.setItem(selectedNode, newtype, newcontent)
					
					
				elif newtag.count('word')!=0:
					print "\n\t -- Adding new word to %s -- " % selectedNode
					
					newTxt= ''
					newGloss= ''
					progress = False
					while len(newTxt)<1 or len(newGloss)<1 or progress == False:
						try:
							wordtextaffirm = raw_input("Would you like to add text and gloss content to the top-level of this word? ").strip()
							if wordtextaffirm.count('n')!=0:
								newTxt = None
								newGloss = None
								progress = True
								break
							newTxt= raw_input("Text content: ").strip()
							newGloss= raw_input("Gloss content: ").strip()
							if len(newTxt)<1 or  len(newGloss)<1  : 
								raise ValueError
							progress = True
						except ValueError:
							print "Please make sure that you have entered text content for both 'text' and 'gloss' levels."
					myIGT.setWord(selectedNode, newTxt, newGloss, insertindex)
					
					
				elif newtag.count('morph')!=0 and newtag.count('morphType')==0:
					print "\n\t -- Adding new morph to %s -- " % selectedNode
					newTxt= ''
					newGloss= ''
					while len(newTxt)<1 or len(newGloss)<1:
						try:
							
							newTxt= raw_input("Text content: ").strip()
							newGloss= raw_input("Gloss content: ").strip()
							if len(newTxt)<1 or  len(newGloss)<1  : 
								raise ValueError
						except ValueError:
							print "Please make sure that you have entered text content for both 'text' and 'gloss' levels."
					
					myIGT.setMorph(selectedNode, newTxt, newGloss, insertindex)
					
				elif newtag.count('text')!=0:
					print "\n\t -- Adding new 'txt' item to %s -- " % selectedNode
					newcontent = ''
					while  len(newcontent)<1:
						try:
							newcontent = raw_input("Text content: ").strip()
							if len(newcontent)<1: 
								raise ValueError
						except ValueError:
							print "Error with", newcontent
							print "Please make sure that you have entered text content for the new 'text' element."
					myIGT.setText(selectedNode, newcontent)
					
					
				elif newtag.count('gloss')!=0:
					print "\n\t -- Adding new 'gloss' item to %s -- " % selectedNode
					newcontent = ''
					while len(newcontent)<1:
						try:
							newcontent = raw_input("Gloss content: ").strip()
							if len(newcontent)<1: 
								raise ValueError
						except ValueError:
							print "Please make sure that you have entered text content for the new 'gloss' element."
					myIGT.setText(selectedNode, newcontent)
					
				elif newtag.count('morphType')!=0:
					print "\n\t -- Adding new 'morphType' item to %s -- " % selectedNode
					print 'morphType'
					newcontent = ''
					while len(newcontent)<1:
						try:
							newcontent  = raw_input("Morph type: ").strip().upper()
							if len(newcontent)<1: 
								raise ValueError
						except ValueError:
							print "Please make sure that you have entered text for the morpheme type."
					myIGT.setMorphType(selectedNode, newcontent)
				
				print "\t --"
				
				

				
		elif action.count('8')==1 and action.count('0')==0:
			# Change node contents
			if selectedNode != None:
				print selectedNode.tag
			else: 
				print "Please select a node to manipulate. "
				break
				
			depth = None
			affirm= ''
			myIGT.printNode(selectedNode, depth)
			if selectedNode.tag.count('phrase')!=0:
				
				while affirm.count('y')==0:
					try:
						prenum = myIGT.getOther(selectedNode, 'number')
						number  = raw_input("Change number from %s to : " % prenum).strip() 
							
						if number.isdigit()!=True and len(number)>0: 
							raise ValueError						
					except ValueError:
						print "Please make sure that you have entered a number."
				
					gloss = raw_input("Change free translation from %s to : " % myIGT.getGloss(selectedNode).encode('utf-8')).strip()
					
					affirm = raw_input('Would you like to finalize these changes? ').strip()
					if affirm.count('y')!= 0:
						if len(number) > 0:
							myIGT.setNumber(selectedNode, number)
						if len(gloss)>0:
							myIGT = myIGT.setGloss(selectedNode, gloss)
					if affirm.count('E')!= 0 or affirm.count('n')!=0:
						break
			
			elif selectedNode.tag.count('word')!=0 or selectedNode.tag.count('morph')!=0:
				while affirm.count('y')==0:
					oldtext = myIGT.getText(selectedNode).encode('utf-8')
					oldgloss = myIGT.getGloss(selectedNode).encode('utf-8')
					text = raw_input("Change text from %s to : " % oldtext).strip()				
					gloss = raw_input("Change gloss from %s to : " % oldgloss).strip()
					
					
					if selectedNode.tag.count('morph')!=0:
						oldmorphtype = myIGT.getOther(selectedNode, 'morphType')
						morphType = raw_input("Change morphType from %s to : " % oldmorphtype).strip()
					
					else: morphType = ''
					

					print "Text: \t %s -> %s " % (oldtext, text)
					print "Gloss: \t %s -> %s " % (oldgloss, gloss)
					affirm = raw_input('Would you like to finalize these changes? ').strip()
					if affirm.count('y')!= 0:
						if len(text) > 0:
							myIGT.setText(selectedNode, text )
						if len(gloss)>0:
							myIGT = myIGT.setGloss(selectedNode, gloss)
						if len(morphType)>0:
							morphType = morphType.upper()
							myIGT = myIGT.setMorphType(selectedNode, morphType)
					if affirm.count('E')!= 0 or affirm.count('n')!=0:
						break
						
			elif selectedNode.tag.count('morph')!=0:
				while affirm.count('y')==0:
					oldtext = myIGT.getText(selectedNode).encode('utf-8')
					oldgloss = myIGT.getGloss(selectedNode).encode('utf-8')
					text = raw_input("Change text from %s to : " % oldtext).strip()				
					gloss = raw_input("Change gloss from %s to : " % oldgloss).strip()
					
					
					print "Text: \t %s -> %s " % (oldtext, text)
					print "Gloss: \t %s -> %s " % (oldgloss, gloss)
					affirm = raw_input('Would you like to finalize these changes? ').strip()
					if affirm.count('y')!= 0:
						if len(text) > 0:
							myIGT.setText(selectedNode, text )
						if len(gloss)>0:
							myIGT = myIGT.setGloss(gloss)
					if affirm.count('E')!= 0 or affirm.count('n')!=0:
						break
				
		elif action.count('9')==1 and action.count('0')==0:
			# Remove element within selectedNode	
			
			
			print "-"*4
			print "Remove element within selected node"
			print 
			
			myIGT.printNode(selectedNode, 0)
			parent = selectedNode
			
			if selectedNode != None:
				i = 0
				j = 0
				print "\n\n"
				print "Choose which subelement to delete: "
				for sub in selectedNode.getchildren():
					print "\t", str(i)+".", sub.tag
					i += 1
					
					for sub2 in sub.getchildren():
						print "\t\t", "a"+str(j)+".", sub2.tag
						j+=1
				
				if selectedNode.tag.count('phrase')!=0:
					choices = ['item', 'words', 'word']
				elif selectedNode.tag.count('word')!=0:
					choices = ['item', 'morphemes', 'morph']
				elif selectedNode.tag.count('morph')!=0:
					choices = ['item']
					
				delchoice = raw_input('\t Delete element: ').strip()
				if delchoice.count('a')==1:
					delchoice = delchoice.strip('a')
					i = j
					strict = None
				else:
					strict = True
					
				progress = False
				while progress == False:
					try: 
						delchoice = int(delchoice)
						if 0<=delchoice and delchoice<i:
							progress = True
						else: raise ValueError
					except ValueError:
						print "Please enter an integer from 0 to %d." % (i-1)
					
				if (raw_input("Are you absolutely certain that you would like to delete this element and all of its contents? ").strip().count('y')>0):
					myIGT.removeNode(parent, delchoice, strict)
				
				print
		
			
			else:
				print
				print "*"*8, "Please select a node to manipulate. ", "*"*8
				break
			print "-"*4
			
		#elif action.count('H')==1:
		#	print ">> Coming soon << "
			
		elif action.count('R')==1:
			# Reset arguments
			args, myIGT = inputArgs(myIGT)
		elif action.count('S')==1:
			# Save current InterlinearText object to archival xml 
			print "\n\t Now saving interlinear text to archival xml file..."
			print "\t This will not overwrite your original xml input file"
			print
			if myIGT!=None and config[2][0] != None:
				#print config[2][0]
				myIGT.write(config[2][0])
				print "Successfully saved interlinear text to %s." % config[2][0]
				
			elif config[2][0] == None:
				progress = False
				while progress == False:
					arch_output = raw_input("Please enter name of the archival xml file (to create or overwrite: ").strip()
					if len(arch_output)>1 and arch_output.count('.xml')!=0:
						config[2] = [arch_output, 'y']
						myIGT.write(config[2][0])
						progress = True
			print 
						
				
		elif action.count('E')==1:
			# Exit manipulation mode
			print "*"*6
			return myIGT, args
		elif action.count('Q')==1:
			# Quit program
			print "-"*12
			print "Thank you for using ETu, the ETtheInterlinear interface."
			print "Now exiting..."
			print "\n\n", "-"*34, "\n"
			sys.exit(0)
			
		else: 
			print "Your choice '%s' was not one of the available menu options. Please try again." % action
		
	
	return myIGT, args
	
	
def demo(input_file, output_file, args = None):
	#arguments:
	#input_file (name for input IGT file)
	#output_file (name for output ODF file)
	#args (arguments passed from command-line, or others)
	#
	#demonstrates some of the basic capabilities of the program
	
#testing the building capabilities of the program
#	
	myTree = ETI.makeIGT(input_file, sample_config[0], args)
	
	if args.count('v') !=0:
		myTree.findPhrases()
		myTree.findWords()
		myTree.findMorphs()
	
	
#testing the find and search capabilities of the program
#
	if  args.count('f') != 0 and args.count('d') != 0:
		# run this test portion of the program if 'f' for 'find' is passed with the intial arguments
		print 
		print "-"*10
		print "Trying to find things in those trees:"
		print "-"*10
		print
	
		myTree.findMetadata()
		phrases=myTree.findPhrases()
		for s in phrases:
			words=myTree.findWords(s)
			for j in words:
				morphs = myTree.findMorphs(j)
				for k in morphs:
					txt = myTree.getText(k)
					gls =myTree.getGloss(k)
					
		#find input text
		findText = raw_input("What would you like to search for? ").strip()
		if (len(findText)<2):
			findText = 'people'
			
		myTree.findContent(findText)
	
		print "End find demo"
		print "-"*10
		print
		
	print	
	print"-"*10, args, "-"*10
	print
	myODF = ETI.makeODF(myTree, output_file, args)
	
	if args.count('Q')!=0:
		
		if args.count('q')==0:
			print "Now exiting the demonstration of ETtheInterlinear"
			print "-"*20	
		print
		
		sys.exit(0)
	
	
	return myTree, myODF


#main interface
if __name__ == '__main__':
	#show program header information
	print "\n\n", "-"*34, "\n"
	print "ETu, the user interface for ETtheInterlinear"
	print "version", version,"\n\n"
	print "Developed by the Rosetta Project, for the Pangloss feasibility study"
	print "Author: Jeremy Fahringer"
	print "\n", "-"*12, "\n"
	
	config = loadInfo()
	args = inputArgs()
	
	myIGT = None
	myODF = None
	
	choice =""
	history =[]
	
	while (choice.count("Q")==0):
		print "*"*12, "\n"
		if myIGT != None:
			print "You have an InterlinearText object open: ", myIGT.filename 
		if myODF != None:
			print "You have an OdfMaker object open."
		print "Running with the following arguments: ", args
		print "Configuration: \t  %s (input) \t %s (output) \t %s (archival xml) \n\n" % (config[0], config[1], config[2][0])
		
		print "Menu: \n"
		print "\t 1. Set new input and output files"
		print "\t 2. Run demonstration of input and output to ODF"
		print "\t 3. Open new InterlinearText object from input ... "
		print "\t 4. Manipulate the open InterlinearText object"
		print "\t 5. Output current InterlinearText object to ODF"
		print "\t 6. Output current InterlinearText object to archival xml only"
		print "\n\t H. Help manual (not yet working)"
		print "\n\t R. Reset runtime arguments"
		print "\t Q. Quit program"
		print
		
		choice = raw_input("\t make a choice: ").strip()
		print
		if (len(choice)>0):
			choice = str(choice[0])
		
	
		if choice.count('1')==1:
			# Set new input and output files
			config = loadInfo()
		
		elif choice.count('2')==1:
			# Run demonstration of input and output to ODF
			myIGT, myODF = demo(config[0], config[1], args)
		elif choice.count('3')==1:
			# Open new InterlinearText object from input ...
			myIGT = ETI.makeIGT(config[0], config[2][0], args)
		elif choice.count('4')==1:
			# Manipulate the open InterlinearText object
			if myIGT!=None:
				myIGT, args = manipulations(myIGT, args)
			else:
				print "No InterlinearText object was found. Please create an InterlinearText object."
		
		elif choice.count('5')==1:
			# Output current InterlinearText object to ODF
			if myIGT!=None:
				myODF = ETI.makeODF(myIGT, config[1], args)
			else:
				print "No InterlinearText object was found. Please create an InterlinearText object."
		elif choice.count('6')==1:
			# Output current InterlinearText object to archival xml only
			if myIGT!=None:
				myIGT.write(config[2][0])
			else:
				print "No InterlinearText object was found. Please create an InterlinearText object."
		
		elif choice.count('H')==1:
			# Help manual
			print "Coming soon...\n"
			
		elif choice.count('R')==1:
			# Reset arguments
			if myIGT != None:
				args, myIGT = inputArgs(myIGT)
			else:
				args = inputArgs()
			
		else: 
			if choice.count('Q')==0 and (len(choice)>0):
				print "Your choice '%s' was not one of the available menu options. Please try again."  % choice
		
		history.append(choice)
	
		
	print "-"*12
	print "History of choices: ", history, "\n"
	print "Thank you for using ETu, the ETtheInterlinear interface."
	print "Now exiting..."
	print "\n\n", "-"*34, "\n"
	
	sys.exit(0)
	
