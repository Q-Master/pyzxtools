#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Vladimir Berezenko <qmaster@rambler.ru>


class ZXFile(object):
    TYPE_PROGRAMM=0
    TYPE_NUMBER_ARRAY=1
    TYPE_CHARACTER_ARRAY=2
    TYPE_CODE=3
    
    def __init__(self, filename, filetype, start_address, filedata):
        self.filedata = filedata
        self.filename = filename
        self.filetype = filetype
        self.start_address = start_address
        self.length = len(filedata)
    
    
    def pack(self):
        return self.filedata
    
    
    def filename(self):
        return self.filename
