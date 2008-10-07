# ETtheInterlinear.py
#current version: 0.14
#
#Purposes of application: 
#1. testing xml.etree.ElementTree module
#2. parse interlinear glossed text (IGT) file into ElementTree
#3. output ODF file containing IGT in content.xml file
#
# usage: python ETtheInterlinear.py input_xml_file output_ODF_file arguments
#
#author: Jeremy Fahringer
#for Rosetta Project, Pangloss 
#
import os, sys
import xml.dom
import xml
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET
import zipfile
import zlib

#set header for output xml file here"
xml_header ="<?xml version='1.0' encoding='utf-8'?> \n"
xsl_header ="<?xml-stylesheet type='text/xsl' href='"
xsl_file="IGTv2.4.xsl"
xsl_header_final="'?> \n"

#add new IGT types here
#example: ['name_of_IGT_type', 'root', 'first child']
igtDictionary = [['ITE', 'TEXT', 'S'], ['Hughes et al. (2003)', 'resource', 'interlinear_text'], ['EOPAS', 'eopas', 'header', 'olac']]
morphtypedict = dict({'CLITIC':'=', 'PROCLITIC':'=', 'ENCLITIC':'=', 'REDUP':'~'})



class InterlinearText:
	def __init__ (self, filename=None, args = None):
		#arguments:
		#self (object to be initialized)
		#filename (interlinear text xml file)
		#args (passed arguments)
		
		#initialize InterlinearText object
		if (filename != None) and (args == None):
			if filename.startswith("-"):
				args = filename
				filename = None
			else: args = ''
				
		if (args != None):
			if args.count('v') != 0:
				print "Setting args to %s on init." % args
			self.args = args
		
		elif (args == None) or args == '':
			self.args = ''

		if (filename != None):
			if args.count('v') != 0:
				print "Filling tree on init."
			self.e_tree=ET.ElementTree(ET.Element('IGT'), filename)
			if self.checkType().count('Hughes') == 0:
				self.e_tree = ET.ElementTree()
				print "*"*20
				print "InterlinearText file that was passed was not of the Hughes et al. (2003) model."
				print "Please use the fillTree() function to create the InterlinearText object with your file."
				print "*"*20
				sys.exit(0)
			else:	
				print "Initialized InterlinearText object from input file '%s'." % filename
				if args.count('v')!=0:
					print self.e_tree.getroot().tag
			self.filename = filename
		
		self.archival = None # initialize archival container within InterlinearText object to None
		
		return None

	def close(self):
		#closes InterlinearText object, prepares for garbage collection
		if self.e_tree:
			self.e_tree.clear()
		if self.args:
			self.args = None
		if self.filename:
			self.filename = None
		if self.archival:
			self.archival.clear()
		
		self = None
		return
		
		
	def setArgs(self, args):
		#Set arguments for operating mode
		#v: verbose
		#p: pretty print
		#q: quiet
		#b: build on-the-fly interlinear text model to play with
		#o: OVERRIDE pretty printing
		#f: find stuff
		
		self.args = args	
		if args.count('v') != 0:
			print "Running in mode: " 
			if args.count('v') != 0: 
				print "verbose"
			if args.count('p') != 0 and args.count('o') ==0: 
				print "pretty printing"
			if args.count('o') != 0:
				print "OVERRIDE pretty printing"
			if args.count('b') != 0: 
				print "build on-the-fly"	
			if args.count('d') != 0:
				print "DEMONSTRATION MODE"
			if args.endswith('f'): 
				print "find" 
			print
		return self
		
	def fillTree(self, filename, args = None):
		#"Fill e_tree with ElementTree parsed from the xml file 'filename', filename node contains original string filename"
		newfile = open(filename, 'r')
		self.e_tree=ET.ElementTree(ET.Element('IGT'), newfile)
		self.filename = filename
		namelist = filename.split("/")
		self.shortname= namelist[len(namelist)-1]
		
		if args != None:
			self.setArgs(args)
		
		if self.args.count('q')==0:	
			print "Initialized ElementTree object from file %s." % filename
		self = self.convert()
		newfile.close()
		return self
		
		
	def cleanup(self):
		#cleans up InterlinearText object elementTree, removing whitespace between elements and surrounding text content of elements
		# self (InterlinearText object)
		
		iterator = self.e_tree.getiterator()
		
		for el in iterator:
			el.tail = None
			if el.text != None:
				el.text = el.text.strip()
				if len(el.text)==0:
					el.text = None
				
		return self
			
			
	def checkType(self):
		#arguments:
		#self (InterlinearText object)
		#checks the first few elements of the InterlinearText elementTree against IGT models
		
		treeroot = self.e_tree.getroot()
		treebranches = treeroot.getiterator()
		
		if self.args.count('v') != 0:
			print "-"*10
			print "Now checking what type of IGT elementtree was created:"
		i = 1
		kind = []
		for branch in treebranches:
			for igt in igtDictionary:
				if len(igt)>i and branch.tag.endswith(igt[i]):
					kind.append(igt[0])
				#	print igt[0]
				#	print branch.tag
