# ETIwithUno.py
#current version: 0.02
#
#Based on the Pangloss test program ETtheInterlinear.py v0.12
#
#Purposes of application: 
#test macro for creating interlinear glossed texts within OpenOffice.org
#
#
# usage: (must be used as a macro within OpenOffice.org)
# g_scripts = silentETDemo, runETIwithUNO, createTables,
#
#author: Jeremy Fahringer
#for Rosetta Project, Pangloss
#(restricted access documentation at http://wiki.rosettaproject.org/PanglossDoc)
#(restricted access project information at http://wiki.rosettaproject.org/Pangloss)
import os, sys
import xml.dom
import xml
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET
import zipfile
import zlib

#import the following modules to work with OpenOffice and the UNO module.
#Unfortunately, this only works as an OpenOffice macro, and will fail to load properly 
#in the Python interpreter (command-line)

import uno
# a UNO struct later needed to create a document
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
from com.sun.star.text.TextContentAnchorType import AS_CHARACTER
from com.sun.star.awt import Size
from com.sun.star.lang import XMain

from eti import ETtheInterlinear
	


#set header for output xml file here"
xml_header ="<?xml version='1.0' encoding='utf-8'?> \n"
xsl_header ="<?xml-stylesheet type='text/xsl' href='"
xsl_file="IGTv2.4.xsl"
xsl_header_final="'?> \n"



class UnoInterlinear :
	def __init__(self, args=None):
		e_tree = None
		
		if (args != None):
			self.args = args
		elif (args == None):
			self.args = ''
		return
		
	def setTree(self, interlinear_text):
		#add ''interlinear_text'' InterlinearText object to UnoInterlinear object 
		self.i_text = interlinear_text
		if (interlinear_text.args != None) and (len(interlinear_text.args)>0):
			if (self.args == None):
				self.args=interlinear_text.args
		return self
				
	def createDoc(self):
		"""creates a new writer document and creates a TextCursor""" 
		ctx = uno.getComponentContext()
		smgr = ctx.ServiceManager
		desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
		
		# open a writer document
		doc = desktop.loadComponentFromURL( "private:factory/swriter","_blank", 0, () )
		text, cursor = self.createText(doc)
		
		return doc, text, cursor
	
		
	def createText(self, doc):
		text = doc.Text
		cursor = text.createTextCursor()
		
		return text, cursor

		

	def writeAll(self, interlinear_text=None):
		#creates a new writer document and writes all contents of (passed or included)
		#interlinear text object to document
		print 'nothing to see here, folks.'
