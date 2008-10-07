#ETIfront.py 
#current version: 0.04
#
#Works with the Pangloss test program ETIwithUno.py
#This set of macros, all programs and extensions are currently under development. Use at your own risk.
#
#Purposes of application: 
#test macro for creating interlinear glossed texts within OpenOffice.org
#
#
# usage: (must be used as a macro within OpenOffice.org)
#g_exportedScripts = createParagraphs, createTables,
#
#author: Jeremy Fahringer
#for Rosetta Project, Pangloss
#(restricted access documentation at http://wiki.rosettaproject.org/PanglossDoc)
#(restricted access project information at http://wiki.rosettaproject.org/Pangloss)

import os, sys
from eti import ETIwithUno as Emu
# from eti import ETtheInterlinear as ETI


import uno
import unohelper
# a UNO struct later needed to create a document
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
from com.sun.star.text.TextContentAnchorType import AS_CHARACTER
from com.sun.star.awt import Size
from com.sun.star.lang import XMain
from com.sun.star.awt import XActionListener
from com.sun.star.awt import XTextListener
from com.sun.star.awt import XItemListener
from com.sun.star.awt import XWindowListener
from com.sun.star.awt import XMouseListener
from com.sun.star.awt import FontDescriptor


#ETI constants:
input_igt_file = '/Users/midnight/Work/pangloss/testingsvn/boktu-short.xml'
output_igt_file = '/Users/midnight/Work/pangloss/testingsvn/archivaloutput.xml'
ETIwUno_object = None

#These constants need to be updated, delete those not in use.
## implemented from dummy listener code by Jluna. http://www.oooforum.org/forum/viewtopic.phtml?t=68328

#Window Constants
# specifies that the window is initially visible.
com_sun_star_awt_WindowAttribute_SHOW        = uno.getConstantByName( "com.sun.star.awt.WindowAttribute.SHOW" )
# specifies that the window fills the complete desktop area.
com_sun_star_awt_WindowAttribute_FULLSIZE    = uno.getConstantByName( "com.sun.star.awt.WindowAttribute.FULLSIZE" )
com_sun_star_awt_WindowAttribute_OPTIMUMSIZE = uno.getConstantByName( "com.sun.star.awt.WindowAttribute.OPTIMUMSIZE" )
com_sun_star_awt_WindowAttribute_MINSIZE     = uno.getConstantByName( "com.sun.star.awt.WindowAttribute.MINSIZE" )
# specifies that the window has visible borders.
com_sun_star_awt_WindowAttribute_BORDER      = uno.getConstantByName( "com.sun.star.awt.WindowAttribute.BORDER" )
# specifies that the size of the window can be changed by the user.
com_sun_star_awt_WindowAttribute_SIZEABLE    = uno.getConstantByName( "com.sun.star.awt.WindowAttribute.SIZEABLE" )
# specifies that the window can be moved by the user.
com_sun_star_awt_WindowAttribute_MOVEABLE    = uno.getConstantByName( "com.sun.star.awt.WindowAttribute.MOVEABLE" )
# specifies that the window can be closed by the user.
com_sun_star_awt_WindowAttribute_CLOSEABLE   = uno.getConstantByName( "com.sun.star.awt.WindowAttribute.CLOSEABLE" )
#[ DEPRECATED ] specifies that the window should support the XSystemDependentWindowPeer interface.
com_sun_star_awt_WindowAttribute_SYSTEMDEPENDENT = uno.getConstantByName( "com.sun.star.awt.WindowAttribute.SYSTEMDEPENDENT" )

#Other Required Constants
com_sun_star_awt_possize = uno.getConstantByName( "com.sun.star.awt.PosSize.POSSIZE" )
com_sun_star_awt_InvalidateStyle_Update = uno.getConstantByName( "com.sun.star.awt.InvalidateStyle.UPDATE" )


## Parts implemented from dummy listener code by Jluna. http://www.oooforum.org/forum/viewtopic.phtml?t=68328
## Listener objects

#Dummy listener that's useful as a template when creating a listener
class MyActionListener( unohelper.Base, XActionListener ):
	def __init__(self, text, cursor ):
		self.text = text
		self.cursor = cursor
	def actionPerformed(self, actionEvent):
		self.text.insertString( self.cursor, "action performed\n", 0 )