#			if self.args.count('v') != 0:
			#	print branch.tag
	
			i += 1
		
		if kind.count(kind[0]) != len(kind) or len(kind)==0:
			print "This IGT hasn't been matched against a known interlinear text model... proceed with caution"
		else: 
			if self.args.count('v') != 0:
				print "The input interlinear text is constructed like the %s model." % kind[0]
			return kind[0]
			
		if len(kind) == 0:
			print
			print "The input file is in a format that is not currently supported. Sorry."
			print
		return "Unsupported format"
	
	
	def convert(self, kind = None):
		#arguments:
		#self (InterlinearText object)
		#kind (IGT model type)
		
		if kind == None:
			kind = self.checkType()
			
		if kind!= None and self.args.count('a') != 0:			
			print "Adding initial input from xml to self.archival"
			self.archival = self.e_tree
		
		if kind.count('ITE') !=0:
			if self.args.count('v') != 0:
				print "Converting InterlinearText elementTree to conform to standard model from %s model." % kind
		
			newTree = InterlinearText()
			newTree.setArgs( self.args)
			newTree, i_text = newTree.buildTree('convert')
			newTree, phrases = newTree.setPhrases(i_text)
			
			num = 1
			for s in self.e_tree.getiterator('S'):
				if len(s.getiterator()) < 2:
					break
				newTree, words = newTree.setPhrase(phrases, num, self.getContent(s.find('FORM')), self.getContent(s.find('TRANSL')) )
				num += 1
				for w in s.getiterator('W'):
					newTree, morphemes = newTree.setWord(words, self.getContent(w.find('FORM')), self.getContent(w.find('TRANSL')) )
				#	print self.getContent(w.find('FORM'))
				#	print self.getContent(w.find('TRANSL'))
					for m in w.getiterator('M'):
						newTree, morph = newTree.setMorph(morphemes, self.getContent(m.find('FORM')), self.getContent(m.find('TRANSL')) )
				#		print self.getContent(m.find('FORM'))
				#		print self.getContent(m.find('TRANSL'))
			
			
			newTree.filename = "InterlinearText converted from ITE model"
			self = newTree
			return newTree
			
		elif kind.count('EOPAS') !=0:
			if self.args.count('v') != 0:
				print "Converting InterlinearText elementTree to conform to standard model from %s model." % kind
		
			newTree = InterlinearText()
			newTree.setArgs( self.args)
			newTree, i_text = newTree.buildTree('convert')
			children = self.e_tree.getroot().getchildren()
			self.setArgs(self.args+"o")
			self.printRoot("")
			
			
			
			if children != None:
				tags = []
				contents = []
				for grandchild in children[0].getchildren()[0].getchildren():
					if grandchild.text != None and grandchild.tag != None:
						tag = grandchild.tag.split('}')
						tag = tag[len(tag)-1]
						tags.append(tag)
						contents.append(grandchild.text)
						
				newTree.setMetadata(i_text, tags, contents)
				
		#fix this after figuring out how to get around ''ValueError: too many values to unpack'' from parseString		
		#		newTree.e_tree.getroot().insert(0, children[0])
		
			
			print newTree.printRoot()	
			newTree, phrases = newTree.setPhrases(i_text)
			
			num = 1
			for s in children[1].getchildren()[0].getchildren():
			#	if len(s.getiterator()) < 2:
			#		break
				
				iD = s.attrib.get('id')
				sT = s.attrib.get('startTime')
				eT = s.attrib.get('endTime')
				text = None
				gloss = None
				for j in s.getchildren():
					tag = j.tag.split('}')
					tag = tag[len(tag)-1]
					if tag.count('words')==0:
						for key in j.attrib.keys():
							attribs = j.attrib.get(key)
							if attribs.count('trans')!=0:	
								text = j.text
							elif attribs.count('ortho')!=0:
								gloss = j.text
				newTree, words = newTree.setPhrase(phrases, num, text, gloss )
				
				phrasehead = newTree.e_tree.getiterator('phrase')[num-1]
				phrasehead.set('id', s.attrib.get('id'))
				phrasehead.set('startTime', s.attrib.get('startTime'))
				phrasehead.set('endTime', s.attrib.get('endTime'))
				print phrasehead.items()
				num += 1
				
				
				if tag.count('words')==0:
					h = s.getiterator()
					j = h[len(h)-1]
				
				for word in j.getchildren():
					
					text = None
					gloss = None
					for w in word.getchildren():
						tag = w.tag.split('}')
						tag = tag[len(tag)-1]
						if tag.count('text')!=0:
							for key in w.attrib.keys():
								attribs = w.attrib.get(key)
								if attribs.count('trans')!=0:	
									text = w.text
								elif attribs.count('ortho')!=0:
									gloss =w.text
					
									
									
					newTree, morphemes = newTree.setWord(words, text, gloss)
					if tag.count('morphemes')==0:
						h = word.getiterator()
						w = h[len(h)-1]
					morphnum = 0
					cliticposition = None
					nexttype = None
					for morph in w.getchildren():
						text = None
						gloss = None
						mtype = None
						morphnum +=1
						
						for n in morph.getchildren():
							tag = n.tag.split('}')
							tag = tag[len(tag)-1]
							if tag.count('text')!=0:
								for key in n.attrib.keys():
									attribs = n.attrib.get(key)
									print attribs
									if attribs.count('morpheme')!=0:
										mtype, cliticposition = self.getMorphType(n, n.text, morphnum)
										if mtype != None:
											print "*"*6, morphtypedict.get(mtype)
											text = n.text.split(morphtypedict.get(mtype))
									
											if len(text[0])==0:
												text = text[len(text)-1]
											else: text = text[0]
										elif mtype == None:
											text = n.text.split('-')
											text = text[len(text)-1]
											
										
										else: text = n.text
										print "text:", text
									elif attribs.count('gloss')!=0:
										mtype, cliticposition = self.getMorphType(n, n.text, morphnum)
										if mtype != None:
											print "^"*6, morphtypedict.get(mtype)
											gloss= n.text.split(morphtypedict.get(mtype))
											
											if len(text[0])==0:
												gloss =gloss[len(gloss)-1]
											else: gloss = gloss[0]
										elif mtype == None:
											gloss = n.text.split('-')
											gloss = gloss[len(gloss)-1]
										else: gloss = n.text
										print "gloss:", gloss
										
						
									
										
						newTree, morph = newTree.setMorph(morphemes, text, gloss )
						if cliticposition == None and mtype!=None:
							newTree.setMorphType(morph, mtype)
						elif cliticposition!=None and mtype!=None:
							print "^"*4
							print "clitic position is", cliticposition
							print "nexttype is now", mtype
							nexttype = mtype 
							cliticposition = None
							print "reset cliticposition to", cliticposition
							print "^"*4
						elif cliticposition == None and nexttype!=None:
							newTree.setMorphType(morph, nexttype)
							print "setMorphType with", nexttype+"."
							nexttype = None
						
			newTree.filename = "InterlinearText converted from EOPAS model"
			self = newTree
			return newTree
		elif kind.count('Unsupported') !=0 and self.args.count('o') == 0:
			exit("This interlinear text document is in an unsupported format. The program will quit. To run program again and override this check, include 'o' in the run-time arguments.")
			
		else: return self
		
		
		
		
	def printRoot(self, pr = None):
		#"Print ElementTree structure and contents."
		print "Now printing the elementTree for InterlinearText object filled from '%s'." % self.filename
		return printRoot(self.e_tree, pr, self.args, self.filename)

	
	
					
	def printNode(self, node, printdepth = None):
		# "Print contents of node, including children nodes if printdepth is included"
		# self (InterlinearText object)
		# node (elementTree element within InterlinearText tree)
		# printdepth (integer, how many layers deep should be printed)
		
		if printdepth != None and type(printdepth)==str:
			printdepth = int(printdepth)
			
		if printdepth < 0 and printdepth != None:
			return
			
		elif printdepth == None:
			dashes = "-"*5
		else:
			dashes = "-"*(6-printdepth)
		
		print
		
		#if node is either word or morph, print dashes before it
	#	if node.tag.count('s')==1 or node.tag.count('phrase')==0:
	#		print dashes*2
	#		print
			
		print "\t Node tag: ", node.tag
		con = self.getContent(node)
		if con != None:
			if len(con.strip())>0:
				print "\t Node text: ", con.strip(),
			if node.attrib:
				print "in",  "'"+node.attrib.values()[0]+"'", "element."
					
		subs = node.getchildren()
		
		if (subs != None and (len(subs)>0)) and (printdepth >= 0 and printdepth  != None) :
			ren = ''
			if len(subs)>1:
				ren = 'ren'
			
			print "%s \t This '%s' node has %d %s." % (dashes, node.tag, len(subs), 'child'+ren)
			if node.tag.count('words')!=0 or node.tag.count('morphemes'):
				if printdepth != None:
					printdepth = printdepth -1
							
			for sub in subs:
				self.printNode(sub, printdepth)
				
				
			return	
				

		return None
	
		
	def write(self, output_file, pr = None):
		#"write ElementTree to output_file, after deleting output_file first. Oops."
		#!!! need to fix overwriting. Checking for file failed.
		output = open(output_file, 'a+')
		output.truncate(0)
		
		#writes xml headers to output file from xml_header global variable
		if xsl_file:
			if self.args.count('v') !=0:
				print "Including XSL file: %s" % xsl_file
			output.write(xml_header+xsl_header+xsl_file+xsl_header_final)	
		else: output.write(xml_header)
		
		if pr == "pretty":
			output.write(self.printRoot('pretty')[23:])	#writes pretty-printed xml to open output file, excluding redundant xml declaration
		else: self.e_tree.write(output)
			
		if self.args.count('v') != 0:
			print
			print "Now writing '%s' elementTree to %s."  % (self.filename, output_file)
		output.close()
			
	
