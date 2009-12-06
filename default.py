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
      (u"Options",    self.fakeBind),
      (u"About",      self.fakeBind),
      (u"Exit",       self.exit)
    ]
    appuifw.app.body = self.uiConsole
    
    # Bind "Exit" key
    appuifw.app.exit_key_handler = self.exit
    
    # Start up network
    self.networking()
    
    # ftpserver init
    if self.network:
      self.ftp_deamon()
    
    # Lock and load (wait)
    self.app_lock = e32.Ao_lock()
    self.app_lock.wait()
  
  def fakeBind(self):
    self.log('Bind!')
  
  def log(self, text):
    if text:
      self.uiConsole.add(u"%s\n" % (text))
  
  def networking(self):
    
    self.log("Connecting to network ...");
    
    self.apid = btsocket.select_access_point()
    self.apo  = btsocket.access_point(self.apid)
    
    try:
      self.apo.start()
      btsocket.set_default_access_point(self.apo)
      self.network = True
      self.log("done.")
    except:
      slef.network = False
      self.log("failed.")
  
  def ftp_server_init(self):
    self.authorizer   = ftpserver.DummyAuthorizer()
    self.ftp_handler  = ftpserver.FTPHandler
    
    self.authorizer.add_user('user', '12345', "E:\\", perm='elradfmw')
    
    self.ftp_handler.authorizer = self.authorizer
    self.ftp_handler.banner     = "sypFTP"
    
    self.address = (self.apo.ip(), 21)
    self.ftpd = ftpserver.FTPServer(self.address, self.ftp_handler)
    
    self.ftpd.max_cons = 256
    self.ftpd.max_cons_per_ip = 5
    
    self.ftpd.serve_forever()
  
  def ftp_deamon(self):
    self.lock = thread.allocate_lock()
    tid = thread.start_new_thread(self.ftp_server_init, ())
    appuifw.note(u"Thead no " + str(tid) + " is running.", "info")
   
  def exit(self):
    #self.apo.stop()
    self.app_lock.signal()

if __name__ == '__main__':
  sypftp()
  