class FileListener( unohelper.Base, XTextListener ):
	def __init__(self, window, file_control, var_name, text, cursor ):
		self.text = text
		self.cursor = cursor
		self.window = window
		self.file_control = file_control
		self.var_name = var_name
#		self.index_list = list()
#		if var_name.count('input')!=0:
#			input_igt_file = file_control.getText()
#		elif var_name.count('output')!=0:
#			output_igt_file = file_control.getText()

	def textChanged(self, textEvent):
		# inserList is the list of strings that are to be inserted.
		# Each element in the ListBox Control has a corresponding element in the insert_items
		global insert_items   
		insert_items = list()
		file_path = self.file_control.getText()
		if os.path.isfile(file_path):   
			#A file has been selected, load the index into the list box and populate the insert_items
		#	self.text.insertString( self.cursor, file_path, 0 )
			if self.var_name.count('input')!=0:
				global input_igt_file
				input_igt_file = file_path
				self.text.insertString( self.cursor, "\nInput file: "+file_path, 0 )
			elif self.var_name.count('output')!=0:
				global output_igt_file
				output_igt_file = file_path
				self.text.insertString( self.cursor, "\nOutput file: "+file_path, 0 )
	#		file = open(file_path)
	#		index = file.readlines()
	#		for item in index:
	#			tmp = item.split('\t')
	#			self.index_list.append(tmp[0] + ' - ' + tmp[1])
	#			insert_items.append(tmp[2])
	#	self.list_control.addItems(tuple(self.index_list), 0)
		#Refresh the window
		self.window.invalidate(com_sun_star_awt_InvalidateStyle_Update)
		
class WindowListener( unohelper.Base, XWindowListener ):
	def __init__(self, window, fixed_text_control, insert_button_control, text, cursor ):
		self.text = text
		self.cursor = cursor
		self.window = window
		self.fixed_text_control = fixed_text_control
		self.insert_button_control = insert_button_control
	def windowResized(self, actionEvent):
		#Resize the various controls when the window is resized.
		#    Note: It would be much cleaner to use constants for the different control sizes.
		rect = self.window.getPosSize()
		self.fixed_text_control.setPosSize(1,66,(rect.Width - 2),28,com_sun_star_awt_possize)
#		self.list_control.setPosSize(1,68,(rect.Width - 2),(rect.Height - 105),com_sun_star_awt_possize)
#		self.insert_button_control.setPosSize( (rect.Width/2) - 30 ,(rect.Height - 35),100,30,com_sun_star_awt_possize)
		#Refresh the window
		self.window.invalidate(com_sun_star_awt_InvalidateStyle_Update)

class InsertButtonListener( unohelper.Base, XActionListener ):
	def __init__(self, desktop ):
		self.desktop = desktop
	def actionPerformed(self, actionEvent):
#		global insert_items
#		pos = self.list_control.getSelectedItemPos()
#		text = (insert_items[pos]).strip("\n")
		
		text = "TESTTEST InsertButtonListener"

		myUno = createTables()
		
		if myUno != None:
			global ETIwUno_object
			ETIwUno_object = myUno
			text = "MyUno isn't None"
			if myUno.i_text.shortname != None:
				text = "TEST SHORT "+ myUno.i_text.shortname
			elif myUno.i_text.shortname == None and myUno.i_text.filename !=None:
				text = "TESTTEST "+myUno.i_text.filename
			
			
		#Get the view cursor.  This is the user's visible cursor in the document.
		desktop_model = self.desktop.getCurrentComponent()
		desktop_controller = desktop_model.getCurrentController()
		text_view_cursor = desktop_controller.getViewCursor()
	       
		#Check to see if view cursor is in a table cell.  Use appropriate method to insert text.
		if text_view_cursor.Cell != None:
			text_view_cursor.Cell.insertString(text_view_cursor.getEnd(), text, True)
		else:
			text_view_cursor.setString(text)
			text_view_cursor.goRight(len(text), False)
	
#		self.list_control.selectItemPos(pos + 1, True)

class CheckButtonListener( unohelper.Base, XActionListener ):
	def __init__(self, fixed_text_control, text, cursor ):
		self.text = text
		self.cursor = cursor
		self.fixed_text_control = fixed_text_control
	def actionPerformed(self, actionEvent):
		global ETIwUno_object
		if ETIwUno_object != None:
			self.text.insertString( self.cursor, "The ETIwUno_object is still alive. \n", 0 )
		#	self.fixed_text_control.Text = ETIwUno_object.i_text.filename