#
#	find functions (various)
#
#This next section/module is useful for iterating through the IGT structure, returning useful sections and text.
#In other words, it can find content to export into ODF structured tables, etc.
#

	def findMetadata(self, pr=None):
		#find metadata items within top-level of interlinear_text node, title, comments, etc.
		#prints text content of metadata items.
		#returns iterator containing metadata items
		lookerR = []
		lookerR = self.e_tree.getiterator('resource')
		if len(lookerR) !=0:
			lookerI =[]
			lookerI = lookerR[0].getiterator('interlinear_text')
			if len(lookerI) != 0:
				looker =lookerI[0].findall("item")
				if pr == 'print':
					print "Looking for the top-level metadata. There are %d metadata items in '%s'." % (len(looker), self.filename)
					for s in looker:
						print s.attrib.values()[0], ":", s.text
				return looker
		
		return None
			
		
	def findPhrases(self, pr=None):
		#find phrase nodes within interlinear text ElementTree
		#if "print" is passed for the argument, then function will print the content of all top-level item nodes.
		#prints text content within top-level item node of the phrase (ie. phrase-level free translation)
		#returns iterator containing the phrase nodes
		looker = self.e_tree.getiterator('phrase')
		
		if self.args.count('v') != 0:
			print "Looking for the contents of each phrase. There are %d phrases in '%s'." % ( len(looker), self.filename)
		
		#if 'print' is passed for argument pr, 
		#prints out all text content at the top level of each phrase node
		if pr == "print":
			i = 0
			for s in looker:
				i+=1
				print "In phrase", i
				looker2 = s.findall('item')
				for j in looker2:
					print j.text.encode('utf-8')
					print
					
		return looker
		
	def findWords(self, parent=None, pr=None):
		#find word nodes within passed 'parent' element. If '' is passed, then find word nodes within interlinear text ElementTree
		#if "print" is passed for the 2nd argument, then function will print the content of all top-level item nodes.
		#prints text content  within top-level item nodes of the phrase (ie. word-level text and gloss)
		#returns iterator containing word nodes
		if parent ==None or parent == "":
			looker = self.e_tree.getiterator('word')
			placename = self.filename
		
		else: 
			looker = parent.getiterator('word')
			placename ="this " + parent.tag
		
		if self.args.count('v') != 0:
			print "Looking for the contents of each word. There are %d words in %s." % ( len(looker), placename)
		
		#if 'print' is passed for argument pr,
		#prints out all text content at the top level of each word node
		if pr == "print":
			i = 0	
			for s in looker:
				i+=1
				print "In word", i
				looker2 = s.findall('item')
				for j in looker2:
					print j.text.encode('utf-8')
				print
		
		return looker
		
	
	def findMorphs(self, parent=None, pr=None):
		#find morph nodes within passed 'words' iterator. If '' is passed, then find morph nodes within interlinear text ElementTree
		#if "print" is passed for the 2nd argument, then function will print the content of all top-level item nodes.
		#prints text content of item nodes within morph nodes.
		#returns iterator containing morph nodes
		if parent ==None or parent == "":
			looker = self.e_tree.getiterator('morph')
			placename = self.filename
		else: 
			looker = parent.getiterator('morph')
			placename = "this " + parent.tag
		
		if self.args.count('v') != 0:
			print "Looking for the contents of each morph. There are %d morphs in %s." % (len(looker), placename)
		
		#if 'print' is passed for argument pr,
		#prints out all text content at the top level of each morph node
		if pr == "print":
			i = 0
			for s in looker:
				i+=1
				print "In morph", i
				looker2 = s.findall('item')
				for j in looker2:
					print j.text.encode('utf-8')
				print
		
		return looker
	
	
	def findContent(self, content_to_find):
		#find specific content 'content_to_find' within interlinear text ElementTree
		#prints where content was found
		#returns iterator containing all item nodes in ElementTree
		looker = self.e_tree.getiterator('item')
		if self.args.count('v') != 0:
			print "Looking for '%s' in '%s'." % (content_to_find, self.filename)
		i = 0
		found = []
		for s in looker:
			i +=1
			if s.text.encode('utf-8').count(content_to_find) != 0:
				print "'%s' found in the %s item of %s %d." % (content_to_find, s.attrib.values()[0], s.tag, i )
				found.append(s)
		
		return found
		
	def getNode(self, phraseIndex=None, wordIndex = None, morphIndex = None, parentNode = None):
		#find a node by its numerical position (optionally within 'parentNode' element, if passed)
		# self (InterlinearText object)
		# phraseIndex (numerical index of phrase node)
		# wordIndex (numerical index of word node)
		# morphIndex (numerical index of morph node)
		# parentNode (node location to look inside)
		
		if parentNode == None:
			parentNode = self.e_tree.getiterator("interlinear_text")[0]
		
		if phraseIndex != None and wordIndex == None and morphIndex != None and parentNode == None:
			print "It is impossible to find a morph at position %s, as the word position is missing." % (str(morphIndex))
			print "Only selected phrase will be returned."
			morphIndex = None
			
		numlist = [phraseIndex, wordIndex, morphIndex]
		for pos in numlist:
			parentNode = self.getbyLoc(parentNode, pos)
			if parentNode == None:
				return None
		
		if (self.args.count('v')!=0):
			print "Node found at position contains: "
			bigtypes = ['words', 'morphemes']
			for sub in parentNode.getchildren():
				if bigtypes.count(sub.tag)==0:
					print sub.tag
				elif sub == None or sub.tag == None:
					print "This subelement is empty."
				else:
					self.getContent(sub)
			
			
		return parentNode
		
		
	def getbyLoc(self, node, index, strict=None):
		# gets element at index position within passed node
		# self (InterlinearText object)
		# node (an element)
		# index (index of subelement to return)
		# strict (optional strictness value (anything other than None))
		# 	if a strict value is passed, skips first step of looking into container elements (ie. phrases, words, morphemes)
		
		if index == None:
			return node
		
				
		else:
			if type(index) is str:
				if (len(index.strip())<1):
					return node
				index = int(index)
			try: 
				#finds last element of node (ie. phrases within interlinear_text)
					
				if strict == None:
					node = node.__getitem__(node.__len__()-1)
				
				#finds subelement at index 'index'
				newnode = node.__getitem__(index)
				return newnode
			except IndexError:
				#if subelement does not exist at that location, returns None
				print "The '%s' node does not have an element index %s." % (node.tag, index)
				return None
			
		

	def getContent(self, node, tag=None):
		#takes a node and optional atrribute tag. If optional atrribute tag is included, will return content only of that type
		#returns text string
		if node == None:
			return None
			
		if  tag != None:
			if node.attrib != None:
				# print node.attrib
				if (node.attrib.values()[0]==tag):
					if self.args.count('v')!=0:
						print "getContent:", node.attrib.values(), node.text.encode('utf-8')
					return node.text.encode('utf-8')
				else:
					return None
		elif tag == None and node.text == None:
			if self.args.count('v')!=0:
				print "This %s node does not have any text content." % node
			return None
			
		else:
			if self.args.count('v')!=0:
				if node.attrib != None:
					print "getContent:", node.attrib.values(), node.text.encode('utf-8')
				
				elif node.text != None: print "getContent: ", node.text.encode('utf-8')
			return node.text.encode('utf-8')
		
		return None

			
	def getText(self, node):
		#uses the getContent function to find 'txt' item in top-level of node
		#returns txt string
		txt = None
	
		for i in node.findall("item"):
			txt = self.getContent(i, "txt")
			if txt != None:
				if self.args.count('v')!=0:
					print "Text item:", txt
				return txt.decode('utf-8')
		return None
	
	def getGloss(self, node):
		#uses the getContent function to find 'gls' item in top-level of node
		#returns gls string
		gls = None
		for i in node.findall("item"):
			gls = self.getContent(i, "gls")
			if gls != None:
				if self.args.count('v')!=0:
					print "Gloss item:", gls
				return gls.decode('utf-8')
		return None
				
	def getOther(self, node, attrib):
		#uses the getContent function to find an item of passed attrib type in top-level of node
		#returns other string
		other = None
		
		for i in node.findall("item"):
			other= self.getContent(i, attrib)
			if other != None:
				if self.args.count('v')!=0:
					print attrib, "item:", other
				return other.decode('utf-8')
		return None

	def getMorphSep(self, morph_node, morphType=None):
		#returns appropriate morpheme separator as string, if node contains morphType item
		#self (InterlinearText object)
		#node (a morph level element)
		#morphType (optional: text string containing morphType to find separator for)
		default = '-'
		
		if morphType != None:
			sep = morphType
			
		else:
			for i in morph_node.findall("item"):
				sep = self.getContent(i, "morphType")
			
		if sep != None:
			if self.args.count('v')!=0:
				print "MorphType:", sep
			
			for mtype, s in morphtypedict.items():
				if sep.count(mtype) != 0:
					return s

					
		return default
		
	def getMorphType(self, node, node_text, morphnum = None):
		#returns appropriate morphType by searching node_text for separator and position
		#self (InterlinearText object)
		#node (a morph level element)
		#node_text (a string of text containing a morpheme separator)
		#morph_num (an integer representing the position of the morpheme within its parent word
		
		
		morphType = None
		print morphnum
		for mtype, s in morphtypedict.items():
			if s.count('=')!=0:
				if node_text.endswith(s) and morphnum == 1:
					print node_text, "might be a PROCLITIC morph."
					return 'PROCLITIC', None
				elif node_text.endswith(s) and morphnum != 1:
					print 'The next node might be a CLITIC morph but this is not certain.'
					return 'CLITIC', 'next'
				elif node_text.startswith(s):
					print node_text, "might be a CLITIC morph."
					return 'CLITIC', None

					

			if node_text.count(s)!=0:
				print node_text, "might be a", mtype, "type morph."
				morphType = mtype
				
			elif node_text.count('-')!=0:
				return None, None
		return morphType, None
		
		
	def getMorphParts(self, morphList):
		#takes list of morph nodes, returns a tuple of lists of text morphs, gloss morphs, and separators
		#first empty index in separators[] is empty unless filled with by a '=' for a proclitic
		#if not empty, separators[0] is appended rather than prepended to final string output (by other functions)
		#self (InterlinearText object)
		#morphList (list of morph nodes from word node within InterlinearText object)
		
		txts =[]
		glosses = []
		separators = [""]
		#first empty index in separators[] is empty unless filled with by a '=' for a proclitic
		#if not empty, separators[0] is appended rather than prepended to final string output
		for m in morphList:
			sep=0
			for i in m.findall("item"):
	#			if self.args.count('v') != 0:
	#				print "getMorphParts list: ", i.items()
				if i.attrib.values()[0].count('txt'):
					txts.append(i.text) #.decode('utf-8'))		
				if i.attrib.values()[0].count('gls'):
					glosses.append(i.text) #.decode('utf-8'))
				if i.attrib.values()[0].count('morphType'):
					sep +=1
					if i.text.count('PROCLITIC')!=0:
						separators[0] = "="
					else:
						separators.append(self.getMorphSep('', i.text)) #.decode('utf-8')))
					print "^"*5, "separators:", separators
			if sep == 0:
				separators.append('-')
			
	#	if self.args.count('v') !=0:
	#		print txts, glosses, separators
		return txts, glosses, separators
				
				

