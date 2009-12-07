# Only for local tests
import sys
sys.path.append('E:\\download\\libs\\')

import appuifw, e32, thread, btsocket, ftpserver

class sypftp(object):
  def __init__(self):
    
    # Some globaly used varibles
    self.log_arr = []
    self.ftpd_running = False
    
    # Bind ftpserver logs to main console output
    ftpserver.log       = self.log
    ftpserver.logline   = self.log
    ftpserver.logerror  = self.log
    
    # Set look and feel
    self.uiConsole = appuifw.Text()
    
    appuifw.app.title = u"sypFTP"
    self.uiMenu(["connect", "options", "about", "exit"])
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
    if self.getIP():
      self.ftp_server_start()
    
    # Lock and load (wait)
    self.app_lock = e32.Ao_lock()
    self.app_lock.wait()
  
  def fakeBind(self):
    self.log("Fake BIND!")
  
  def uiMenu(self, struc):
    allstruc = [
      ["connect", (u"Connect to network",   self.networking)],
      ["start",   (u"Start server",         self.ftp_server_start)],
      ["stop",    (u"Stop server",          self.ftp_server_stop)],
      ["options", (u"Options",              self.fakeBind)],
      ["about",   (u"About",                self.fakeBind)],
      ["exit",    (u"Exit",                 self.exit)],
    ]
    
    selstruc = []
    
    for name, bind in allstruc:
      if struc.count(name):
        if name == "connect" and self.getIP() == False:
          selstruc.append(bind)
        elif name == "start" and self.getIP() != False and self.ftpd_running == False:
          selstruc.append(bind)
        elif name == "stop" and self.ftpd_running == True:
          selstruc.append(bind)
        elif name != "connect" and name != "start" and name != "stop":
          selstruc.append(bind)
    
    if len(selstruc):
      appuifw.app.menu = selstruc
  
  def output(self):
    if len(self.log_arr):
      for index, msg in enumerate(self.log_arr):
        self.uiConsole.add(msg)
        self.log_arr.pop(index)
    
    self.output_thread.after(0, self.output)
  
  def log(self, msg):
    if msg:
      self.log_arr.append(u"%s\n" % (msg))
  
  def getIP(self):
    try:
      return self.apo.ip()
    except:
      return False
  
  def networking(self):
    
    self.log("Connecting to network ...");
    
    self.apid = btsocket.select_access_point()
    self.apo  = btsocket.access_point(self.apid)
    
    try:
      self.apo.start()
      btsocket.set_default_access_point(self.apo)
      self.log("done.")
      self.uiMenu(["start", "stop", "options", "about", "exit"])
    except:
      self.log("failed.")
      self.uiMenu(["connect", "options", "about", "exit"])
  
  def ftp_server_stop(self):
    try:
      self.ftpd.close_all()
    except:
      pass
    
    self.ftpd_running = False
    self.uiMenu(["start", "options", "about", "exit"])
  
  def ftp_server_deamon(self):
    if self.ftpd_running == False:
      self.ftp_authorizer   = ftpserver.DummyAuthorizer()
      self.ftp_handler      = ftpserver.FTPHandler
      
      # Just for now, while everything is breaking ...
      self.ftp_authorizer.add_user('user', '12345', "E:\\", perm='elradfmw')
      
      self.ftp_handler.authorizer = self.ftp_authorizer
      self.ftp_handler.banner     = "sypFTP"
      
      self.ftp_address = (self.getIP(), 21)
      self.ftpd = ftpserver.FTPServer(self.ftp_address, self.ftp_handler)
      
      self.ftpd.max_cons = 256
      self.ftpd.max_cons_per_ip = 5
      
      self.ftpd_running = True
      self.uiMenu(["stop", "options", "about", "exit"])
      self.ftpd.serve_forever()
      
      self.log("FTP server stopped.")
  
  def ftp_server_start(self):
    if self.getIP():
      self.ftpd_thread = thread.start_new_thread(self.ftp_server_deamon, ())
      
    else:
      self.networking()
      
      if self.getIP():
        self.ftpd_thread = thread.start_new_thread(self.ftp_server_deamon, ())
      else:
        self.uiMenu(["connect", "options", "about", "exit"])
  
  def exit(self):
    try:
      self.apo.stop()
    except:
      pass
    
    self.app_lock.signal()

if __name__ == '__main__':
  sypftp()
