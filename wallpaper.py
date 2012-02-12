#!/usr/bin/env python
"""
Switch Wallpaper Randomly

Reads the ~/.gnome2/backgrounds.xml file to allow user management
of wallpaper configs under Gnome's Appearance Preferences dialog.
"""

from xml.etree.ElementTree import ElementTree
import gconf
import random
import os.path

GNOME_WALLPAPER_FILE = '~/.gnome2/backgrounds.xml'

# Data Structures
# =================================

class Wallpaper(object):
	"""
	Wallpaper class represents a single wallpaper's data:
		* filename is the name of the file
		* options is the zooming algorithm

		(there are other keys, but I don't care about setting
		  or switching to flat color backgrounds.)

	Subclasses handle instantiation from XML or Gconf directly.

	Relevant gconf keys are in:
		/desktop/gnome/background

	The XML backgrounds config is in:
		~/.gnome2/backgrounds.xml
	"""

	FILENAME_KEY = '/desktop/gnome/background/picture_filename'
	OPTIONS_KEY = '/desktop/gnome/background/picture_options'

	def __init__(filename=None, options=None):
		self.filename = filename
		self.options = options

	def __repr__(self):
		return "<Wallpaper>"

	def __str__(self):
		return "wallpaper [%s, %s]" % (self.filename, self.options)

	def switchTo(self):
		"""
		Set as the current wallpaper.
		Sends the data to the GConf server. 
		"""
		client = gconf.client_get_default()
		client.set_string(Wallpaper.FILENAME_KEY, self.filename)
		client.set_string(Wallpaper.OPTIONS_KEY, self.options)

class XmlWallpaper(Wallpaper):
	"""
	Subclass to init from XML.
	Uses the ElementTree API.
	"""
	def __init__(self, xmlElement):
		self.name = xmlElement.find('name').text
		self.filename = xmlElement.find('filename').text
		self.options = xmlElement.find('options').text

class CurrentWallpaper(Wallpaper):
	"""
	Subclass to init from Gconf.
	Always initializes as the 'current' user wallpaper. 
	"""
	def __init__(self):
		client = gconf.client_get_default()
		self.filename = client.get_string(Wallpaper.FILENAME_KEY)
		self.options = client.get_string(Wallpaper.OPTIONS_KEY)

# Procedures
# =================================

def getXmlWallpapers(filename=None):
	"""
	Get a list of wallpaper objects parsed from the available 
	wallpapers in ~/.gnome2/background.xml. 
	"""
	def openXmlFile(filename):
		doc = ElementTree(file=filename)
		return doc

	if not filename:
		filename = os.path.expanduser(GNOME_WALLPAPER_FILE)
	
	doc = openXmlFile(filename)

	wallpapers = []
	for e in doc.findall('wallpaper'):
		if e.attrib['deleted'] in [True, 'true']:
			continue
		if e.find('filename').text in ['', '(none)']:
			continue

		wall = XmlWallpaper(e)
		wallpapers.append(wall)

	return wallpapers

def setRandomWallpaper(wallpapers=None):
	"""
	Set a random wallpaper from the list available wallpapers. (ie, 
	perhaps we want to manually filter it!)
	If no wallpapers are set, the wallpapers are selected from the
	gnome config file.
	"""
	if not wallpapers:
		wallpapers = getXmlWallpapers()

	# Set random wallpaper as the current one
	# TODO: Don't allow current wallpaper in selection.
	print "Selecting random wallpaper from %d choices." % len(wallpapers)
	random.choice(wallpapers).switchTo()

def main():
	setRandomWallpaper()

if __name__ == '__main__':
	main()