# Handy function provided by hanya (from the OOo forums) to create a control, model.
def createControl(smgr,ctx,type,x,y,width,height,names,values):
	   ctrl = smgr.createInstanceWithContext( "com.sun.star.awt.UnoControl%s" % type,ctx)
	   ctrl_model = smgr.createInstanceWithContext( "com.sun.star.awt.UnoControl%sModel" % type,ctx)
	   ctrl_model.setPropertyValues(names,values)
	   ctrl.setModel(ctrl_model)
	   ctrl.setPosSize(x,y,width,height,com_sun_star_awt_possize)
	   return (ctrl, ctrl_model)
	   
 # 'translated' from the developer's guide chapter 11.6
def createWindow():
	"""Opens a dialog with a push button and a label, clicking the button increases the label counter."""
	
	
	#Note: There are generally two ways to run a python program that integrates with OOo.  The first is to start
	#openoffice so that it is listening on a port, like so:
	#    ./soffice "-accept=socket,host=localhost,port=2002;urp;"&
	# You could then launch your python program, like so:
	#    "/cygdrive/c/Program Files/OpenOffice.org 2.3/program/python.bat" testing2.py
	#This method is preferred when doing development, since it is much easier to debug problems.
	#When development is complete, it can be launched as a macro.  This script assumes that you are launching it
	#as a macro from inside of OOo. If you want to connect via a socket, you will have to get the context by
	#uncommenting the lines below:
	
	## get the uno component context from the PyUNO runtime
	#local_context = uno.getComponentContext()
	## create the UnoUrlResolver
	#resolver = local_context.ServiceManager.createInstanceWithContext(
	#        "com.sun.star.bridge.UnoUrlResolver", local_context )
	#ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
	##Also note that at the end of this script you will have to force the script to sleep if you want listeners to work.

	#Comment this out if you are connecting to OOo via  socket.
	ctx = uno.getComponentContext()
	
	smgr = ctx.ServiceManager
	toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx);
	
	desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
	# access the current writer document
	model = desktop.getCurrentComponent()
	
	#Get model text and create cursor for debugging purposes.
	#  Note: This isn't the view cursor, it's a second cursor that's not visible on the screen.
	text = model.Text
	cursor = text.createTextCursor()
	# An example of how to insert text with the new cursor:
	#text.insertString( cursor, "Inserting this text...\n", 0 )
	
	oCoreReflection = smgr.createInstanceWithContext( "com.sun.star.reflection.CoreReflection", ctx )
	
	#Create Uno Struct
	oXIdlClass = oCoreReflection.forName( "com.sun.star.awt.WindowDescriptor" )
	oReturnValue, oWindowDesc = oXIdlClass.createObject( None )
	
	oWindowDesc.Type = uno.getConstantByName( "com.sun.star.awt.WindowClass.TOP" )
	oWindowDesc.WindowServiceName = ""
	oWindowDesc.Parent = toolkit.getDesktopWindow()
	oWindowDesc.ParentIndex = -1
	
	#Set Window Attributes
	gnDefaultWindowAttributes = \
		com_sun_star_awt_WindowAttribute_SHOW + \
		com_sun_star_awt_WindowAttribute_BORDER + \
		com_sun_star_awt_WindowAttribute_MOVEABLE + \
		com_sun_star_awt_WindowAttribute_CLOSEABLE 	# + \