'''		
		if (interlinear_text == None) and (self.i_text == None):
			print "No interlinear text was available to write to a new document"
			break
		elif (interlinear_text != None) and (self.i_text == None):
			self.i_text = interlinear_text


		doc, text, cursor = self.createDoc()
		
		meta = self.i_text.findMetadata()
		if meta != None:
			for m in meta:
				text.insertString( cursor, m, 0)
		else: print 'No metadata was included with this interlinear text.'

		return self
'''
'''
	
	def addPhrase(self, doc, text, cursor, node):
		#adds contents of phrase node (from InterlinearText object) to text
		#of writer document at cursor position
		print 'nothing to see here, folks.'
		
		return self, cursor
			
		
'''
'''	
	def insertTextIntoCell( self, table, cellName, text, color ):
		tableText = table.getCellByName( cellName )
		cursor = tableText.createTextCursor()
		cursor.setPropertyValue( "CharColor", color )
		tableText.setString( text )
	
	
	def testET(self, text, cursor):
		elem = ET.Element("tag", first="1", second="2")
		text.insertString(cursor, str(elem.attrib.get("first"))+"\n\n\n", 0)
		
		
	def createTables(self):
		"""creates a new writer document and inserts a table with some data (also known as the SWriter sample)""" 
		ctx = uno.getComponentContext()
		smgr = ctx.ServiceManager
		desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
		
		# open a writer document
		doc = desktop.loadComponentFromURL( "private:factory/swriter","_blank", 0, () )
		
		text = doc.Text
		cursor = text.createTextCursor()
		
		# write paths in sys.path
	#	for x in sys.path:
	#		text.insertString( cursor, str(x)+"\n", 0)
	#	text.insertString(cursor, str(sys.version)+"\n\n", 0)
		
		# test functions
		# testET(text, cursor)
		
		#create InterlinearText object
		if (!self.i_text):
			args = '-vpx'
			myTree = makeIGT('/Users/midnight/Work/pangloss/testingsvn/boktu-short.xml', '/Users/midnight/Work/pangloss/testingsvn/outputsample.xml', args)
			#makeODF(myTree, '/Users/midnight/Work/pangloss/testingsvn/testoutput.odt', args)
		
			#create UnoInterlinear object
			self = UnoInterlinear(args)
			self = self.setTree(myTree)
		
		#print metadata
		metaset = self.i_text.findMetadata()
		
		# create table for metadata
		tablemeta = doc.createInstance("com.sun.star.text.TextTable")
		# with 2 columns and as many rows as there are metadata items (+1 for titles)
		tablemeta.initialize(len(metaset)+1, 2)
		text.insertTextContent( cursor, tablemeta, 0)
		rows = tablemeta.Rows
		
		tablemeta.setPropertyValue( "BackTransparent", uno.Bool(0) )
		tablemeta.setPropertyValue( "BackColor", 13421823 )
		row = rows.getByIndex(0)
		row.setPropertyValue( "BackTransparent", uno.Bool(0) )
		row.setPropertyValue( "BackColor", 6710932 )
		textColor = 16777215
	
		self.insertTextIntoCell( tablemeta, "A1", "Metadata", textColor )
		self.insertTextIntoCell( tablemeta, "B1", "Content", textColor )
		
		#add text from each metadata item into the created table 'tablemeta'
		i = 1
		for m in metaset:
			i +=1
			tablemeta.getCellByName("A"+str(i)).setString(m.attrib.values()[0])
			tablemeta.getCellByName("B"+str(i)).setString(str(m.text))
	
			
		text.insertString( cursor, "\n\n\n", 0)
		
		phrases = self.i_text.findPhrases()
		i = 1
		for p in phrases:
			cursor.setPropertyValue( "CharShadowed", uno.Bool(1) )
			if (self.i_text.getGloss(p) != None):
				text.insertString( cursor, str(i)+". "+self.i_text.getGloss(p)+"\n", 0)
			cursor.setPropertyValue( "CharShadowed", uno.Bool(0) )
			i+=1
			words = self.i_text.findWords(p)
			phrasetext = ''
			phrasegloss = ''
			for w in words:
				wordtext = ''
				wordgloss = ''
				morphs = self.i_text.findMorphs(w)
				txts, glosses, separators = self.i_text.getMorphParts(morphs)
				morphset = [txts, glosses, separators]
				j = 0	
				for m in morphs:
					if (j!=0) and (len(separators[j])>0):
						wordtext = wordtext + separators[j]
						wordgloss = wordgloss + separators[j]
					if (myUno.i_text.getText(m) != None):
						wordtext = wordtext + self.i_text.getText(m)
					if (myUno.i_text.getGloss(m) != None):
						wordgloss = wordgloss + self.i_text.getGloss(m)
					if (j==0) and (len(separators[j])>0):
						wordtext = wordtext + separators[j]
						wordgloss= wordgloss + separators[j]
					j += 1
				phrasetext = phrasetext + wordtext+"\t"
				phrasegloss = phrasegloss + wordgloss+"\t"
			
				
			text.insertString( cursor, phrasetext + "\n", 0)
			text.insertString( cursor, phrasegloss + "\n", 0)
			text.insertString( cursor, "\n\n", 0)
			



'''


	
###
#trying to debug OOo python: functions that should be in UnoInterlinear
##
def insertTextIntoCell( table, cellName, text, color ):
	tableText = table.getCellByName( cellName )
	cursor = tableText.createTextCursor()
	cursor.setPropertyValue( "CharColor", color )
	tableText.setString( text )


def testET(text, cursor):
	elem = ET.Element("tag", first="1", second="2")
	text.insertString(cursor, str(elem.attrib.get("first"))+"\n\n\n", 0)
	
	
def createTables():
	"""creates a new writer document and inserts a table with some data (also known as the SWriter sample)""" 
	ctx = uno.getComponentContext()
	smgr = ctx.ServiceManager
	desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
	
	# open a writer document
	doc = desktop.loadComponentFromURL( "private:factory/swriter","_blank", 0, () )
	
	text = doc.Text
	cursor = text.createTextCursor()
	
	# write paths in sys.path
