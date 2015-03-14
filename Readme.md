# Pangloss Prototype - OpenOffice.org macro and command-line interface #
  * created by the [Rosetta Project](http://www.rosettaproject.org) as part of the [Pangloss Feasibility Study](http://www.rosettaproject.org/about-us/projects/pangloss)

  * author: Jeremy Fahringer
  * created: Jan - July 02008
  * last modified: July 28, 02008

---

This package is distributed under the Creative Commons license. Use at your own risk as it is experimental and not necessarily well-tested (may cause conflicts or lose data, or otherwise damage things).

---

## Project Goals ##
The outputs of this project can be summarized as follows:
  * **Tools:** This project will develop a preliminary version of a “plug-in” for use with OpenOffice.org to facilitate the creation and maintenance of interlinear glossed texts. It will also develop code libraries allowing the interlinear glossed text to be “linked” to entries in a lexical database.
  * **Standards:** This project will develop XML standards for interlinear glossed text which will be suitable for use in the OpenOffice.org environment. It will further develop a standard mechanism within OpenOffice.org to link lexical items in texts to lexical database entries.
  * **Recommendations:** This project will propose recommendations concerning (i) the general problem of adapting pre-existing open-source applications to more narrow academic functions and (ii) the more specific problem of doing this with OpenOffice.org.

## Installation ##
This package contains the programs and macros developed under the Pangloss Feasibility Study. The package may be installed in the user's OpenOffice.org installation. It should reside within the macros/scripting folder within the installation itself, to have access to the !OO.org python installation.

  1. **eti** module must be installed by user into OpenOffice.org python installation (for example, _/Applications/OpenOffice.org\ 2.1.app/Contents/MacOS/program_)
  1. **eti** module contains **xml** module for Core XML support for Python, which includes the **ElementTree** libraries
  1. **ETIfront.py** should be installed into any of the macro locations (e.g. for application-wide usage, _/Applications/OpenOffice.org\ 2.1.app/Contents/MacOS/share/Scripts/python_)

  * **ETu.py** (within **eti** module)  is a command-line user interface that contains most of the proposed first-iteration functionality of the Pangloss suite.