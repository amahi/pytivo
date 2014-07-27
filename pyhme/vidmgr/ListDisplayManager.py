from hme import *

from VideoFile import VideoFile
from VideoDir import VideoDir
from VideoShare import VideoShare
from DVDDir import DVDDir
from DVDShare import DVDShare

from Config import ( listViewSize, listViewWidth, listYStart, listHeight, listXText, listXIcon, listXCue,
				TYPE_VIDFILE, TYPE_VIDDIR, TYPE_VIDSHARE, TYPE_DVDDIR, TYPE_DVDSHARE )

navkeys = [KEY_UP, KEY_DOWN, KEY_CHANNELUP, KEY_CHANNELDOWN, KEY_REPLAY, KEY_ADVANCE,
		KEY_NUM0, KEY_NUM1, KEY_NUM2, KEY_NUM3, KEY_NUM4, KEY_NUM5, KEY_NUM6, KEY_NUM7, KEY_NUM8, KEY_NUM9]		

keymap = { KEY_NUM1: 10.0, KEY_NUM2: 20.0, KEY_NUM3: 30.0, KEY_NUM4: 40.0, KEY_NUM5: 50.0,
		KEY_NUM6: 60.0, KEY_NUM7: 70.0, KEY_NUM8: 80.0, KEY_NUM9: 90.0 }