#	for x in sys.path:
#		text.insertString( cursor, str(x)+"\n", 0)
#	text.insertString(cursor, str(sys.version)+"\n\n", 0)
	
	# test functions
	# testET(text, cursor)
	
	#create InterlinearText object
	args = '-vpx'
	myTree = ETtheInterlinear.makeIGT('/Users/midnight/Work/pangloss/testingsvn/boktu-short.xml', '/Users/midnight/Work/pangloss/testingsvn/outputsample.xml', args)
	#makeODF(myTree, '/Users/midnight/Work/pangloss/testingsvn/testoutput.odt', args)
	
	#create UnoInterlinear object
	myUno = UnoInterlinear(args)
	myUno.setTree(myTree)
	
	#print metadata
	metaset = myUno.i_text.findMetadata()
	
	# create table for metadata
	tablemeta = doc.createInstance("com.sun.star.text.TextTable")
	# with 2 columns and as many rows as there are metadata items (+1 for titles)
	tablemeta.initialize(len(metaset)+1, 2)
	text.insertTextContent( cursor, tablemeta, 0)
	rows = tablemeta.Rows
	
	tablemeta.setPropertyValue( "BackTransparent", uno.Bool(0) )
	tablemeta.setPropertyValue( "BackColor", 13421823 )
	row = rows.getByIndex(0)
	row.setPropertyValue( "BackTransparent", uno.Bool(0) )
	row.setPropertyValue( "BackColor", 6710932 )
	textColor = 16777215

	insertTextIntoCell( tablemeta, "A1", "Metadata", textColor )
	insertTextIntoCell( tablemeta, "B1", "Content", textColor )
	
	#add text from each metadata item into the created table 'tablemeta'
	i = 1
	for m in metaset:
		i +=1
		tablemeta.getCellByName("A"+str(i)).setString(m.attrib.values()[0])
		tablemeta.getCellByName("B"+str(i)).setString(str(m.text))

		
	text.insertString( cursor, "\n\n\n", 0)
	
	phrases = myUno.i_text.findPhrases()
	i = 1
	for p in phrases:
		cursor.setPropertyValue( "CharShadowed", uno.Bool(1) )
		if (myUno.i_text.getGloss(p) != None):
			text.insertString( cursor, str(i)+". "+myUno.i_text.getGloss(p)+"\n", 0)
		cursor.setPropertyValue( "CharShadowed", uno.Bool(0) )
		i+=1
		words = myUno.i_text.findWords(p)
		phrasetext = ''
		phrasegloss = ''
		for w in words:
			wordtext = ''
			wordgloss = ''
			morphs = myUno.i_text.findMorphs(w)
			txts, glosses, separators = myUno.i_text.getMorphParts(morphs)
			morphset = [txts, glosses, separators]
			j = 0	
			for m in morphs:
				if (j!=0) and (len(separators[j])>0):
					wordtext = wordtext + separators[j]
					wordgloss = wordgloss + separators[j]
				if (myUno.i_text.getText(m) != None):
					wordtext = wordtext + myUno.i_text.getText(m)
				if (myUno.i_text.getGloss(m) != None):
					wordgloss = wordgloss + myUno.i_text.getGloss(m)
				if (j==0) and (len(separators[j])>0):
					wordtext = wordtext + separators[j]
					wordgloss= wordgloss + separators[j]
				j += 1
			phrasetext = phrasetext + wordtext+"\t"
			phrasegloss = phrasegloss + wordgloss+"\t"
		
			
		text.insertString( cursor, phrasetext + "\n", 0)
		text.insertString( cursor, phrasegloss + "\n", 0)
		text.insertString( cursor, "\n\n", 0)

###End inserted debug functions    
    
    

		
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
	interlinear_text = ETtheInterlinear.InterlinearText()
	interlinear_text = interlinear_text.fillTree(input_file, args)

	if args.count('q') ==0:
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
	tree4 = ETtheInterlinear.InterlinearText()
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
		
	ODF_this = ETtheInterlinear.ODFMaker()
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
	myTree = ETtheInterlinear.makeIGT(input_file, "sample.xml", args)
	
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
	ETtheInterlinear.makeODF(myTree, output_file, args)
	
	if args.count('q')==0:
		print "Now exiting the demonstration of ETtheInterlinear"
		print "-"*20
	print
	sys.exit(0)


	
	
def silentETDemo(input_file=None, output_file=None, args = None):
	#arguments:
	#input_file (name for input IGT file)
	#output_file (name for output ODF file)
	#args (arguments passed from command-line, or others)
	#
	#demonstrates some of the basic capabilities of the program
	
#testing the building capabilities of the program
#	
	args = '-vpx'
	myTree = ETtheInterlinear.makeIGT('/Users/midnight/Work/pangloss/testingsvn/boktu-short.xml', '/Users/midnight/Work/pangloss/testingsvn/outputsample.xml', args)
	ETtheInterlinear.makeODF(myTree, '/Users/midnight/Work/pangloss/testingsvn/testoutput.odt', args)

	
def runETIwithUNO(input_file=None, output_file=None, args = None):
	#arguments:
	#input_file (name for input IGT file)
	#output_file (name for output ODF file)
	#args (arguments passed from command-line, or others)
	#
	#runs a basic demo of the ETIwithUno capabilities, using file
	#/Users/midnight/Work/pangloss/testingsvn/boktu-short.xml
	#as input
	
	if (input_file == None or input_file== ''):
		input_file = '/Users/midnight/Work/pangloss/testingsvn/boktu-short.xml'
	if (output_file == None or output_file == ''):
		output_file = '/Users/midnight/Work/pangloss/testingsvn/outputsample.xml'
	if (args == None or args == ''):
		args = '-vpx'
	myTree = ETtheInterlinear.makeIGT(input_file, output_file, args)
	#makeODF(myTree, '/Users/midnight/Work/pangloss/testingsvn/testoutput.odt', args)
	myUno = UnoInterlinear(args)
	myUno.setTree(myTree)
#	myUno.writeAll()
	createTables() 
	
	
	
	

#### run main program
if __name__ == '__main__':

	sys.exit(0)



#junk in the attic: clear this if you don't need it anymore
#otherwise, use for reference or usage tips


#put this in the first line of the program if you need to---
# This Python file uses the following encoding: utf-8

g_exportedScripts = silentETDemo, runETIwithUNO, createTables,
