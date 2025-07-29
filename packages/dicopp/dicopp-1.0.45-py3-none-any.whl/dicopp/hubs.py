
from gi.repository import Gtk,GLib

import xml.etree.ElementTree as ET
import urllib.request
import math
import threading

listdef=lambda:Gtk.ListStore(str,int,str,str)

from . import base
from . import hubscon
from . import sets
from . import overrides

predefined_list='https://gist.github.com/colin-i/ad1282a45dce276407567e59afb15025/raw'
addr=Gtk.EntryBuffer(text=predefined_list)
addr2=Gtk.EntryBuffer(text='')
timeout=Gtk.EntryBuffer()
file=Gtk.EntryBuffer()
lim=Gtk.EntryBuffer(text='200')
labelA="Searching..."
labelB="HubList"
label=Gtk.Label()

list=listdef() #TreeModelSort

from enum import IntEnum
class COLUMNS(IntEnum):
	ADDRESS=0
	USERS=1
	COUNTRY=2
	SHARED=3
def treedef(lst,act,clkrow,data):
	tree=TreeView(lst)
	col(tree,'Address',COLUMNS.ADDRESS,act)
	col(tree,'Users',COLUMNS.USERS,act)
	col(tree,'Country',COLUMNS.COUNTRY,act)
	col(tree,'Shared',COLUMNS.SHARED,act)
	tree.connect("row-activated",clkrow,data)
	tree.set_activate_on_single_click(True)
	return tree
def col(tr,tx,ix,act):
	renderer = Gtk.CellRendererText()
	column = Gtk.TreeViewColumn()
	column.set_title(tx)
	column.set_resizable(True)
	column.pack_start(renderer,True)
	column.add_attribute(renderer, "text", ix)
	tr.append_column(column,act,ix)

class TreeView(Gtk.TreeView):
	def __init__(self,model):
		Gtk.TreeView.__init__(self)
		self.set_model(model)
		#self.set_headers_clickable(True)is default
	def append_column(self,col,fn,ix):
		col.connect('clicked',fn,ix)
		col.set_clickable(True)
		Gtk.TreeView.append_column(self,col)

def confs():
	f=Gtk.Frame(label="Hub List")
	g=Gtk.Grid()
	lb=Gtk.Label(halign=Gtk.Align.START,label="File address")
	g.attach(lb,0,0,1,1)
	g.attach(sets.entries(addr),1,0,1,1)
	lb=Gtk.Label(halign=Gtk.Align.START,label="File address 2")
	g.attach(lb,0,1,1,1)
	g.attach(sets.entries(addr2),1,1,1,1)
	lb=Gtk.Label(halign=Gtk.Align.START,label="Timeout in seconds (blank for default)")
	g.attach(lb,0,2,1,1)
	g.attach(sets.entries(timeout),1,2,1,1)
	lb=Gtk.Label(halign=Gtk.Align.START,label="File fallback location")
	g.attach(lb,0,3,1,1)
	g.attach(sets.entries(file),1,3,1,1)
	lb=Gtk.Label(halign=Gtk.Align.START,label="Maximum number of entries")
	g.attach(lb,0,4,1,1)
	g.attach(sets.entries(lim),1,4,1,1)
	f.set_child(g)
	return f
def store(d):
	d['hub_file']=addr.get_text()
	d['hub_file2']=addr2.get_text()
	d['hub_timeout']=timeout.get_text()
	d['hub_file_fallback']=file.get_text()
	d['hub_limit']=lim.get_text()
def restore(d):
	addr.set_text(d['hub_file'],-1)
	addr2.set_text(d['hub_file2'],-1)
	timeout.set_text(d['hub_timeout'],-1)
	file.set_text(d['hub_file_fallback'],-1)
	lim.set_text(d['hub_limit'],-1)

def reset():
	list.clear()
	ini()

