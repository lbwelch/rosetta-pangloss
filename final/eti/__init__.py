"""Interlinear text creation and manipulation with and for OpenOffice.org

This package contains four sub-packages:

	
ETtheInterlinear -- InterlinearText object, OdfMaker object, core functions

ETIwithUno --  InterlinearText object, OdfMaker object, UnoInterlinear object, core functions
	#Will replace ETtheInterlinear temporarily.

ETu -- ETtheInterlinear commandline user interface. Demonstration of API capabilities and usages.

xml -- Core XML support for Python


"""


__all__ = ["ETtheInterlinear", "ETIwithUno", "ETu", "xml"]

# When being checked-out without options, this has the form
# "<dollar>Revision: x.y </dollar>"
# When exported using -kv, it is "x.y".
__version__ = "$Revision: 00012 $".split()[-2:][0]