class ListDisplayManager:
	def __init__(self, app, opts):
		self.app = app
		self.opts = opts
		self.stack = []
		
		self.listOffset = 0
		self.listSelection = 0
		self.node = None
		# now create the listing page (and shares page) views

		self.vwList = View(self.app, width=listViewWidth)
		self.vwListText = []
		self.vwListBkg = []
		self.vwListIcon = []
		self.vwListCue = []
		for i in range(listViewSize):
			yval = listYStart + (i*listHeight)
			bkg = View(self.app, height=listHeight, width=listViewWidth, ypos=yval, parent=self.vwList)
			self.vwListBkg.append(bkg)
			self.vwListText.append(View(self.app, height=listHeight, width=listViewWidth-listXText-10,
									ypos=0, xpos=listXText, parent=bkg))
			self.vwListIcon.append(View(self.app, height=32, width=32, ypos=4, xpos=listXIcon, parent=bkg))
			self.vwListCue.append(View(self.app, height=32, width=32, ypos=4, xpos=listXCue, parent=bkg))
			
		self.vwListCueTop = View(self.app, height=32, width=32, ypos=listYStart-listHeight+3,
								xpos=listXCue, parent=self.vwList)
		self.vwListCueBot = View(self.app, height=32, width=32, ypos=listYStart+listHeight*listViewSize,
								xpos=listXCue, parent=self.vwList)
	def ReInit(self):
		self.stack = []
		self.listOffset = 0
		self.Selection = 0
		self.node = None
		
	def Descend(self, node):
		self.stack.append([self.node, self.listOffset, self.listSelection])
		self.node = node
		self.opts = node.getOpts()
		self.listSize = len(self.node)
		self.listOffset = 0
		self.listSelection = 0
		self.PopulateScreen()
		if self.listSize == 0:
			return self.node, None
		else:
			self.Hilite(0)
			return self.node, self.node.getItem(self.listSelection)
	
	def Ascend(self):
		if len(self.stack) == 0:
			return None, None
		
		self.node, self.listOffset, self.listSelection = self.stack.pop()
		if self.node == None:
			return None, None
		
		self.PopulateScreen()
		self.Hilite(self.listSelection)
		return self.node, self.node.getItem(self.listSelection)

	def PopulateScreen(self):
		self.listSize = len(self.node)
		if (self.listSize == 0):
			for i in range(listViewSize):
				self.vwListBkg[i].clear_resource();
				self.vwListCue[i].clear_resource();
				self.vwListText[i].clear_resource()
				self.vwListIcon[i].clear_resource()
			self.vwListCueTop.clear_resource();
			self.vwListCueBot.clear_resource();
			self.vwListText[3].set_text('No videos in this folder - press LEFT to continue', font=self.app.myfonts.fnt20,
									colornum=0xffffff, flags=RSRC_HALIGN_LEFT);
			self.vwListCue[3].set_resource(self.app.myimages.CueLeft)
		
		else:
			self.vwListCueTop.clear_resource();
			if self.listSelection == 0 and self.listOffset != 0:
				self.vwListCueTop.set_resource(self.app.myimages.CueUp)
				
			self.vwListCueBot.clear_resource();
			if (self.listSelection == listViewSize-1) and (self.listSelection+self.listOffset < self.listSize-1):
				self.vwListCueBot.set_resource(self.app.myimages.CueDown)
			
			for i in range(listViewSize):
				self.vwListBkg[i].clear_resource()
				self.vwListCue[i].clear_resource()
				sx = i + self.listOffset
				if (sx < self.listSize):
					item = self.node.getItem(sx)
					self.vwListText[i].set_text(item.formatDisplayText(self.opts['dispopt']), font=self.app.myfonts.fnt24,
										colornum=0xffffff, flags=RSRC_HALIGN_LEFT)
					icon = self.getIcon(item)
					if icon == None:
						self.vwListIcon[i].clear_resource()
					else:
						self.vwListIcon[i].set_resource(icon)
				else:
					self.vwListText[i].clear_resource()
					self.vwListIcon[i].clear_resource()
					
	def getIcon(self, item):
		otype = item.getObjType()
		if otype == TYPE_VIDFILE:
			if item.isDVDVideo():
				return self.app.myimages.IconDVDVideo
			else:
				return self.app.myimages.IconVideo
		if otype == TYPE_VIDDIR:
			return self.app.myimages.IconFolder
		if otype == TYPE_VIDSHARE:
			return self.app.myimages.IconFolder
		if otype == TYPE_DVDDIR:
			return self.app.myimages.IconDVDFolder
		if otype == TYPE_DVDSHARE:
			return self.app.myimages.IconDVDFolder

		return None
	
	def Hilite(self, x, on=True):
		if x == self.listOffset and self.listOffset != 0:
			self.vwListCueTop.set_resource(self.app.myimages.CueUp)
		else:
			self.vwListCueTop.clear_resource()
			
		if x == self.listOffset+listViewSize-1 and x < self.listSize-1:
			self.vwListCueBot.set_resource(self.app.myimages.CueDown)
		else:
			self.vwListCueBot.clear_resource()
			
		for i in range(listViewSize):
			self.vwListBkg[i].clear_resource()
			self.vwListCue[i].clear_resource()
			sx = i + self.listOffset
			if on:
				if (sx < self.listSize):
					if sx == x:
						self.vwListBkg[i].set_resource(self.app.myimages.HiLite)
						self.vwListCue[i].set_resource(self.app.myimages.CueLeft)
					elif sx == x-1:
						self.vwListCue[i].set_resource(self.app.myimages.CueUp)
					elif sx == x+1:
						self.vwListCue[i].set_resource(self.app.myimages.CueDown)

	def isNavKey(self, keynum, rawcode):
		return keynum in navkeys
	
	def Verify(self):
		self.listSize = len(self.node)
		if self.listSelection >= self.listSize:
			self.listSelection = self.listSize - 1
			
		if self.listSelection < 0: 
			self.listSelection = 0
			
		if self.listOffset > self.listSelection:
			self.listOffset = self.listSelection
			
		self.PopulateScreen()
		if self.listSize != 0:
			self.Hilite(self.listSelection)
			return self.node.getItem(self.listSelection)
		else:
			return None
			
											
	def Navigate(self, keynum, rawcode):
		self.listSize = len(self.node)
		oldSelection = self.listSelection
		oldOffset = self.listOffset
		
		snd = 'updown'
		if len(self.node) == 0 and keynum not in [ KEY_LEFT, KEY_TIVO ]:
			snd = 'bonk'
		elif keynum == KEY_DOWN:
			if not self.CursorForward(1):
				snd = 'bonk'
					
		elif keynum == KEY_UP:
			if not self.CursorBackward(1):
				snd = 'bonk'
				
		elif keynum == KEY_CHANNELUP:
			if not self.CursorBackward(listViewSize):
				snd = 'bonk'
		
		elif keynum == KEY_CHANNELDOWN:
			if not self.CursorForward(listViewSize):
				snd = 'bonk'
				
		elif keynum in keymap:
			pct = keymap[keynum]
			self.listOffset = int(pct * self.listSize / 100.0)
			self.listSelection = self.listOffset
				
		elif keynum == KEY_REPLAY:
			self.listSelection = 0
			self.listOffset = 0
			
		elif keynum in [ KEY_ADVANCE, KEY_NUM0 ]:
			if self.listSelection == self.listSize - 1:
				self.listSelection = 0
				self.listOffset = 0
			else:
				self.listOffset = self.listSize - listViewSize
				if self.listOffset < 0:
					self.listOffset = 0
				self.listSelection = self.listSize-1
		
		if self.listOffset == oldOffset:
			# screen is still the same - just maybe a different hilite line
			if self.listSelection != oldSelection:
				#remove the hilite from the old
				self.Hilite(oldSelection, False)
				# hilite the new
				self.Hilite(self.listSelection)
		else:
			# everything has changed
			self.PopulateScreen()
			self.Hilite(self.listSelection)

		self.app.sound(snd)
		
		return self.node.getItem(self.listSelection)
	
	def CursorForward(self, lines):
		newSelection = self.listSelection + lines
		if newSelection >= self.listSize:
			newSelection = self.listSize-1
		
		if newSelection == self.listSelection:
			return False
		
		self.listSelection = newSelection
		
		if self.listSelection - self.listOffset >= listViewSize:
			newOffset = self.listOffset + lines
			if newOffset >= self.listSize:
				newOffset = self.listSize-1
			self.listOffset = newOffset
			
		return True
		
	def CursorBackward(self, lines):
		if self.listSelection == 0:
			return False
		
		self.listSelection -= lines
		if self.listSelection < 0:
			self.listSelection = 0
			
		if self.listSelection < self.listOffset:
			self.listOffset -= lines
			if self.listOffset < 0:
				self.listOffset = 0
			
		return True
