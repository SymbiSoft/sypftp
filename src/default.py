# Only for local tests
import sys
sys.path.append('E:\\download\\libs\\')

import appuifw, e32, thread, btsocket, ftpserver

class sypftp(object):
  def __init__(self):
    
    # Everything to output
    self.log_arr = []
    
    # Bind ftpserver logs to main console output
    ftpserver.log       = self.log
    ftpserver.logline   = self.log
    ftpserver.logerror  = self.log
    
    # Set look and feel
    self.uiConsole = appuifw.Text()
    
    appuifw.app.title = u"sypFTP"
    appuifw.app.menu = [
      (u"Run server", self.fakeBind),
      (u"Options",    self.fakeBind),
      (u"About",      self.fakeBind),
      (u"Exit",       self.exit)
    ]
    appuifw.app.body = self.uiConsole
    appuifw.app.screen = "normal"
    
    # Bind "Exit" key
    appuifw.app.exit_key_handler = self.exit
    
    # Log output thread (well not realy, but that is the only way to do this in PyS60)
    self.output_thread = e32.Ao_timer()
    self.output_thread.after(0, self.output)
    
    # Determine thread lock
    self.thread_lock  = thread.allocate_lock()
    
    # Start up network
    self.networking()
    
    # ftpserver init
    if self.network:
      self.ftp_server_deamon()
    
    # Lock and load (wait)
    self.app_lock = e32.Ao_lock()
    self.app_lock.wait()
  
  def fakeBind(self):
    self.log("Fake BIND!")
  
  def output(self):
    for index, log in enumerate(self.log_arr):
      self.uiConsole.add(log)
      self.log_arr.pop(index)
    
    self.output_thread.after(0, self.output)
  
  def log(self, text):
    if text:
      self.log_arr.append(u"%s\n" % (text))
  
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
    #self.ftp_handler.on_file_sent = self.ftp_on_file_received
    
    self.ftp_address = (self.apo.ip(), 21)
    self.ftpd = ftpserver.FTPServer(self.ftp_address, self.ftp_handler)
    
    self.ftpd.max_cons = 256
    self.ftpd.max_cons_per_ip = 5
    
    self.ftpd.serve_forever()
  
  def ftp_server_deamon(self):
    self.ftp_thread   = thread.start_new_thread(self.ftp_server_init, ())
   
  def exit(self):
    self.apo.stop()
    self.app_lock.signal()

if __name__ == '__main__':
  sypftp()
