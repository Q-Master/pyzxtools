#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Based on functionality of mctrd by SAM Style
# Author: Vladimir Berezenko <qmaster@rambler.ru>


import sys, os, stat, struct
from zxfile import ZXFile

TYPE_NONE = 0
TYPE_TRD = 1
TYPE_SCL = 2


class TRDfile(ZXFile):
    def __init__(self, filename, extension, start_address, sector_count, filedata, start_sector = 0, start_track = 0):
        super(TRDfile,self).__init__(filename, ZXFile.TYPE_PROGRAMM if extension == "B" else ZXFile.TYPE_CODE, start_address, filedata)
        self.extension = extension
        self.sector_count = int(sector_count)
        if len(filedata)%256:
            filedata_pad = 256-len(filedata)%256
            filedata += "\x00"*int(filedata_pad)
        self.start_sector = start_sector
        self.start_track = start_track
    
    
    def pack(self, zxtype):
        if zxtype == TYPE_TRD:
            return struct.pack("<8scHHccc", self.fname(), self.extension, self.start_address, self.length, chr(self.sector_count), chr(self.start_sector), chr(self.start_track))
        elif zxtype == TYPE_SCL:
            return struct.pack("<8scHHc", self.fname(), self.extension, self.start_address, self.length, chr(self.sector_count))
        else:
            raise AttributeError("Wrong file type")
    
    
    def fname(self):
        return self.filename.ljust(8, " ")[:8]


class TRD(object):
    def __init__(self, filename = None):
        self.img_filename = filename
        self.img_data = None
        self.img_type = TYPE_NONE
        self.filelist = []
        self.fies_amount = 0
        self.last_track = 1
        self.last_sector = 0
        self.free_sector = 0
        self.modified = False
    
    
    def open(self, filename = None):
        if not filename and not self.img_filename:
            raise IOError("No file found")
        if filename:
            self.img_filename = filename
        img_file = open(self.img_filename, 'rb')
        self.img_data = img_file.read()
        img_file.close()
        
        if self.img_data[:8] == "SINCLAIR" and self.img_data[8] >= 0:
            self.img_type = TYPE_SCL
        elif len(self.img_data) > 0x900 and ord(self.img_data[0x8e7]) == 0x10:
            self.img_type = TYPE_TRD
            last_sector, last_track, _, files_amount, self.free_sector = struct.unpack("<ccccH", self.img_data[0x8e1: 0x8e7])
            self.disc_name = self.img_data[0x8f5:0x8ff]
            self.last_sector = ord(last_sector)
            self.last_track = ord(last_track)
            self.fies_amount = ord(files_amount)
        else:
            self.img_type = TYPE_NONE
            self.img_data = None
            raise IOError("Wrong file type")
        self._scan_files()
    
    
    def _scan_files(self):
        if self.img_type == TYPE_NONE:
            raise IOError("No file opened")
        elif self.img_type == TYPE_SCL:
            idx = 9
            self.fies_amount = ord(self.img_data[8])
            data_start = self.fies_amount*14
            for i in range(self.fies_amount):
                filename, extension, start, length, sector_count = struct.unpack("<8scHHc", self.img_data[idx:idx+14])
                sector_count = ord(sector_count)
                filedata = self.img_data[data_start:data_start+sector_count*256]
                data_start += sector_count*256
                self.filelist.append(TRDfile(filename, extension, start, sector_count, filedata))
                idx += 14
        elif self.img_type == TYPE_TRD:
            i = 0
            idx = 0
            while ord(self.img_data[idx]) and i < 128:
                filename, extension, start, length, sector_count, start_sector, start_track = struct.unpack("<8scHHccc", self.img_data[idx:idx+16])
                sector_count = ord(sector_count)
                start_sector = ord(start_sector)
                start_track = ord(start_track)
                data_start = start_track*4096+start_sector*256
                filedata = self.img_data[data_start:data_start+sector_count*256]
                self.filelist.append(TRDfile(filename, extension, start, sector_count, filedata, start_sector, start_track))
                idx += 16
                i += 1
    
    
    def list_files(self):
        if self.img_type == TYPE_NONE:
            raise IOError("No file opened")
        if self.img_type == TYPE_TRD:
            print "Name\t\tExt\tStart\tSize\tSLen\tTrk\tSec\n---------------------------"
        else:
            print "Name\t\tExt\tStart\tSize\tSLen\n---------------------------"
            
        for zxfile in self.filelist:
            if self.img_type == TYPE_TRD:
                print "%.8s\t%c\t%i\t%i\t%i\t%i\t%i" % (zxfile.fname(), zxfile.extension, zxfile.start_address, zxfile.length, zxfile.sector_count, zxfile.start_track, zxfile.start_sector)
            else:
                print "%.8s\t%c\t%i\t%i\t%i" % (zxfile.fname(), zxfile.extension, zxfile.start_address, zxfile.length, zxfile.sector_count)
    
    
    def append_file(self, filename, basic = False, autostart = 0):
        if self.img_type == TYPE_NONE:
            raise IOError("No file opened")
        if self.fies_amount > 127:
            raise IOError("Too many files")
        zxfile = open(filename, 'rb')
        filedata = zxfile.read()
        zxfile.close()
        
        name, extension = filename.rsplit(".")
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
        
        if self.free_sector and self.free_sector < sector_count:
            raise IOError("No free space")
        file = TRDfile(name, extension, length if basic else 0, sector_count, filedata)
        self.fies_amount += 1
        
        if self.img_type == TYPE_SCL:
            self.filelist.append(file)
        elif self.img_type == TYPE_TRD:
            self.free_sector -= sector_count
            file.start_sector = self.last_sector
            file.start_track = self.last_track
            self.filelist.append(file)
            self.last_track = self.last_track + sector_count/16
            self.last_sector = sector_count%16
        self.modified = True
    
    
    def extract_file(self, filename):
        name, extension = filename.rsplit(".")
        name = name.ljust(8, " ")
        if not extension:
            extension = 'C'
        for zx_file in self.filelist:
            if zx_file.fname() == name and zx_file.extension == extension:
                outfile = open(filename, 'wb+')
                outfile.write(zx_file.filedata)
                outfile.close()
                break
    
    
    def _crc(self, buf):
        return sum([ord(x) for x in buf])
    
    
    def close(self):
        if self.img_type == TYPE_NONE:
            raise IOError("No file opened")
        
        if not self.modified:
            return
        
        filedata = "".join(d.filedata for d in self.filelist)
        
        if self.img_type == TYPE_SCL:
            header = struct.pack('8sc', 'SINCLAIR', chr(self.fies_amount))
            for f in self.filelist:
                header += f.pack(TYPE_SCL)
            header += struct.pack('<I', self._crc(header))
        else:
            header = ""
            i = 0
            
            for f in self.filelist:
                header += f.pack(TYPE_TRD)
                i += 1
            
            header += "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"*(128-i)
            #9 sector
            header += struct.pack("<c224sccccH3s9s2s11s", "\x00", "\x00"*224, chr(self.last_sector), chr(self.last_track), "\x00", chr(self.fies_amount), self.free_sector, "\x10\x00\x00",  " "*9, "\x00\x00", self.disc_name)
            # last sectors of 1st track
            header += "\x00"*1792
            filedata += "\x00"*(655360-4096-len(filedata))
        
        img = open(self.img_filename, "wb+")
        img.write(header)
        img.write(filedata)
        img.close()
        self.img_data = None
        self.img_type = TYPE_NONE
