import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk,GLib

import os
import sys

from . import base
from . import layout 
from . import limit
from . import log
from . import stor2
from . import nick
from . import hubs
from . import hubscon
from . import daem
from . import search
from . import dload
from . import com
from . import first

def quit(widget, mainloop):
	base.write(widget)
	daem.dclose_owned() #in base.write is log, can require daemon open
	limit.close()
	hubscon.close()
	search.close()
	dload.close()
	com.close()
	mainloop.quit()
	return True

def main():
	daem.ini()
	win = Gtk.Window()
	d=base.read(win)  #needed at cleanup(stor2)/first(stor2/nick)/...
	if len(sys.argv)>1:
		if sys.argv[1]=="--remove-config":
			cleanup()
			return
		sys.stdout.write("ENTRY_DEBUG marker\n")
		sys.stdout.flush()
	n=first.ini()
	if n:
		mainloop = GLib.MainLoop()
		win.set_title('Direct Connect')
		layout.show(win)
		limit.open(win)
		log.ini()
		stor2.ini()
		nick.ini(False if n==1 else True)
		hubs.ini()
		win.connect('close-request', quit, mainloop)
		try:
			daem.dopen()
		except Exception:
			print("daemon open error")
			return
		base.read2(d)#after daemon start
		win.show()
		mainloop.run()
def get_yes():
	print("yes ?");
	str = ""
	while True:
		x = sys.stdin.read(1) # reads one byte at a time, similar to getchar()
		if x == '\n':
			break
		str += x
	return str
def cleanup():
	#remove config and exit
	r=" removed"
	c=base.get_client_dir()
	if os.path.isdir(c):
		print("Would remove(dirs only if empty):");
		f=base.get_client()
		if os.path.isfile(f):
			print(f)
		else:
			f=None
		print(c)
		basepath=os.path.dirname(c)
		basepathname=os.path.basename(basepath)
		if basepathname[0]=='.' or basepathname==base.pkname: #same like torra
			print(basepath)
		else:
			basepath=None
		str=get_yes()
		if str=="yes":
			if f:
				os.remove(f)
				print(f+r)
			if len(os.listdir(path=c))==0:
				os.rmdir(c) #OSError if not empty
				print(c.__str__()+r)
				if basepath:
					if len(os.listdir(path=basepath))==0:
						os.rmdir(basepath)
						print(basepath.__str__()+r)
					else:
						print(basepath.__str__()+" is not empty.")
			else:
				print(c.__str__()+" is not empty.")
		else:
			print("expecting \"yes\"")
	f2=stor2.get_file() #default or get_text
	if os.path.isfile(f2):
		print("Was this extern file, "+f2+" ,made by dicopp? Remove?")
		str=get_yes()
		if str=="yes":
			os.remove(f2)
			print(f2+r)
		else:
			print("expecting \"yes\"")

if __name__ == "__main__":
    main()
