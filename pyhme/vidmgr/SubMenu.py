from hme import *

from Config import screenHeight, screenWidth, submenuheight, submenuwidth, submenulineheight

class SubMenu(View):
	def __init__(self, app, opts):
		xpos = (screenWidth-submenuwidth)/2
		ypos = (screenHeight-submenuheight)/2
		View.__init__(self, app, width=submenuwidth, height=submenuheight, xpos=xpos, ypos=ypos, visible=False)
		self.set_resource(app.myimages.SubMenu)
		self.opts = opts
		self.respkey = None
		self.menuContent = []
		self.menuView = []
		self.menuBkgView = []
		self.linesPerPage = 4
		self.lineCount = 0
		self.displayOffset = 0
		self.currentChoice = 0
		self.resultvalue = None
		self.isactive = False
		self.app = app

		for i in range(self.linesPerPage):
			m = View(self.app, parent=self, width=submenuwidth-20, height=submenulineheight, xpos=10, ypos=(i+1)*(submenulineheight+4))
			self.menuBkgView.append(m)

			m = View(self.app, parent=self, width=submenuwidth-40, height=submenulineheight, xpos=20, ypos=(i+1)*(submenulineheight+4))
			self.menuView.append(m)

		self.vwTitle = View(self.app, parent=self, width=submenuwidth-20, height=submenulineheight, xpos=20, ypos=2)

		self.vwUp = View(self.app, parent=self, width=32, height=16, xpos=30, ypos=36)
		self.vwUp.set_resource(self.app.myimages.InfoUp)
		self.vwDown = View(self.app, parent=self, width=32, height=16, xpos=30, ypos=submenuheight-18)
		self.vwDown.set_resource(self.app.myimages.InfoDown)


	def load(self, title, menu, respkey):
		self.menuContent = []
		self.lineCount = 0
		self.displayOffset = 0
		self.currentChoice = 0
		self.respkey = respkey
		self.resultvalue = None
		for m in menu:
			self.menuContent.append(m)
			self.lineCount += 1

		self.vwTitle.set_text(title, font=self.app.myfonts.fnt24, colornum=0xffffff, flags=RSRC_HALIGN_CENTER)

		self.paint()
		self.isactive = True
		self.set_visible(True)

	def getResult(self):
		return self.resultvalue
		
	def paint(self):
		if self.displayOffset == 0:
			self.vwUp.set_visible(False)
		else:
			self.vwUp.set_visible(True)
			
		if self.displayOffset + self.linesPerPage >= self.lineCount:
			self.vwDown.set_visible(False)
		else:
			self.vwDown.set_visible(True)
			
		for i in range(self.linesPerPage):
			n = self.displayOffset + i
			if n >= self.lineCount:
				self.menuView[i].set_text("")
			else:
				self.menuView[i].set_text(self.menuContent[n],
					font=self.app.myfonts.fnt20,
					colornum=0xffffff,
					flags=RSRC_HALIGN_CENTER)
		self.hilite()
	
	def hilite(self):
		for i in range(self.linesPerPage):
			if i + self.displayOffset == self.currentChoice:
				self.menuBkgView[i].set_resource(self.app.myimages.MenuHiLite)
			else:
				self.menuBkgView[i].clear_resource()

	def handlekeypress(self, keynum, rawcode):
		snd = 'updown'
		if keynum == KEY_DOWN:
			if not self.linedown():
				snd = 'bonk'

		elif keynum == KEY_UP:
			if not self.lineup():
				snd = 'bonk'

		elif keynum == KEY_CHANNELDOWN:
			if not self.pagedown():
				snd = 'bonk'

		elif keynum == KEY_CHANNELUP:
			if not self.pageup():
				snd = 'bonk'

		elif keynum in [ KEY_RIGHT, KEY_SELECT ]:
			self.resultvalue = self.currentChoice
			self.app.send_key(KEY_TIVO, self.respkey)
			self.isactive = False
			self.set_visible(False)

		elif keynum == KEY_LEFT:
			self.resultvalue = -1
			self.app.send_key(KEY_TIVO, self.respkey)
			self.isactive = False
			self.set_visible(False)

		else:
			snd = 'bonk'

		self.app.sound(snd)

	def linedown(self):
		if self.currentChoice >= self.lineCount-1:
			return False
		
		self.currentChoice += 1
		if self.currentChoice-self.displayOffset == self.linesPerPage:
			self.displayOffset += 1
			self.paint()
		else:
			self.hilite()
		return True
	
	def lineup(self):
		if self.currentChoice == 0:
			return False;
		
		self.currentChoice -= 1
		if self.currentChoice < self.displayOffset:
			self.displayOffset = self.currentChoice
			self.paint()
		else:
			self.hilite()

		self.paint()
		return True

	def pagedown(self):
		if self.displayOffset + self.linesPerPage >= self.lineCount:
			return False
		
		self.displayOffset = self.displayOffset + self.linesPerPage
		if self.displayOffset + self.linesPerPage > self.lineCount:
			self.displayOffset = self.lineCount - self.linesPerPage
			
		self.currentChoice = self.currentChoice + self.linesPerPage
		if self.currentChoice >= self.lineCount:
			self.currentChoice = self.lineCount - 1
			
		self.paint()
		return True
	
	def pageup(self):
		if self.displayOffset == 0 and self.currentChoice == 0:
			return False;
		
		self.displayOffset = self.displayOffset - self.linesPerPage
		if self.displayOffset < 0:
			self.displayOffset = 0
			
		self.currentChoice = self.currentChoice - self.linesPerPage
		if self.currentChoice < 0:
			self.currentChoice = 0
			
		self.paint()
		return True
		