#
#	Tree builder module, on-the-fly
#
#This module is not yet very useful, but will eventually be useful for building IGT ElementTrees from scratch within program,
#rather than relying on well-formed IGT contained within an external file
	def buildTree(self, convert = None):
		#"Build an IGT ElementTree from on-the-fly user inputs"
		#self (InterlinearText object)
		#convert (text string, 
		if self.args.count('v') != 0:
			print
			print "Beginning buildTree function"
			print "-"*10
			print
			
		root = ET.Element("resource")
		i_text = ET.SubElement(root, "interlinear_text")
		
		if convert == None:
			self.fillbuiltTree(i_text)
	
		self.e_tree = ET.ElementTree(root)
		if convert == None:
			self.filename="Generated Tree"
		else: self.filename="Converted Tree"
		
		if self.args.count('v') != 0:
			print "ending buildTree function"
		
		return self, i_text
		
		
	def fillbuiltTree(self, i_text):
	# use this as the basis for building any trees from other kinds of interlinear text documents
		#arguments:
		#self (InterlinearText object)
		#i_text (parent node to the rest of the tree contents)
		#fills up the built tree
	
		
		self.setMetadata(i_text, ['title', 'comment', 'author'], ['a tiny title here', 'a testy comment or two here', 'Jeremy the author'])
		#	self.setMetadata(i_text, ['x type', 'y type', 'z type'], ['x content', 'y content', 'z content'])
		self, phrases = self.setPhrases(i_text)	
		self, words = self.setPhrase(phrases) 			#self.setPhrase(phrases, number, 'original form', 'free translation')
		self, morphemes = self.setWord(words)		#self.setWord(words, 'original word text', 'word gloss')
		self, morph = self.setMorph(morphemes)		#self.setMorph(morphemes, 'morph text', 'morph gloss')
		
		return self
		
		
	def setMetadata(self, parent, itemTypes, itemContents):
		#arguments:
		#self (InterlinearText object)
		#parent (parent node for metadata children)
		#itemTypes (list, in order, of metadata types to add)
		#itemContents (list, in order, of metadata contents to add)
		
		if len(itemTypes) != len(itemContents):
			print "There is a mismatch between metadata item types and contents."
			print
			return self
			
		for item in itemTypes:
			ind = itemTypes.index(item)
			content = itemContents[ind]
			print ind, item, content
			self.setItem(parent, item, content)
		return self
	
		
	def setItem(self, parent, itemType, itemContent):
		#Set item within IGT. Takes parent node, itemType and itemContent as arguments."
		parent.item= None
		itemfind = parent.findall('item')
		if len(itemfind)>0 :
			for item in itemfind:
				if self.getContent(item, itemType) != None:
					parent.item = item
					parent.item.text = itemContent.decode('utf-8')
					if self.args.count('v') != 0:
						print "Overwriting '%s' item with content '%s'." % (itemType, itemContent)
					return self
					
		
		item=ET.SubElement(parent, "item")
		item.set("type", itemType)
		item.text = itemContent.decode('utf-8')
		if self.args.count('v') != 0:
			print "run setItem function for %s containing '%s'." % (itemType, itemContent)
		return self
	
		
	def setPhrases(self, i_text):
		#Set phrases in interlinear_text IGT. Takes parent node as argument."
		
		if self.args.count('v') != 0:
			print "begin setPhrases function"	
		
		phrases = ET.SubElement(i_text, "phrases")
		
		#need a way to iterate over phrases within interlinear_text object
		#self.setPhrase(phrases)
		
		if self.args.count('v') != 0:
			print "end setPhrases function"
		return self, phrases
		
		
	def setPhrase(self, phrases, number = None, text = None, gloss = None, insertindex = None):
		#Set single phrase in IGT, within parent phrases. Takes parent node as argument."
		# insertindex (optional index position to insert phrase within phrases element)
		
		
		
		if self.args.count('v') != 0:
			print "begin setPhrase function"
			
		#insert word at index if insertindex value is passed	
		if insertindex != None :
			insertindex = int(insertindex)
			if self.args.count('v')!=0:
				print "Now inserting new phrase into 'phrases' element at index '%d'." % insertindex
			phrase = ET.Element("phrase")
		else:
			phrase = ET.SubElement(phrases, "phrase")		
		
		if number == None:
			self.setNumber(phrase, str(1))
		else: self. setNumber(phrase, number)
		
		if text == None:
			text = None
		else: self.setText(phrase, text)
		
		if gloss == None:
			self.setGloss(phrase, ''.encode('utf-8'))
		else: self.setGloss(phrase, gloss)
			
		self, words = self.setWords(phrase)

		if insertindex != None:
			phrases.insert(insertindex, phrase)
			
		if self.args.count('v') != 0:
			print "end setPhrase function"
		
		return self, words

		
	def setWords(self, phrase):
		#Set words in interlinear_text IGT. Takes parent node 'phrase' as argument."
		
		if self.args.count('v') != 0:
			print "begin setWords function"	
		
		words = ET.SubElement(phrase, "words")
		
		if self.args.count('v') != 0:
			print "end setWords function"
		return self, words

		
	def setWord(self, words, text = None, gloss = None, insertindex = None):
		#Set single word in IGT, within parent words. Takes parent node as argument."
		# self (InterlinearText object)
		# words (element into which word will be inserted/added) 
		# text (optional text-level content for word)
		# gloss (optional gloss-level content for word)
		# insertindex (optional index position to insert word within words element)
		
		#disambiguates 'words' element from 'phrase' element
		if words.tag.count('phrase')!=0:
			newwords = words.getiterator('words')
			if newwords==None:
				self, words = self.setWords(words)
			else: words = newwords[0]
			
		if self.args.count('v') != 0:
			print "begin setWord function"
			
		#insert word at index if insertindex value is passed	
		if insertindex != None :
			insertindex = int(insertindex)
			if self.args.count('v')!=0:
				print "Now inserting new word into 'words' element at index '%d'." % insertindex
			word = ET.Element("word")
			

		else:
			word = ET.SubElement(words, "word")	
		
		#need to have a way of getting user-content for each item set within word object
		if text == None:
			if self.args.count('b')!=0:		
				self.setText(word, "tiva")
			else:
				None
		elif (type(text) == str and len(text)<1):
			if self.args.count('b')!=0:		
				self.setText(word, "tiva")
			else:
				None
		else: self.setText(word, text)
		
		if  gloss == None:
			if self.args.count('b')!=0:		
				self.setGloss(word, "tuvan")
			else:
				None
		elif (type(gloss) == str and len(gloss)<1):
			if self.args.count('b')!=0:		
				self.setGloss(word, "tuvan")
			else:
				None
		else: self.setGloss(word, gloss)
		
		self, morphemes = self.setMorphemes(word)
		
		
		if insertindex != None:
			words.insert(insertindex, word)
		
		if self.args.count('v') != 0:
			print "end setWord function"
		return self, morphemes
		
		
	def setMorphemes(self, word):
		#Set morphemes in interlinear_text IGT. Takes parent node as argument."
		
			
		if self.args.count('v') != 0:
			print "begin setMorphemes function"	
		
		morphemes = ET.SubElement(word, "morphemes")
		#need a way to iterate over morphemes contained in word
		#self.setMorph(morphemes)
		
		if self.args.count('v') != 0:
			print "end setMorphemes function"
		return self, morphemes
		
		
	def setMorph(self, morphemes, text = None, gloss = None, insertindex = None):
		#Set single morph in IGT, within parent morphemes. Takes parent node as argument."
		# self (InterlinearText object)
		# morphemes (element into which morph will be inserted/added) 
		# text (optional text-level content for morph)
		# gloss (optional gloss-level content for morph)
		# insertindex (optional index position to insert morph within morphemes element)
		
		#disambiguates 'morphemes' element from 'word' element
		if morphemes.tag.count('word')!=0:
			newmorphemes = morphemes.getiterator('morphemes')
			if newmorphemes==None:
				self, morphemes = self.setMorphemes(morphemes)
			else: morphemes = newmorphemes[0]
			
		if self.args.count('v') != 0:
			print "begin setMorph function"
		
		#insert morph at index if insertindex value is passed	
		if insertindex != None:
			insertindex = int(insertindex)
			if self.args.count('v')!=0:
				print "Now inserting new morph into 'morphemes' element at index '%d'." % insertindex
			morph = ET.Element("morph")

		else:
			morph = ET.SubElement(morphemes, "morph")

		
		if text == None and gloss == None and self.args.count('b')!=0:
			#need to have a way of getting user-content for each item set within morph object
			self.setText(morph, "tiva")
			self.setGloss(morph, "tuvan")
		
		elif text == None or gloss == None:
			print "# There is a morph content mismatch. Either text or gloss content is missing."
			return self, morph
		
		else: 
			self.setText(morph, text)
			self.setGloss(morph, gloss)
			
		if insertindex != None:
			morphemes.insert(insertindex, morph)
		
		#if morphType different, then
		#self.setItem(morph, "morphType","clitic")
		if self.args.count('v') != 0:
			print "end setMorph function"
		return self, morph
		
		
	def setNumber(self, node, number):
		#Set number data for node. Takes node and number as arguments."
