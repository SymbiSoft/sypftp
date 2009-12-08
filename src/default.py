import appuifw, e32, e32dbm, globalui, btsocket, thread, re, os, ftpserver

class sypftp(object):
  def __init__(self):
    
    self.__NAME__     = u"sypFTP"
    self.__VERSION__  = u"0.1.0"
    self.__AUTHOR__   = u"Intars Students"
    self.__EMAIL__    = u"the.mobix@gmail.com"
    
    try:
      m = re.match("^([A-Z])\:", os.getcwd())
      self.__DRIVE__ = m.group(1)
    except:
      self.__DRIVE__ = "C:"
    
    self.__APPDIR__ = u"%s:\\data\\sypFTP" % self.__DRIVE__
    
    if os.path.isdir(self.__APPDIR__) == False:
      os.makedirs(self.__APPDIR__)
    
    # Some globaly used varibles
    self.log_arr      = []
    self.ftpd_running = False
    self.db           = u"%s\\options.db" % self.__APPDIR__
    
    self.generateDriveList()
    
    self.default = {
      u"port"  : 21,
      u"user"  : u"user",
      u"pass"  : u"12345",
      u"dir"   : u"C:\\"
    }
    
    self.getOptions()
    
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
    
    self.uiOptions = appuifw.Form(
      [
        (u"Port",   "number", self.default["port"]),
        (u"User",   "text",   self.default["user"]),
        (u"Paswd",  "text",   self.default["pass"]),
        (u"Dir.",   "combo",  (self.available_drives, self.available_drives.index(self.default["dir"])))
      ],
      appuifw.FFormEditModeOnly
    )
    self.uiOptions.save_hook = self.saveOptions
    
    self.uiPopup = globalui
    
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
  
  def showAbout(self):
    self.uiPopup.global_msg_query(
      (
      self.__NAME__ + " v." + self.__VERSION__ + "\n" +
      "by " + self.__AUTHOR__ + "\n" + 
      self.__EMAIL__
      ),
      u"About",
      10
    )
  
  def getOptions(self):
    try:
      db = e32dbm.open(self.db, "r")
      
      for key, value in db.items():
        if key == "port":
          self.default[key] = int(value)
        else:
          self.default[key] = (u"%s" % value)
      
      db.close()http://docs.python.org/library/re.html
      
    except Exception, e:
      self.setOptions()
  
  def setOptions(self):
    db = e32dbm.open(self.db, "c")
    for key in self.default.keys():
      db[key] = str(self.default[key])
    db.close()
  
  def generateDriveList(self):
    self.available_drives = [((u"%s\\" % drive)) for drive in e32.drive_list()]
  
  def uiMenu(self, struc):
    allstruc = [
      ["connect", (u"Connect to network",   self.networking)],
      ["start",   (u"Start server",         self.ftp_server_start)],
      ["stop",    (u"Stop server",          self.ftp_server_stop)],
      ["restart", (u"Restart server",       self.ftp_server_restart)],
      ["options", (u"Options",              self.showOptions)],
      ["about",   (u"About",                self.showAbout)],
      ["exit",    (u"Exit",                 self.exit)],
    ]
    
    selstruc = []
    
    for name, bind in allstruc:
      if struc.count(name):
        if name == "connect" and self.getIP() == False:
          selstruc.append(bind)
        elif name == "start" and self.getIP() != False and self.ftpd_running == False:
          selstruc.append(bind)
        elif (name == "stop" or name == "restart") and self.ftpd_running == True:
          selstruc.append(bind)
        elif name != "connect" and name != "start" and name != "stop" and name != "restart":
          selstruc.append(bind)
    
    if len(selstruc):
      appuifw.app.menu = selstruc
  
  def saveOptions(self, arg):
    
    if int(arg[0][2]) < 0 or int(arg[0][2]) > 65535:
      self.uiPopup.global_note(u"Port must be in range of 0 - 65535")
      return False
    
    else:
      self.default["port"] = int(arg[0][2])
    
    if re.search("^[a-zA-Z0-9_]+$", (u"%s" % arg[1][2])) == None:
      self.uiPopup.global_note(u"You can only use A-z, 0-9 and underscore in username")
      return False
    
    else:
      self.default["user"] = (u"%s" % arg[1][2])
      
    if re.search("^[a-zA-Z0-9_@#$%^&+=]+$", (u"%s" % arg[2][2])) == None:
      self.uiPopup.global_note(u"You can only use A-z, 0-9 and any of them (_@#$%^&+=) in password")
      return False
      
    else:
      self.default["pass"] = (u"%s" % arg[2][2])
    
    self.default["dir"] = (u"%s" % self.available_drives[arg[3][2][1]])
    
    self.setOptions()
    self.uiPopup.global_note(u"Options saved", "info")
    return True
  
  def debug(self, command):
    if command:
      self.log(eval("dir(" + command + ")"))
  
  def showOptions(self):
    self.generateDriveList()
    self.uiOptions.execute()
  
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
    
    self.log("Connecting to network ...")
    
    try:
      self.apid = btsocket.select_access_point()
      self.apo  = btsocket.access_point(self.apid)
      
      self.apo.start()
      btsocket.set_default_access_point(self.apo)
      
      self.log("done.")
      self.uiMenu(["start", "restart", "stop", "options", "about", "exit"])
      
    except:
      self.log("failed.")
      self.uiMenu(["connect", "options", "about", "exit"])
  
  
  def ftp_server_restart(self):
    self.ftp_server_stop()
    self.ftp_server_start()
  
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
      self.ftp_authorizer.add_user(self.default["user"], self.default["pass"], self.default["dir"], perm='elradfmw')
      
      self.ftp_handler            = ftpserver.FTPHandler
      self.ftp_handler.authorizer = self.ftp_authorizer
      self.ftp_handler.banner     = "sypFTP"
      
      
      self.ftpd = ftpserver.FTPServer((self.getIP(), self.default["port"]), self.ftp_handler)
      self.ftpd.max_cons        = 256
      self.ftpd.max_cons_per_ip = 5
      self.ftpd_running         = True
      
      self.uiMenu(["restart", "stop", "options", "about", "exit"])
      self.ftpd.serve_forever()
      
      self.ftpd_running = False
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
      self.ftp_server_stop()
      self.apo.stop()
    except:
      pass
    
    self.app_lock.signal()

if __name__ == '__main__':
  sypftp()
