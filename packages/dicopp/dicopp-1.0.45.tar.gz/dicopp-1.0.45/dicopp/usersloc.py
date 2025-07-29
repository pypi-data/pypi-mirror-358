from gi.repository import Gtk

from . import reqs
from . import users
from . import flist
from . import overrides

list=users.listdef() #TreeModelSort
#list.append(['test1'])#test will work without set list.clear()
#list.append(['test2'])
page=Gtk.ScrolledWindow()

def show(nb):
	page.set_vexpand(True)
	users.show_univ(nb,page,list,clkrow)
	return page

def clkrow(t,p,c,b):
	m=t.get_model()
	user=m.get_value(m.get_iter(p),0)
	flist.set(b,user)

def set():
	s=";"
	r=reqs.reque("list.local",{"separator" : s})
	list.clear()
	if r:
		usrs=r.split(s)
		for x in usrs:
			if x: #can be "oneuser...;"
				overrides.append(list,[x])