#!!!! This is a really bad hack to make it work.
#!!!! why do we need to make number into a string?
#!!!! How do we leave it as an int without decoding it?
		
		node.number = None
		numfind = node.findall('item')
		if len(numfind)>0 :
			for num in numfind:
				if self.getContent(num, 'number')!= None:
					node.number = num
					node.number.text = str(number)
					if self.args.count('v') != 0:
						print "Overwriting number with content '%s'." % number
					
					return self
						
			
	
		node.number = ET.SubElement(node, "item")
		node.number.set("type","number")
		if str(number).isdigit() == True:
			node.number.text = str(number).decode('utf-8')
		else: node.number.text = str(number)
	
		
		if self.args.count('v') != 0:
			print "run setNumber function with '%s'." % str(number)
		return self 
		
		
	def setGloss(self, node, gloss):
		#Set gloss data for node. Takes node and gloss text as arguments."
		
		node.gls= None
		glsfind = node.findall('item')
		if len(glsfind)>0 :
			for gls in glsfind:
				if self.getContent(gls, 'gls') != None:
					node.gls = gls
					node.gls.text = gloss.decode('utf-8')
					if self.args.count('v') != 0:
						print "Overwriting gloss item with content '%s'." % gloss
					return self
					
		
		if self.getGloss(node) == None:	
			node.gls = ET.SubElement(node, "item")
			node.gls.set("type","gls")
			node.gls.text = gloss.decode('utf-8')
		
			
		if self.args.count('v') != 0:
			print "run setGloss function for '%s'." % gloss
		return self 
	
	def setText(self, node, text):
		#Set text data for node. Takes node and text as arguments.
		node.txt= None
		txtfind = node.findall('item')
		if len(txtfind)>0 :
			for txt in txtfind:
				if self.getContent(txt, 'txt') != None:
					node.txt = txt
					node.txt.text = text.decode('utf-8')
					if self.args.count('v') != 0:
						print "Overwriting text item with content '%s'." % text
					return self
					
		if self.getText(node) == None:
			node.txt = ET.SubElement(node, "item")
			node.txt.set("type","txt")
			node.txt.text = text.decode('utf-8')
		
		if self.args.count('v') != 0:
			print "run setText function for '%s'." % text
		return self 
		
	
	def setMorphType(self, node, morphType):
		#set morph type for morph. Takes morph node and string morphType as arguments.
		if node.tag.count('morph')!=0 and node.tag.count('morphemes')==0:
			print "This node may not have a morphType element, as it is not a morph element."
			raise AssertionError
			return None
			
		node.mType = None
		mTypefind = node.findall('item')
		if len(mTypefind)>0 :
			for mType in mTypefind:
				if self.getContent(mType, 'morphType')!= None:
					node.mType = mType
					node.mType.text = morphType
					if self.args.count('v') != 0:
						print "Overwriting morphType with content '%s'." % morphType
					
					return self
		
			node.mType = ET.SubElement(node, "item")
			node.mType.set('type', 'morphType')
			node.mType.text = morphType
		else: node.mType.text = morphType
		if self.args.count('v') != 0:
			print "run setMorphType function for '%s'." % text
		return self
	
		
	def removeNode(self, parent, delindex, strict = None):
		# removes a node from interlinear text elementTree, by finding its parent
		# self (InterlinearText object)
		# parent (parent element of node to delete)
		# delindex (index of node to delete)
		
		print "parent node is", parent
	
		delnode = self.getbyLoc(parent, delindex, strict)
		
		if strict != True:
			newparent = None
			if parent.tag.count('phrase')>0 and parent.tag.count('s')==1:
				newparent = parent.getiterator('words')
			if parent.tag.count('word')>0 and parent.tag.count('s')==0:
				newparent = parent.getiterator('morphemes')
			if newparent != None:
				parent = newparent[0]
				newparent = None
			
		parent.remove(delnode)
	
		return self
		
	
		
		

