#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Vladimir Berezenko <qmaster@rambler.ru>

import sys, os, stat, struct

TAP_BLOCK_TYPE_PROGRAMM=0
TAP_BLOCK_TYPE_NUMBER_ARRAY=1
TAP_BLOCK_TYPE_CHARACTER_ARRAY=2
TAP_BLOCK_TYPE_CODE=3


class TAPfile(object):
    def __init__(self, filename, filetype, start_address, param2, filedata):
        self.filename = filename.ljust(10, " ")[:10]
        self.filetype = filetype
        self.start_address = start_address
        self.param2 = param2
        self.filedata = filedata
        self.length = len(filedata)
    
    
    def _header(self):
        return struct.pack("<c10sHHH", chr(self.filetype), self.filename, self.length, self.start_address, self.param2)
    
    
    def _crc(self, data, code):
        xor = 0xff if code else 0x00
        
        for i in data:
            xor ^= ord(i)
        return chr(xor)
    
    
    def pack(self):
        header = self._header()
        out = struct.pack("<Hc", len(header)+2, '\x00')
        out += header
        out += struct.pack("<cHc", self._crc(header, False), self.length+2, '\xff')
        out += self.filedata
        out += self._crc(self.filedata, True)
        return out


class TAP(object):
    TYPES = {TAP_BLOCK_TYPE_PROGRAMM : "B", TAP_BLOCK_TYPE_CODE : "C", TAP_BLOCK_TYPE_CHARACTER_ARRAY : "DC", TAP_BLOCK_TYPE_NUMBER_ARRAY : "DN"}
    def __init__(self, filename = None):
        self.img_filename = filename
        self.modified = False
        self.img_data = None
        self.filelist = []
    
    
    def open(self, filename = None):
        if not filename and not self.img_filename:
            raise IOError("No file found")
        if filename:
            self.img_filename = filename
        img_file = open(self.img_filename, 'rb')
        self.img_data = img_file.read()
        img_file.close()
        self._scan_files()
    
    
    def _scan_files(self):
        if self.img_data == None:
            raise IOError("No file opened")
        idx = 0
        while idx < len(self.img_data):
            try:
                (length,) = struct.unpack("<H", self.img_data[idx: idx+2])
                (block_type, filetype, filename, file_length, start_address, param2, checksumm) = struct.unpack("<cc10sHHHc", self.img_data[idx+2 : idx+2+length])
                if block_type != '\x00':
                    raise IOError("Wrong TAP file")
                idx += length+2
                (length,) = struct.unpack("<H", self.img_data[idx: idx+2])
                block_type = self.img_data[idx+2]
                if block_type != '\xff':
                    raise IOError("Wrong TAP file")
                data = self.img_data[idx+3 : idx+3+length-2]
                checksumm = self.img_data[idx+3+length-1 : idx+3+length]
                self.filelist.append(TAPfile(filename, ord(filetype), start_address, param2, data))
                idx += length+2
            except IndexError:
                raise IOError("Unexpected end of file %d" % idx)
    
    
    def list_files(self):
        if self.img_data == None:
            raise IOError("No file opened")
        
        print "Name\t\tType\tStart\tSize\n---------------------------------------------"
        
        for zxfile in self.filelist:
            print "%.10s\t%s\t%i\t%i" % (zxfile.filename, TAP.TYPES[zxfile.filetype], zxfile.start_address, zxfile.length)
    
    
    def append_file(self, filename, file_type, start_address):
        if self.img_data == None:
            raise IOError("No file opened")
        zxfile = open(filename, 'rb')
        filedata = zxfile.read()
        zxfile.close()
        
        filename, _, _ = filename.rpartition(".")
        
        if file_type == TAP_BLOCK_TYPE_PROGRAMM:
            param2 = len(filedata)
        elif file_type == TAP_BLOCK_TYPE_CODE:
            param2 = 32768
        self.filelist.append(TAPfile(filename, file_type, start_address, param2, filedata))
        self.modified = True
    
    
    def extract_file(self, filename, file_type):
        if self.img_data == None:
            raise IOError("No file opened")
        filename = filename.ljust(10, " ")
        
        for zx_file in self.filelist:
            if zx_file.filename == filename and zx_file.filetype == file_type:
                outfile = open(filename.strip()+".%s" % TAP.TYPES[file_type], 'wb+')
                outfile.write(zx_file.filedata)
                outfile.close()
                break
    
    
    def close(self):
        if self.img_data == None:
            raise IOError("No file opened")
        
        if not self.modified:
            return
        
        filedata = "".join(d.pack() for d in self.filelist)
        img = open(self.img_filename, "wb+")
        img.write(filedata)
        img.close()
        
        self.img_data = None