def clk_univ(lst,ix):
	n=lst.get_sort_column_id()
	if n[1]!=Gtk.SortType.ASCENDING:
		lst.set_sort_column_id(ix,Gtk.SortType.ASCENDING)
	else:
		lst.set_sort_column_id(ix,Gtk.SortType.DESCENDING)
def clk(b,ix):
	clk_univ(list,ix)
def show():
	wn=Gtk.ScrolledWindow()
	wn.set_vexpand(True)
	tree=treedef(list,clk,hubscon.add,list)
	wn.set_child(tree)
	return wn

def ini():
	label.set_text(labelA)
	#global async_th
	async_th = threading.Thread(target=ini_async)
	async_th.start()
def ini_urls(a,b):
	try:
		urlresult=urllib.request.urlopen(a) #,timeout -> this is not working for https and for http is non-blocking at all
	except Exception:
		print("urlopen exception")
		try:
			if b:
				urlresult=urllib.request.urlopen(b)
			else:
				return None
		except Exception:
			print("urlopen 2 exception")
			return None
	return urlresult
def ini_predefined():
	try:
		urlresult=urllib.request.urlopen(predefined_list)
	except Exception:
		print("gist open error")
		return None
	urls=urlresult.read().split()
	return ini_urls(urls[0].decode(),urls[1].decode())
def ini_async():
	import socket
	a=timeout.get_text()
	if a:
		a=float(a)
		socket.setdefaulttimeout(a) #this is working both for https and http
	else:
		if socket.getdefaulttimeout()!=None:  #in case we already set it
			socket.setdefaulttimeout(None) #this will wait like default, ~2 minutes?
	if addr.get_text()==predefined_list:
		urlresult=ini_predefined()
		if urlresult==None:
			try:
				urlresult=urllib.request.urlopen(addr2.get_text())
			except Exception:
				print("after predefined, urlopen 2 exception")
	else:
		urlresult=ini_urls(addr.get_text(),addr2.get_text())
	#GLib.idle_add(ini_main,(urlresult,threading.current_thread())) why was needed to compare async_th and th?
	GLib.idle_add(ini_main,urlresult)
def ini_main(urlresult):
	#urlresult,th=mixt
	#if async_th==th:
	try:
		label.set_text(labelB)
		if urlresult==None:
			raise Exception
		tree = ET.ElementTree(file=urlresult)
		root = tree.getroot()
	except Exception:
		print("hubs list error")
		if file.get_text():
			tree = ET.parse(file.get_text())
			root = tree.getroot()
		else:
			#if the module has never been imported before (== not present in sys.modules), then it is loaded and added to sys.modules.
			import gzip

			#https://setuptools.pypa.io/en/latest/userguide/datafiles.html
			#import os.path
			from importlib.resources import files
			#with gzip.open(os.path.join(os.path.dirname(__file__),'hublist.xml.gz'), mode='r') as zipfile:
			with gzip.open(files(base.pkname).joinpath('hublist.xml.gz'), mode='r') as zipfile:
				root = ET.fromstring(zipfile.read())
	ini_result(root)
	return False
def ini_result(root):
	try:
		hbs=root.find("Hubs").findall("Hub")
	except Exception:
		return
	mx=min(int(lim.get_text()),len(hbs))
	for i in range(mx):
		attrs=hbs[i].attrib
		if ('Secure' in attrs) and (attrs['Secure']):
			huburl=attrs['Secure']
		elif 'Address' in attrs:
			huburl=attrs['Address']
		else:
			continue
		if ('Users' in attrs) and ('Country' in attrs) and ('Shared' in attrs):
			overrides.append(list,[huburl,int(attrs['Users']),attrs['Country'],convert_size(int(attrs['Shared']))])

def convert_size(size_bytes):
	if size_bytes == 0:
		return "0 B"
	size_name = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
	i = math.floor(math.log(size_bytes, 1024))
	p = pow(1024, i)
	s = math.floor(size_bytes / p * 100)/100 # trunc for positiv/negativ
	return "%s %s" % (s, size_name[i])