class ODFMaker :
	def __init__(self, args=None):
		filelist = ['']
		self.filelist = filelist
		if (args != None):
			self.args = args
		elif (args == None):
			self.args = ''
		return
			
		
	def setArgs(self, args):
		#Set arguments for operating modes
		#v: verbose
		#p: pretty print
		#q: quiet
		#o: OVERRIDE pretty printing (due to utf-8 problem with pretty print)

		self.args = args	
		if args.count('v') != 0:
			print "Running in mode: " 
			if args.count('v') != 0: 
				print "verbose"
			if args.count('p') != 0 and args.count('o') ==0: 
				print "pretty printing"
			if args.count('o') != 0:
				print "OVERRIDE pretty printing"
			if args.count('t') != 0: 
				print "print content tree building notices"
			if args.count('x') != 0:
				print "chunk IGT no tables"
			if args.count('a') != 0:
				print "make parallel archival.xml file inside odf"
			print
		return self
		
		
	def makeManifest(self):
		#make an elementTree for the manifest.xml file within the ODF document
		#Initially, it makes an absolutely minimal skeleton for an ODF document, 
		#including only manifest.xml and content.xml files
		#
		#remember to update this function as more files are required (style.xml, meta.xml, etc.)
		root = ET.Element("manifest:manifest")
		root.set("xmlns:manifest", "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0")

		file1 = ET.SubElement(root, "manifest:file-entry")
		file1.set("manifest:media-type", "application/vnd.oasis.opendocument.text")
		file1.set("manifest:full-path", "/")
		
		#add other non-essential files here in the form of the one below
		file2 = ET.SubElement(root, "manifest:file-entry")
		file2.set("manifest:media-type", "text/xml" )
		file2.set("manifest:full-path", "content.xml")
		
		if self.args.count('a') != 0:
			file3 = ET.SubElement(root, "manifest:file-entry")
			file3.set("manifest:media-type", "text/xml" )
			file3.set("manifest:full-path", "archival.xml")
		
		# wrap it in an ElementTree instance, and save as XML
		self.manifest = ET.ElementTree(root)
	
		if self.args.count('v') != 0: 
			manifestfile = printRoot(self.manifest, 'pretty', self.args)
		
		self.filelist.append("manifest.xml")
		return self
	
		
	def makeContent(self, interlinear_text = None):
		#make an elementTree for the content.xml file within the ODF document
		#takes ODFMaker object (as self) and an optional InterlinearText object 

		root = ET.Element("office:document-content")
		root.set("xmlns:office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0")
		root.set("xmlns:style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0")
		root.set("xmlns:text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0")
		root.set("xmlns:table", "urn:oasis:names:tc:opendocument:xmlns:table:1.0")
		root.set("xmlns:draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0")
		root.set("xmlns:fo", "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0")
		root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
		root.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
		root.set("xmlns:meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0")
		root.set("xmlns:number", "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0")
		root.set("xmlns:svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0")
		root.set("xmlns:chart", "urn:oasis:names:tc:opendocument:xmlns:chart:1.0")
		root.set("xmlns:dr3d", "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0")
		root.set("xmlns:math", "http://www.w3.org/1998/Math/MathML")
		root.set("xmlns:form", "urn:oasis:names:tc:opendocument:xmlns:form:1.0")
		root.set("xmlns:script", "urn:oasis:names:tc:opendocument:xmlns:script:1.0")
		root.set("xmlns:ooo", "http://openoffice.org/2004/office")
		root.set("xmlns:ooow", "http://openoffice.org/2004/writer")
		root.set("xmlns:oooc", "http://openoffice.org/2004/calc")
		root.set("xmlns:dom", "http://www.w3.org/2001/xml-events")
		root.set("xmlns:xforms", "http://www.w3.org/2002/xforms")
		root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
		root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")		
		root.set("office:version", "1.0")
		
		file1 = ET.SubElement(root, "office:scripts")
		file2 = ET.SubElement(root, "office:font-face-decls")
		font = ET.SubElement(file2, "style:font-face")
		#to change font style for document, change the content in the following 'set' methods
		#these are probably not necessary, though I'm not certain about that
		font.set("style:name", "Times New Roman")
		font.set("svg:font-family", "&apos;Times New Roman&apos;")
		font.set("style:font-family-generic", "roman")
		font.set("style:font-pitch", "variable")
	
		#setting default styles for lines of igt with automatic-styles
		if self.args.count('x')!=0:
			file3 = ET.SubElement(root, "office:automatic-styles")
			freestyle= ET.SubElement(file3, "style:style")
			freestyle.set("style:name", "free")
			freestyle.set("style:family", "paragraph")
			freestyleChild = ET.SubElement(freestyle, "style:text-properties")
			freestyleChild.set("fo:font-weight", "bold")
			freestyleChild.set("fo:font-weight-asian", "bold")
			freestyleChild.set("fo:font-weight-complex", "bold")
			
			txtstyle= ET.SubElement(file3, "style:style")
			txtstyle.set("style:name", "txt")
			txtstyle.set("style:family", "paragraph")
			txtstyleChild = ET.SubElement(txtstyle, "style:text-properties")
			txtstyleChild.set("fo:color", "#008080")
			txtstyleChild.set("fo:font-weight", "bold")
			txtstyleChild.set("fo:font-weight-asian", "bold")
			txtstyleChild.set("fo:font-weight-complex", "bold")
			
			glsstyle= ET.SubElement(file3, "style:style")
			glsstyle.set("style:name", "gls")
			glsstyle.set("style:family", "paragraph")
			glsstyleChild = ET.SubElement(glsstyle, "style:text-properties")
			glsstyleChild.set("fo:font-weight", "normal")
			glsstyleChild.set("fo:font-weight-asian", "normal")
			glsstyleChild.set("fo:font-weight-complex", "normal")
			
			print "added style declarations for free, text and gloss lines"
		
		
		body = ET.SubElement(root, "office:body")
		text = ET.SubElement(body, "office:text")
		#content is added as subelements to this body node
		
		#checks to see whether interlinear_text was passed in, and if it contains an ElementTree)
		if (interlinear_text != None) and (ET.iselement(interlinear_text.e_tree.getroot())):
			#creates paragraphs in content ElementTree for each metadata item 
			if self.args.count('t') != 0:
				print
				print "-------building content tree for content.xml file in ODF document-------------------"
				print
			
			if self.args.count('x') != 0:	
				self = self.fillMetadata(interlinear_text, text)
				self = self.chunkIGT(interlinear_text, text)
				
			else: 
				self = self.fillMetadata(interlinear_text, text)	
				self = self.fillPhrases(interlinear_text, text)
				
			if self.args.count('t') != 0:
				print
				print "-------end building of content tree-------------------"
				print
					
		# wrap it in an ElementTree instance, and save as XML
		self.content = ET.ElementTree(root)
		self.filelist.append("content.xml")
		return self
		
	
	def chunkIGT(self, interlinear_text, position):
		#takes InterlinearText object and outputs phrases as chunks (text:section including text:body nodes) rather than tables.
		#self (ODFMaker object)
		# interlinear_text (InterlinearText object that is being parsed to the ODF doc)
		# position (parent node, should be text)
		if self.args.count('v') != 0:
			print "Run chunkIGT function --"
		
		if self.args.count('x') >= 2:
			section = ET.SubElement(position, "text:section")
			section.set("text:name", "interlinear text resource")
			section.append(interlinear_text.e_tree.getroot())
		
		else: 
			self.fillPhrasesX(interlinear_text, position)
			
		return self
		
		
			
	def fillMetadata(self, interlinear_text, position):
		# arguments: self = ODFMaker object
		# interlinear_text (InterlinearText object that is being parsed to the ODF doc)
		# position (parent node, should be text)
		if self.args.count('v') != 0:
			print "Run fillMetadata function --"
			
		meta = interlinear_text.findMetadata()
		if meta != None:
			for m in meta:
				metadata = ET.SubElement(position, "text:p")
				metadata.set("text:style-name", "Standard")
				metadata.text = m.text
				if self.args.count('v') != 0:
					print "adding metadata '%s' to content tree." % m.text
		return self 
		
		
	def fillPhrases(self, interlinear_text, position):
		# arguments: self = ODFMaker object
		# interlinear_text (InterlinearText object that is being parsed to the ODF doc)
		# position (parent node, should be text)
		
		if self.args.count('v') != 0:
			print "Run fillPhrases function --"
		
		i = 1
		#creates tables in content ElementTree for each phrase item 
		for p in interlinear_text.findPhrases():
			blank = ET.SubElement(position, "text:p")
			blank.set("text:style-name", "Standard")
			
			phrase = ET.SubElement(position, "table:table")
			phrase.set("table:name", "Table"+str(i))
			i +=1
			#phrase.set("table:style-name", "Table"+str(i))
			
			wordList =interlinear_text.findWords(p)
			numWords = len(wordList)
			
			phraseTableColumn = ET.SubElement(phrase, "table:table-column")
			#phraseTableColumn.set("table:style-name", "Table"+str(i)+".A")
			phraseTableColumn.set("table:number-columns-repeated", str(numWords))
				
			phraseTableRow = ET.SubElement(phrase, "table:table-row")
			phraseTableCell = ET.SubElement(phraseTableRow, "table:table-cell")
			phraseTableCell.set("table:number-columns-spanned", str(numWords))
			phraseTableCell.set("office:value-type", "string")
			
			phraseP = ET.SubElement(phraseTableCell , "text:p")

			phraseP.text = interlinear_text.getOther(p, "number")+". "+interlinear_text.getGloss(p)
		
			if self.args.count('t') != 0:
				print "Adding phrase '%s' to content tree." % phraseP.text.encode('utf-8')
			
			j = numWords		#this needs to correspond to column total for table
			while ( j > 1 ):
				coveredTable = ET.SubElement(phraseTableRow, "table:covered-table-cell")
				j -=1
				
			if interlinear_text.getText(p):
				phraseTableRow = ET.SubElement(phrase, "table:table-row")
				phraseTableCell = ET.SubElement(phraseTableRow, "table:table-cell")
				phraseTableCell.set("table:number-columns-spanned", str(numWords))
				phraseTableCell.set("office:value-type", "string")
				
				phraseP = ET.SubElement(phraseTableCell , "text:p")
	
				phraseP.text = interlinear_text.getOther(p, "number")+". "+interlinear_text.getText(p)
			
				if self.args.count('t') != 0:
					print "Adding phrase '%s' to content tree." % phraseP.text.encode('utf-8')
				
				j = numWords		#this needs to correspond to column total for table
				while ( j > 1 ):
					coveredTable = ET.SubElement(phraseTableRow, "table:covered-table-cell")
					j -=1

			PhraseTableRow2 = ET.SubElement(phrase, "table:table-row")
			
			self, i = self.fillWords(interlinear_text, wordList, PhraseTableRow2, i)
		return self
			
		
	def fillWords(self, interlinear_text, wordList, position, i):
		# arguments: self = ODFMaker object
		# interlinear_text (InterlinearText object that is being parsed to the ODF doc)
		# wordList (List of word elements from interlinear text elementTree) 
		# position (parent node, should be PhraseTableRow2)
		# i (integer counter for words)
		if self.args.count('v') != 0:
			print "Run fillWord function --"
			
		for w in wordList:
			word = ET.SubElement(position, "table:table-cell")
			word.set("office:value-type", "string")
			
			wordTable = ET.SubElement(word, "table:table")
			wordTable.set("table:name", "Table"+str(i))
			i +=1
			morphList =interlinear_text.findMorphs(w)
			numMorphs = len(morphList)
			
			wordTableColumn = ET.SubElement(wordTable, "table:table-column")
			
			if numMorphs > 1:
				wordTableColumn.set("table:number-columns-repeated", str(numMorphs))
			
			#fill two lists with the contents of the txt and gloss items contained in a word
			#this is needed because OO makes tables with the rows containing
			#the cells with content, rather than columns
			
		#	this function is slightly faster, but not as robust in terms of unicode support
		#	use only if necessary, and remove folowing set of calls
		#	txts, glosses, separators = interlinear_text.getMorphParts(morphList)
			
		
			txts =[]
			glosses = []
			separators = ['']
			
			for m in morphList:
				txt = interlinear_text.getText(m)
				txts.append(txt)	
				glosses.append(interlinear_text.getGloss(m))
				mtype =interlinear_text.getOther(m, 'morphType')
				if mtype!=None:
					if mtype.count('PROCLITIC')!=0:
						separators[0] = "="
						print '^'*3, 'Proclitic - separators[0] is now', separators[0]
					else:
						separators.append(interlinear_text.getMorphSep(m))
				else: separators.append('-')
				
				
	#This should become a real error tagging utility.
	#
			if numMorphs != len(txts) != len(glosses):
				print "There is a mismatch in glossing"
				
			if numMorphs == 0:
				txts.append(interlinear_text.getText(w))
				glosses.append(interlinear_text.getGloss(w))
			
			wordTableRow = ET.SubElement(wordTable, "table:table-row")
			self = self.fillMorphs(txts, separators, wordTableRow)
		
			wordTableRow2 = ET.SubElement(wordTable, "table:table-row")
			#self = self.fillMorphs(txts, wordTableRow2)
			self = self.fillMorphs(glosses, separators, wordTableRow2)
		return self, i
		
		
	def fillMorphs(self, morphlist, separators, position, tag = None):
		# arguments: self = ODFMaker object
		# morphlist (list of morphs (not iterator) taken from fillWord function)
		# separators (list of morpheme separators taken from fillWord function)
		# position (parent node, should be wordTableRow or wordTableRow2)
		# tag (type of morph, ie. gls or txt) 		--Not yet needed, will be for later class attributing of morph table cells
		if self.args.count('v') != 0:
			print "Run fillMorphs function --"
		l = 0
		pro = None
		
		for k in morphlist:
			wordTableCell = ET.SubElement(position, "table:table-cell")
			wordTableCell.set("office:value-type", "string")
			
			morphP = ET.SubElement(wordTableCell, "text:p")
			#morphP.set("text:style-name", "Standard")
			if l != 0 and pro == None:
				k = separators[l]+k
				if self.args.count('v') !=0:
					print "Inserted %s before morph %s." % (separators[l], str(l+1))
			elif l!=0 and pro ==1:
				pro = None
			elif l == 0 and len(separators[0])>0:
				k = k+separators[l]
				if self.args.count('v') !=0:
					print "Inserted PROCLITIC %s after morph %s." % (separators[l], str(l+1))
				pro = 1
				
			l += 1
			morphP.text = k
		return self 


