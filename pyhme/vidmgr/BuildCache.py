'''
Created on Aug 3, 2011

@author: Jeff
'''
import sys
sys.path.append('..')

from VideoCache import VideoCache
import Config

import getopt

verbose = False

try:
	opts, args = getopt.getopt(sys.argv[1:], "v", ["verbose"])
	for o, a in opts:
		if o == "-v":
			verbose = True
			
except getopt.GetoptError, err:
	print "Ignoring invalid options"

cfg = Config.Config()
opts = cfg.load()
cp = cfg.getConfigParser()

c = VideoCache(opts, cp)
c.build(verbose)
c.save(True)
