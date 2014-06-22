#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Vladimir Berezenko <qmaster@rambler.ru>
from argparse import ArgumentParser
from pyZXTools import tap
from pyZXTools.zxfile import ZXFile



if __name__ == "__main__":
    EXTENSIONS = {
        "B" : ZXFile.TYPE_PROGRAMM, "b" : ZXFile.TYPE_PROGRAMM, 
        "C" : ZXFile.TYPE_CODE, "c" : ZXFile.TYPE_CODE, 
        "DC" : ZXFile.TYPE_CHARACTER_ARRAY, "dc" : ZXFile.TYPE_CHARACTER_ARRAY, 
        "DN" : ZXFile.TYPE_NUMBER_ARRAY, "dn" : ZXFile.TYPE_NUMBER_ARRAY, 
    }
    def list_files(args):
        tapO = tap.TAP(args.infile)
        tapO.open()
        tapO.list_files()
        tapO.close()
    
    
    def add_file(args):
        tapO = tap.TAP(args.infile)
        tapO.open()
        _, _, extension = args.filename.rpartition(".")
        try:
            ext = EXTENSIONS[extension]
        except KeyError:
            ext = EXTENSIONS["C"]
        
        tapO.append_file(args.filename, ext, args.start_address)
        tapO.close()
    
    
    def get_file(args):
        tapO = tap.TAP(args.infile)
        tapO.open()
        filename, _, extension = args.filename.rpartition(".")
        tapO.extract_file(filename, EXTENSIONS[extension])
        tapO.close()
    
    
    def create_img(args):
        tapO = tap.TAP(args.outfile)
        tapO.img_data = ""
        tapO.modified = True
        tapO.close()
    
    
    argparser = ArgumentParser()
    subparsers = argparser.add_subparsers(title="Commands")
    
    list_parser = subparsers.add_parser("list", help="show image catalog")
    list_parser.add_argument('infile', nargs='?', type=str, help="image file name")
    list_parser.set_defaults(func=list_files)
    
    add_parser = subparsers.add_parser("add", help="put file into image")
    add_parser.add_argument('infile', nargs='?', type=str, help="image file name")
    add_parser.add_argument('filename', nargs='?', type=str, help="filename in format file.ext to add to image")
    add_parser.add_argument('-s', '--start_address', type=int, default=0, help="start address for file")
    add_parser.set_defaults(func=add_file)
    
    pop_parser = subparsers.add_parser("pop", help="extract file from image")
    pop_parser.add_argument('infile', nargs='?', type=str, help="image file name")
    pop_parser.add_argument('filename', nargs='?', type=str, help="filename in format file.ext to fetch from image")
    pop_parser.set_defaults(func=get_file)
    
    create_parser = subparsers.add_parser("create", help="create new image file")
    create_parser.add_argument('outfile', nargs='?', type=str, help="image file name")
    create_parser.set_defaults(func=create_img)
    
    
    args = argparser.parse_args()
    args.func(args)