import appuifw, e32, thread, btsocket

# Only for local tests
#import sys
#sys.path.append('E:\\download\\libs\\')

import ftpserver

class sypftp(object):
  def __init__(self):
    # Set look and feel
    appuifw.app.title = u"sypFTP"
    appuifw.app.menu = [
      (u"Run server", self.fakeBind),
      (u"Options",    self.fakeBind),
      (u"About",      self.fakeBind),
      (u"Exit",       self.exit)
    ]
    appuifw.app.body = None
    
    # Bind "Exit" key
    appuifw.app.exit_key_handler = self.exit
    
    # Start up network
    self.networking()
    
    # ftpserver init
    if self.network:
      self.ftp_server_deamon()
    
    # Lock and load (wait)
    self.app_lock = e32.Ao_lock()
    self.app_lock.wait()
  
  def fakeBind(self):
    self.log('Bind!')
  
  def log(self, text):
    if text:
      print u"%s" % (text)
  
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
    self.ftp_authorizer   = ftpserver.DummyAuthorizer()
    self.ftp_handler      = ftpserver.FTPHandler
    
    # Just for now, while everything is breaking ...
    self.ftp_authorizer.add_user('user', '12345', "E:\\", perm='elradfmw')
    
    self.ftp_handler.authorizer = self.ftp_authorizer
    self.ftp_handler.banner     = "sypFTP"
    
    self.ftp_address = (self.apo.ip(), 121)
    self.ftpd = ftpserver.FTPServer(self.ftp_address, self.ftp_handler)
    
    self.ftpd.max_cons = 256
    self.ftpd.max_cons_per_ip = 5
    
    self.ftpd.serve_forever()
  
  def ftp_server_deamon(self):
    self.thread_lock  = thread.allocate_lock()
    self.ftp_thread   = thread.start_new_thread(self.ftp_server_init, ())
   
  def exit(self):
    self.apo.stop()
    self.app_lock.signal()

if __name__ == '__main__':
  sypftp()