#fill X section -- no tables ODF output, using working model for implant as of 2.23.08		
	
	def fillPhrasesX(self, interlinear_text, position):
		# fill phrases as part of output from InterlinearText object into ODFMaker content elementTree using working model 2.23.08 instead of tables
		# self (ODFMaker object)
		# interlinear_text (InterlinearText object that is being parsed to the ODF doc)
		# position (parent node, should be text)
		
		if self.args.count('v') != 0:
			print "Run fillPhrasesX function --"
		
		i = 1
		#creates tables in content ElementTree for each phrase item 
		for p in interlinear_text.findPhrases():
			phrase = ET.SubElement(position, "text:section")
			phrase.set("text:name", "phrase"+str(i))
			
			#phrase.set("table:style-name", "Table"+str(i))
			
			wordList =interlinear_text.findWords(p)
			numWords = len(wordList)


			self, i = self.fillWordsX(interlinear_text, wordList, phrase, i)
			
			phraseP = ET.SubElement(phrase, "text:p")
			phraseP.set("text:style-name", "free")
			freeSpan = ET.SubElement(phraseP, "text:span")
			freeSpan.set("text:style-name", "free")
		#	freeSpan.set("text:style-name", "phrase"+str(i)+".free")
			freeSpan.text = interlinear_text.getOther(p, "number")+". "+interlinear_text.getGloss(p)
		
			if self.args.count('t') != 0:
				print "Adding phrase '%s' to content tree." % phraseP.text.encode('utf-8')
			
			i +=1
			
		return self
			
		
	def fillWordsX(self, interlinear_text, wordList, position, i):
		# fill words as part of output from InterlinearText object into ODFMaker content elementTree using working model 2.23.08 instead of tables
		# self (ODFMaker object)
		# interlinear_text (InterlinearText object that is being parsed to the ODF doc)
		# wordList (List of word elements from interlinear text elementTree) 
		# position (parent node, should be PhraseTableRow2)
		# i (integer counter for words)
		if self.args.count('v') != 0:
			print "Run fillWordX function --"
			

		
		phraseText = []
		phraseGloss = []
		phraseSeparators = []
		for w in wordList:
			morphList =interlinear_text.findMorphs(w)
			numMorphs = len(morphList)
			wordtxts =[]
			wordglosses = []
			separators = ['']
			
			for m in morphList:
				txt = interlinear_text.getText(m)
				wordtxts.append(txt)		
				wordglosses.append(interlinear_text.getGloss(m))
				mtype =interlinear_text.getOther(m, 'morphType')
				if mtype!=None:
					if mtype.count('PROCLITIC')!=0:
						separators[0] = "="
						print '^'*3, 'Proclitic - separators[0] is now', separators[0]
					else:
						separators.append(interlinear_text.getMorphSep(m))
				else: separators.append("-")
			
				
			if numMorphs != len(wordtxts) != len(wordglosses):
				print "There is a mismatch in morpheme glossing"
				print "There are %d text morphemes and %d gloss morphemes. Please correct this problem." % (len(wordtxts), len(wordglosses))
			
			if numMorphs == 0:
				wordtxts.append(interlinear_text.getText(w))
				wordglosses.append(interlinear_text.getGloss(w))
				
			phraseText.append(wordtxts)
			phraseGloss.append(wordglosses)
			phraseSeparators.append(separators)
			
		phraseP = ET.SubElement(position, "text:p")
		phraseP.set("text:style-name", "txt")
		
		h=0
		for word in phraseText:
			if h != 0:
				tabstop = ET.SubElement(phraseP, "text:tab-stop")
			textSpan = ET.SubElement(phraseP, "text:span")
			textSpan.set("text:style-name", "txt")
			#textSpan.set("text:style-name", "p"+str(i)+".w"+str(h)+" text")
			j = 0
			pro = None
			for morph in word:						
				if j!=0 and pro == None:	#if not first morpheme and not preceded by a Proclitic, then insert morpheme separator from list
					sepSpan = ET.SubElement(textSpan, "text:span")
					sepSpan.text = phraseSeparators[h][j]
					if self.args.count('v') !=0:
						print "Inserted %s before morph %s." % (sepSpan.text, str(j+1))
				
				elif j!=0 and pro != None:
					pro =None
				
					
				mSpan = ET.SubElement(textSpan, "text:span")
				mSpan.set("text:style-name", "txt")
			#	mSpan.set("text:style-name", "p"+str(i)+".w"+str(h)+".m"+str(j)+".text")
				mSpan.text = morph
				if j==0 and len(phraseSeparators[h][j])>0:
					pro = 1
					sepSpan = ET.SubElement(textSpan, "text:span")
					sepSpan.text = phraseSeparators[h][j]
					if self.args.count('v') !=0:
						print "Inserted PROCLITIC %s after morph %s." % (sepSpan.text, str(j+1))
				
				j +=1	
			h +=1
			
		phraseP2 = ET.SubElement(position, "text:p")
		phraseP2.set("text:style-name", "gls")
		h=0
		for word in phraseGloss:
			if h != 0:
				tabstop = ET.SubElement(phraseP2, "text:tab-stop")
			textSpan = ET.SubElement(phraseP2, "text:span")
			textSpan.set("text:style-name", "gls")
		#	textSpan.set("text:style-name", "p"+str(i)+".w"+str(h)+"gloss")
			j = 0
			pro = None
			for morph in word:
				if j!=0 and pro == None:	#if not first morpheme and not preceded by a Proclitic, then insert morpheme separator from list
					sepSpan = ET.SubElement(textSpan, "text:span")
					sepSpan.text = phraseSeparators[h][j]
					if self.args.count('v') !=0:
						print "Inserted %s before morph %s." % (sepSpan.text, str(j+1))
				
				elif j!=0 and pro != None:
					pro =None		
						
				mSpan = ET.SubElement(textSpan, "text:span")
				mSpan.set("text:style-name", "gls")
			#	mSpan.set("text:style-name", "p"+str(i)+".w"+str(h)+".m"+str(j)+".gloss")
				mSpan.text = morph	
				if j==0 and len(phraseSeparators[h][j])>0:
					pro = 1
					sepSpan = ET.SubElement(textSpan, "text:span")
					sepSpan.text = phraseSeparators[h][j]
					if self.args.count('v') !=0:
						print "Inserted PROCLITIC %s after morph %s." % (sepSpan.text, str(j+1))
				j +=1	
			h +=1
			
			
				
#			self = self.fillMorphsX(glosses, separators, wordTableRow2)
		
		return self, i
		
		
	def fillMorphsX(self, morphlist, separators, position, tag = None):
		# self (ODFMaker object)
		# morphlist (list of morphs (not iterator) taken from fillWord function)
		# separators (list of morpheme separators taken from fillWord function)
		# position (parent node, should be wordTableRow or wordTableRow2)
		# tag (type of morph, ie. gls or txt) 		--Not yet needed, will be for later class attributing of morph table cells
		if self.args.count('v') != 0:
			print "Run fillMorphsX function --"
		l = 0
		pro = None
		
		print "morphlist:", morphlist, "of length", len(morphlist)
		print "separators:", separators, "of length", len(separators)
		
		for k in morphlist:
			wordTableCell = ET.SubElement(position, "table:table-cell")
			wordTableCell.set("office:value-type", "string")
			
			morphP = ET.SubElement(wordTableCell, "text:p")
			#morphP.set("text:style-name", "Standard")
			if l != 0 and pro == None:
				k = separators[l]+k
				if self.args.count('v') !=0:
					print "Inserted %s before morph %s." % (separators[l], str(l+1))
			elif l!=0 and pro == 1:
				pro = None
			elif l == 0 and len(separators[0])>0:
				k = k+separators[l]
				if self.args.count('v') !=0:
					print "Inserted PROCLITIC %s after morph %s." % (separators[l], str(l+1))
				pro = 1
			l += 1
			morphP.text = k
		return self 