#		com_sun_star_awt_WindowAttribute_SIZEABLE
		
	#Create Bounding Rectangle
	oXIdlClass = oCoreReflection.forName( "com.sun.star.awt.Rectangle" )
	oReturnValue, oRect = oXIdlClass.createObject( None )
	oRect.X = 100
	oRect.Y = 200
	oRect.Width = 402
	oRect.Height = 180

	oWindowDesc.Bounds = oRect
   
	# specify the window attributes.
	oWindowDesc.WindowAttributes = gnDefaultWindowAttributes
	#create window
	oWindow = toolkit.createWindow(oWindowDesc)

	
	#create frame for window
	oFrame = smgr.createInstanceWithContext( "com.sun.star.frame.Frame", ctx )
	oFrame.initialize( oWindow )
	oFrame.setCreator( desktop )
	oFrame.activate()
	oFrame.Title = "Pangloss"
	

	# create new control container
	cont = smgr.createInstanceWithContext(
		"com.sun.star.awt.UnoControlContainer",ctx)
	cont_model = smgr.createInstanceWithContext(
		"com.sun.star.awt.UnoControlContainerModel",ctx)
	cont_model.BackgroundColor = -1
	cont.setModel(cont_model)
	# need createPeer just only the container
	cont.createPeer(toolkit,oWindow)
	cont.setPosSize(0,0,500,400,com_sun_star_awt_possize)
	
	oFrame.setComponent(cont,None)
   
	#Create controls
	#    Note: The dimensions for the controls should probably be constants for easy changes in the future. Oh well.
	
	#File Control
	file_control, file_model = createControl(
					smgr,ctx,"FileControl",1,1,400,32,
					("Label",),
					("file_control",) )
	file_model.Text = "Select an input file: "
	file_control.setEditable(False);  #Doesn't seem to do anything
	

	#Archival File Control
	arch_file_control, arch_file_model = createControl(
					smgr,ctx,"FileControl",1,34,400,32,
					("Label",),
					("arch_file_control",) )
					
	arch_file_model.Text = "Select an archival output file: "
	arch_file_control.setEditable(False);  #Doesn't seem to do anything
	
	
	#Fixed Text Control
	fixed_text_control, fixed_text_model = createControl(
						smgr,ctx,"FixedText", 5,66, 200,28,
						('Name','Label'),('current_item_label','Current element (eventually)...') )
	#Create font descriptor for fixed text
	font_descriptor = FontDescriptor()
	font_descriptor.Name = 'Verdana'
	font_descriptor.Height = 12
	font_descriptor.Width = 6
	font_descriptor.Weight = 100
	font_descriptor.Kerning = True
	fixed_text_model.FontDescriptor = font_descriptor


	#Insert Button Control
	insert_button_control, insert_button_model = createControl(
		smgr,ctx,"Button",120,100,100,30,
		('Label',),('Create IGT',) )
	#Check Button Control
	check_button_control, check_button_model = createControl(
		smgr,ctx,"Button",120,140,100,30,
		('Label',),('Check IGT',) )

	#Add Listeners To Controls
	file_control.addTextListener( FileListener(oWindow, file_control, "input_igt_file", text, cursor) )
	arch_file_control.addTextListener( FileListener(oWindow, arch_file_control, "output_igt_file", text, cursor) )
#	list_control.addItemListener( ListItemListener(oWindow, list_control, fixed_text_model, text, cursor) )   
	insert_button_control.addActionListener( InsertButtonListener( desktop) )
	check_button_control.addActionListener( CheckButtonListener( fixed_text_control, text, cursor) )
	oWindow.addWindowListener( WindowListener(oWindow, fixed_text_control, insert_button_control, text, cursor) )

	# add controls to the container
	cont.addControl("file_control",file_control)
	cont.addControl("arch_file_control",arch_file_control)
#	cont.addControl("list_control",list_control)
	cont.addControl("fixed_text_control",fixed_text_control)
	cont.addControl("insert_button_control", insert_button_control)
	cont.addControl("check_button_control", check_button_control)
	#self.cont = cont
	#edit_ref.setFocus()
	#self.addlisteners()
		
	oWindow.setVisible(True)

	#Important: If you want to have this script connect over a socket, you must force the script to sleep for listeners to work.
	#They will only work as long as the script sleeps.
	#time.sleep(100)
	




   
###
#please clean up all of this code, make as much of it as possible part of the UnoInterlinear class within EmuwithUno
##

def insertTextIntoCell( table, cellName, text, color ):
	tableText = table.getCellByName( cellName )
	cursor = tableText.createTextCursor()
	cursor.setPropertyValue( "CharColor", color )
	tableText.setString( text )


def createParagraphs():
	"""creates a new writer document and inserts a table with some data (also known as the SWriter sample)""" 
	ctx = uno.getComponentContext()
	smgr = ctx.ServiceManager
	desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
	
	# open a writer document
	doc = desktop.loadComponentFromURL( "private:factory/swriter","_blank", 0, () )
	
	text = doc.Text
	cursor = text.createTextCursor()
	

	# test functions
	# testET(text, cursor)
	
	#create InterlinearText object
	args = '-vpx'
	myTree = Emu.makeIGT(input_igt_file, output_igt_file, args)
	#makeODF(myTree, '/Users/midnight/Work/pangloss/testingsvn/testoutput.odt', args)
	
	#create UnoInterlinear object
	myUno = Emu.UnoInterlinear(args)
	myUno.setTree(myTree)
	
	#get metadata
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
		


