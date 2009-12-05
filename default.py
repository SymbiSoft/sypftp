import appuifw, e32, thread, btsocket

# Only for local tests
import sys
sys.path.append('E:\\download\\libs\\')

import ftpserver

class sypftp(object):
	def __init__(self):
		
		self.uiConsole = appuifw.Text()
		
		# Set look and feel
		appuifw.app.title = u"sypFTP"
		appuifw.app.menu = [
			(u"Run server", self.fakeBind),
			(u"Options", 		self.fakeBind),
			(u"About", 			self.fakeBind),
			(u"Exit", 			self.exit)
		]
		appuifw.app.body = self.uiConsole
		
		# Bind "Exit" key
		appuifw.app.exit_key_handler = self.exit
		
		# Start up network
		self.networking()
		
		# Lock and load (wait)
		self.app_lock = e32.Ao_lock()
		self.app_lock.wait()
	
	def fakeBind(self):
		self.uiConsole.add(u"I told you so!")
	
	def log(self, text):
		if text:
			self.uiConsole.add(u"%s\n" % (text))
	
	def networking(self):
		
		self.log("Connecting to network ...");
		
		self.apid = btsocket.select_access_point()
		self.apo 	= btsocket.access_point(self.apid)
		
		try:
			self.apo.start()
			btsocket.set_default_access_point(self.apo)
			self.log("done.")
		except:
			self.log("failed.")
	
	def exit(self):
		#self.apo.stop()
		self.app_lock.signal()

if __name__ == '__main__':
	sypftp()