# end fill X section -------



		
	def makeMeta(self, interlinear_text = None):
		#this function should create an elementTree for the meta.xml file within the ODF document
		if ET.iselement(interlinear_text.e_tree.getroot()):
			print "Will extract metadata information from InterlinearText object and put it into the meta.xml file."
			print
			self.filelist.append("meta.xml")
		return self
		
		
	def makeArchivalform(self, interlinear_text):
		#this function takes the interlinear_text object and writes a verbatim copy to archival.xml within the ODF document
		# self (ODFMaker object)
		# interlinear_text (InterlinearText object)
		
		if interlinear_text.archival != None:
			self.archival = interlinear_text.archival
		else:
			self.archival =interlinear_text.e_tree
			
		if ET.iselement(self.archival.getroot()):
			print "Will make archival form of '"+interlinear_text.filename+"' within ODF document.."
			self.filelist.append("archival.xml")
		return self
		
		
		
		
	def output(self, output_file):
		#this function takes the output filename and opens an ODF zipfile,
		#then writes the manifest and content files to the zipfile
		# self (ODFMaker object)
		# output_file (text string output_file name)
		
		if "content.xml" in self.filelist and "manifest.xml" in self.filelist:
			print
			print "Output the ODF document '%s'." % output_file
			print
			newfile = zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED)
			newfile.encoding = 'utf-8'
			
			newfile.writestr("mimetype", "application/vnd.oasis.opendocument.text")
			if "meta.xml" in self.filelist:
				if self.args.count('o') != 0: newfile.writestr("meta.xml", xml_header+printRoot(self.meta, 'pretty', self.args).decode('utf-8'))	
				else: newfile.writestr("meta.xml", printRoot(self.meta, 'pretty', self.args))
				#metafile = open('meta.xml', 'a+')
				#metafile.encoding = 'utf-8'
				#metafile.write(printRoot(self.meta, 'pretty', self.args).decode('utf-8'))
				#newfile.write(metafile, 'meta.xml')
				#metafile.close()
				
			if "archival.xml" in self.filelist:
				if self.args.count('o') != 0: newfile.writestr("archival.xml", xml_header+printRoot(self.archival, 'pretty', self.args).decode('utf-8'))	
				else: newfile.writestr("archival.xml", printRoot(self.archival, 'pretty', self.args))
				
			if self.args.count('o') != 0: newfile.writestr("content.xml", xml_header+printRoot(self.content, 'pretty', self.args).decode('utf-8'))
			else: newfile.writestr("content.xml", printRoot(self.content, 'pretty', self.args))
			
			newfile.writestr("META-INF/manifest.xml", printRoot(self.manifest, 'pretty', self.args))
			newfile.close()

			self.testZip(output_file)
			
		else:
			print "ODFMaker object does not have a manifest or content elementTree."
			print "please create them first, then try to output the ODF file first."
			sys.exit(0)
			
		return self
			
		
	def testZip(self, zipfile_name):
		#test if it's a good zipfile.
		#arguments: self (ODFMaker object)
		# zipfile_name (name of zipfile to check)
		
		newfile = zipfile.ZipFile(zipfile_name, 'r')
		if self.args.count('v') !=0:
			print 
			print "------- Testing '%s' ODF file :" % zipfile_name
			print
			
		if newfile.testzip() != None:
			print "Program failed to output a valid zip file. Please check output content using test programs."
			sys.exit(0)
			
		if self.args.count('v') !=0:
			print "Files included in output ODF file include:"
			for s in newfile.infolist():	
				print s.orig_filename, s.date_time, s.filename, s.file_size, s.compress_size
			print
			print "-------- End testing"
			
		newfile.close()
		
		
#program-wide methods

def printRoot(e_tree, pr = None, args = None, filename = None):
	#"Print ElementTree structure and contents."
	if ET.iselement(e_tree.getroot()) == "false":	
		print "Tried to pass an object which was not an element tree to function printRoot()"
		sys.exit(0)
		
	stringtree = ET.tostring(e_tree.getroot(), 'utf-8')
	if (args.count('v') != 0 and args.count('p') == 0) or args.count('o') != 0:
		if filename:
			print "In %s:" % filename
		print stringtree
	
	elif args.count('p') != 0 or pr == "pretty" and args.count('o') == 0 :
		#trying to pretty print with xml.dom.minidom
		dom3 = parseString(stringtree)
		#!!! need to fix pretty print with utf-8 input
		
		pretty = dom3.toprettyxml()
		if args.count('p') != 0 and (args.count('o') == 0 or args.count('q')==0):
			print pretty.encode('utf-8')
		dom3.unlink()
		return pretty.encode('utf-8') 
		
	else:
		print stringtree
	return stringtree
	

def makeIGT(input_file, output_file=None, args = None):
	#arguments:
	#input_file (name for input IGT file)
	#output_file (xml output of InterlinearText elementTree)
	#args (arguments passed from command-line, or others)
	#runs all of the necessary processes for making an InterlinearText object from an input file
	
	if output_file != None and args == None:
		if output_file.beginswith('-'):
			args = output_file
			output_file = None
	
	if args == None:
		args = '-'
			
	if args.count('v') !=0:
		print "Now making InterlinearText object in one fell swoop"
		print "-"*10
		print
# use this sparingly, it is unsafe to use:
#	interlinear_text = InterlinearText(input_file, args)
	interlinear_text = InterlinearText()
	interlinear_text = interlinear_text.fillTree(input_file, args)

	if (args.count('q') ==0) and (args.count('v') != 0) :
		interlinear_text.printRoot()
		
	if output_file != None:
		interlinear_text.write(output_file)
	
	return interlinear_text
		

def makenewIGT(output_file = None, args = None):
	#arguments:
	#output_file (xml output of InterlinearText elementTree)
	#args (arguments passed from command-line, or others)
	#runs all of the necessary processes for making an InterlinearText object from a scratch
	
	if output_file != None and args == None:
		if output_file.beginswith('-'):
			args = output_file
			output_file = None
	
	if args == None:
		args = '-'
		
	if args.count('v') !=0:
		#run if 'v' for 'verbose' is passed with initial arguments
		print 
		print "Building a new tree:"
		print
	tree4 = InterlinearText()
	tree4.setArgs(args)
	tree4.buildTree()
	tree4.checkType()
	tree4.printRoot()
	
	if output_file != None:
		tree4.write(output_file, 'pretty')
	
	return tree4
	
	
def makeODF(interlinear_text, output_file, args = None):
	#arguments:
	#interlinear_text (InterlinearText object)
	#output_file (name for output ODF file)
	#args (arguments passed from command-line, or others)
	#runs all of the necessary processes for making an ODF file from an InterlinearText object
	
	if args.count('v') !=0:
		print "Now making ODF output in one fell swoop"
		print "-"*10
		print
		
	ODF_this = ODFMaker()
	ODF_this.setArgs(args)
	
	if args.count('a'):
		ODF_this.makeArchivalform(interlinear_text)
	ODF_this.makeManifest()
#	ODF_this.makeMeta(interlinear_text)
	ODF_this.makeContent(interlinear_text)
	ODF_this.output(output_file)
	
	return ODF_this
	
	
	
def demo(input_file, output_file, args = None):
	#arguments:
	#input_file (name for input IGT file)
	#output_file (name for output ODF file)
	#args (arguments passed from command-line, or others)
	#
	#demonstrates some of the basic capabilities of the program
	
#testing the building capabilities of the program
#	
	myTree = makeIGT(input_file, "sample.xml", args)
	
	if args.count('v') !=0:
		myTree.findPhrases()
		myTree.findWords()
		myTree.findMorphs()
	
#	if args.count('b') !=0:
		#run if 'b' for 'build' is passed with initial arguments
		#this module has pretty major problems with the encoding, I think
		
#		tree4 = makenewIGT('homebuilt.xml', args)
		

#		
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
					
		myTree.findContent('people')
	
		if args.count('b') != 0:
			tree4.findMetadata()
			phrases=tree4.findPhrases()
			for s in phrases:
				words=tree4.findWords(s)
				for j in words:
					tree4.findMorphs(j)
			tree4.findContent('tiva')
		print "End find demo"
		print "-"*10
		print
		
	print	
	print"-"*10, args, "-"*10
	print
	makeODF(myTree, output_file, args)
	
	if args.count('q')==0:
		print "Now exiting the demonstration of ETtheInterlinear"
		print "-"*20
	print
	sys.exit(0)

	
#### run main program
if __name__ == '__main__':
	if len(sys.argv)<3:
		print "Usage:  python ETtheInterlinear.py input_xml_file output_ODF_file -args"
		print "You have", len(sys.argv)-1, "arguments for the program."
		print "Arguments must be preceded by a '-'."
		print "'v' : verbose running"
		print "'q' : quiet running"
		print "'p' : pretty printing"
		print "'b' : demo build tree from scratch"
		print "'t' : ODF tree building notices"
		print "'d' : run demo"
		print "'x' : use chunk of IGT rather than tables"
		print "'a' : make parallel archival.xml file inside odf"
			
	
		sys.exit(0)
	
	if len(sys.argv)<4:
		args = '-vpdx'
		
	else:
		args = sys.argv[3]

	if args.count('d') != 0:
	#if 'd' is passed with demo, run demo of program abilities
		demo(sys.argv[1], sys.argv[2], args)

	if args.count('b') !=0:
	#run if 'b' for 'build' is passed with initial arguments
		
		tree4 = makenewIGT('homebuilt.xml', args)
		makeODF(tree4, 'homebuilt.odt', args)
		
	if args.count('i') !=0:
		tree5 = InterlinearText()
		tree5.setArgs(args)
		tree5.fillTree(sys.argv[1])
		tree6 = tree5.convert()
		tree6.printRoot()
		tree6.close()

		
	if args.count('d')==0 and args.count('i')==0 and args.count('b')==0:
		myTree = makeIGT(sys.argv[1], "sample.xml", args)
		makeODF(myTree, sys.argv[2], args)
		
	
	sys.exit(0)



#junk in the attic: clear this if you don't need it anymore
#otherwise, use for reference or usage tips


#put this in the first line of the program if you need to---
# This Python file uses the following encoding: utf-8