#
#feeder functions for createTables, should all end up in ETIwithUno somewhere if at all possible (public vs. private implications)
#

def fillMetadata(interlinear_text, doc, text, cursor):
	# arguments: 
	# interlinear_text (InterlinearText object that is being parsed to the ODF doc)
	# doc (writer document, from loadComponentFromURL)
	# text (text of document (doc.Text))
	# cursor (text cursor from createTextCursor)
	
				
	#get metadata
	metaset = interlinear_text.findMetadata()
	
	if metaset != None:
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
		
	return cursor

def fillTablePhrases(interlinear_text, doc, text, cursor):
	# arguments: 
	# interlinear_text (InterlinearText object that is being parsed to the ODF doc)
	# doc (writer document, from loadComponentFromURL)
	# text (text of document (doc.Text))
	# cursor (text cursor from createTextCursor)
	
	#get phrases
	phrases = interlinear_text.findPhrases()
	
	alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	pnum = 0 
	
	if phrases != None:
		for p in phrases:
			pnum +=1
			words = interlinear_text.findWords(p)
			# create table for phrases
			phrasetable = doc.createInstance("com.sun.star.text.TextTable")
			# with 1 row and as many columns as there are words in the phrase
			phrasetable.initialize(3, len(words))
			text.insertTextContent(cursor, phrasetable, 0)
			rows = phrasetable.Rows
			
			phrasetable.setPropertyValue( "BackTransparent", uno.Bool(1) )
			row = rows.getByIndex(0)
#			row.setPropertyValue( "BackTransparent", uno.Bool(0) )
#			row.setPropertyValue( "BackColor", 6710932 )
		#	textColor = 16777215
		
			
			tablecursor = phrasetable.createCursorByCellName("A1")
			
			tablecursor.goRight(len(words)-1, 1)
			tablecursor.mergeRange()
			
			if (interlinear_text.getGloss(p) != None):
				phrasetable.getCellByName("A1").setString( str(pnum)+". "+interlinear_text.getGloss(p))
				tablecursor = phrasetable.createCursorByCellName("A1")
				tablecursor.setPropertyValue( "CharShadowed", uno.Bool(1) )
				
			#add text from each word into the created table 'phrasetable'
			i = 0
			for w in words:

				wordtext = ''
				wordgloss = ''
				morphs = interlinear_text.findMorphs(w)
				txts, glosses, separators = interlinear_text.getMorphParts(morphs)
				morphset = [txts, glosses, separators]
				j = 0	
				for m in morphs:
					if (j!=0) and (len(separators[j])>0):
						wordtext = wordtext + separators[j]
						wordgloss = wordgloss + separators[j]
					if (interlinear_text.getText(m) != None):
						wordtext = wordtext + interlinear_text.getText(m)
					if (interlinear_text.getGloss(m) != None):
						wordgloss = wordgloss + interlinear_text.getGloss(m)
					if (j==0) and (len(separators[j])>0):
						wordtext = wordtext + separators[j]
						wordgloss= wordgloss + separators[j]
					j += 1
				
				#phrasetable.getCellByName(alphabet[i]+"1").setString('word'+str(i))
				#phrasetable.getCellByName(alphabet[i]+"1").setString(wordtext+"\n"+wordgloss)
				
				phrasetable.getCellByPosition(i, 1).setString(wordtext)
				phrasetable.getCellByPosition(i, 2).setString(wordgloss)
				
				i +=1
				
			text.insertString( cursor, "\n\n\n", 0)

		
		
	return cursor

	
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
	myTree = Emu.makeIGT(input_igt_file, output_igt_file, args)
	#makeODF(myTree, '/Users/midnight/Work/pangloss/testingsvn/testoutput.odt', args)
	
	#create UnoInterlinear object
	myUno = Emu.UnoInterlinear(args)
	myUno.setTree(myTree)
	
	cursor = fillMetadata(myUno.i_text, doc, text, cursor)
	
	cursor = fillTablePhrases(myUno.i_text, doc, text, cursor)
	
	global ETIwUno_object
	ETIwUno_object = myUno
	
	return myUno


###
    
g_exportedScripts =  createTables, createWindow,  		#createParagraphs,
