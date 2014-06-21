#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Vladimir Berezenko <qmaster@rambler.ru>

import sys, os, stat, struct
from pyZXTools.trdos import TRDfile


class Hobeta(object):
    def __init__(self, filename = None):
        self.img_filename = filename
        self.img_data = None
        self.modified = False
    
    
    def _crc(self, data):
        crc=0;
        for i in data:
            crc += i*257+i
        return  crc
    
    
    def open(self, filename = None):
        if not filename and not self.img_filename:
            raise IOError("No file found")
        if filename:
            self.img_filename = filename
        img_file = open(self.img_filename, 'rb')
        img_data = img_file.read()
        img_file.close()
        
        crcf = struct.unpack("<H", img_data[15:17])
        crc = self._crc(img_data[:14])
        
        if crc != crcf:
            raise IOError("Wrong CRC in file")
        filename, extension, start, length, seclen = struct.unpack("<8scHHH", img_data[:14])
        self.img_data = TRDfile(filename, extension, start, length, seclen, img_data[17:])
    
    
    def append_file(self, filename, basic = False, autostart = 0):
        if self.img_data:
            raise IOError("File is already opened")
        zxfile = open(filename, 'rb')
        filedata = zxfile.read()
        zxfile.close()
        
        name, extension = filename.rsplit(".$")
        if not extension:
            extension = 'C'
        
        if basic:
            extension = 'B'
            basic_append = struct.pack("<ccH", '\x80', '\xaa', autostart)
            filedata += basic_append
        length = len(filedata)
        
        if length > 0xff00:
            raise IOError("File size too big")
        sector_count = int(round(length/256.0+0.5))
        
        self.img_data = TRDfile(name, extension, length if basic else 0, length, sector_count, filedata)
        self.modified = True
    
    
    def extract_file(self, filename):
        outfile = open(filename, 'wb+')
        outfile.write(zx_file.filedata)
        outfile.close()
    
    
    def close(self):
        if not self.img_data:
            raise IOError("No file opened")
        
        if not self.modified:
            return
        
        header = struct.pack("<8scHHH", self.img_data.filename, self.img_data.extension, self.img_data.start_address, self.img_data.length, self.img_data.sector_count)
        crc = self._crc(header)
        header += struct.pack("<H", crc)
        
        img = open(self.img_filename, "wb+")
        img.write(header)
        img.write(self.img_data.filedata)
        img.close()
        
        self.img_data = None
