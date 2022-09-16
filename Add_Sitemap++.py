# -*- coding: utf-8 -*-

import threading, os, sys, re, zipfile
from urlparse import urlparse

from burp import IBurpExtender
from burp import IContextMenuFactory

from java.io import IOException
from java.net import URL
from java.util import List, ArrayList
from javax import swing
from javax.swing import JMenuItem
from javax.swing.filechooser import FileNameExtensionFilter
from java.awt import HeadlessException, Toolkit
from java.awt.datatransfer import DataFlavor, UnsupportedFlavorException


class BurpExtender(IBurpExtender, IContextMenuFactory):
    
    selectedUrls = []
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))" # if you have a better one change freely
    
    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.context = None
        callbacks.setExtensionName("Add to Sitemap++")
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self, IContextMenuInvocation):
        self.context = IContextMenuInvocation
        if IContextMenuInvocation.getInvocationContext() == IContextMenuInvocation.CONTEXT_TARGET_SITE_MAP_TREE:
            menu_list = ArrayList()
            menu_list.add(JMenuItem("Add to sitemap from clipboard", actionPerformed=self.get_clipboard))
            menu_list.add(JMenuItem("Add to sitemap from file", actionPerformed=self.file_import))
            self.selectedUrls=[]
            for selectedMessage in IContextMenuInvocation.getSelectedMessages():
                if (selectedMessage.getHttpService() != None):
                    url = self.helpers.analyzeRequest(selectedMessage.getHttpService(),selectedMessage.getRequest()).getUrl()        
                    self.selectedUrls.append(urlparse(url.toString()).hostname)
            self.selectedUrls = set(self.selectedUrls)
            return menu_list
        
    def get_clipboard(self, event):
        self.sitemap_importer_from_clipboard()
        return
        
    def file_import(self, event):
        self.sitemap_importer_from_file()
        return
    
    def custom_dialog(self):
        filename = None
        fc = swing.JFileChooser()
        ef = swing.filechooser.FileNameExtensionFilter("", ["*"])
        fc.addChoosableFileFilter(ef)
        files = fc.showDialog(None, "Choose File")
        if files == swing.JFileChooser.APPROVE_OPTION:
            filename = fc.getSelectedFile().getPath()
        return filename

    def sitemap_importer_from_clipboard(self):
        content = Toolkit.getDefaultToolkit().getSystemClipboard().getData(DataFlavor.stringFlavor)
        regex = self.regex
        testregex = re.findall(regex, content)
        count = 0
        for url in testregex:
          for selectedurls in self.selectedUrls:
            if(re.match("^https?://"+selectedurls+".+", str(url[0]))):
               self.callbacks.printOutput(str(url[0]))
               t = threading.Thread(target=self.sitemap_importer, args=[str(url[0])])
               t.daemon = True
               t.start()
               count += 1
        self.callbacks.printOutput(str(count) +' unique urls imported from clipboard')
        self.callbacks.printOutput("searching for:\n----------\n"+"\n".join(self.selectedUrls)+"\n----------")        
        return

    def sitemap_importer_from_file(self):
        urls = []
        filename = self.custom_dialog()
        regex = self.regex
        if zipfile.is_zipfile(filename):
            # If it is a zipped file
            content = ''
            if filename and os.path.exists(filename):
                zip = zipfile.ZipFile(filename, 'r')
                with zip as zipObj:
                    listOfiles = zipObj.namelist()
                    for elem in listOfiles:
                        f=zip.open(elem)
                        contents=f.read()
                        content += str(contents)
                        f.close()          
            testregex = re.findall(regex, content)
            count = 0
            for url in testregex:
                for selectedurls in self.selectedUrls:
                    if(re.match("^https?://"+selectedurls+".+", str(url[0]))):
                        self.callbacks.printOutput(str(url[0]))
                        t = threading.Thread(target=self.sitemap_importer, args=[str(url[0])])
                        t.daemon = True
                        t.start()
                        count += 1
            zip.close()
            self.callbacks.printOutput(str(count) +' unique urls imported')
            self.callbacks.printOutput("searching for:\n----------\n"+"\n".join(self.selectedUrls)+"\n----------")       
        else:
            # Not a zipped file then
            if filename and os.path.exists(filename):
                file=open(filename, 'r')
                for url in file: 
                   testregex = re.findall(regex, url)
                   if(len(testregex)> 0):
                     urls.append(testregex[0][0])     
                unique = set(urls) 
                count = 0
                for url in unique: 
                    for selectedurls in self.selectedUrls:
                        if(re.match("^https?://"+selectedurls+".+", url)):
                            self.callbacks.printOutput(url) 
                            t = threading.Thread(target=self.sitemap_importer, args=[url])
                            t.daemon = True
                            t.start()
                            count += 1
            file.close()
            self.callbacks.printOutput(str(count) +' unique urls imported')
            self.callbacks.printOutput("searching for:\n----------\n"+"\n".join(self.selectedUrls)+"\n----------")      
   
    def sitemap_importer(self, http_url):
        sitemapUrl = URL(http_url)
        port = 443 if sitemapUrl.protocol == 'https' else 80
        port = sitemapUrl.port if sitemapUrl.port != -1 else port
        httpService = self.helpers.buildHttpService(sitemapUrl.host, port, sitemapUrl.protocol)
        httpRequest = self.helpers.buildHttpRequest(URL(http_url))
        self.callbacks.addToSiteMap(self.callbacks.makeHttpRequest(httpService, httpRequest))

