#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Vladimir Berezenko <qmaster@rambler.ru>


from argparse import ArgumentParser
from pyZXTools import trdos

if __name__ == "__main__":
    def list_files(args):
        trd = trdos.TRD(args.infile)
        trd.open()
        trd.list_files()
        trd.close()
    
    
    def add_file(args):
        trd = trdos.TRD(args.infile)
        trd.open()
        trd.append_file(args.filename, args.start, args.length, args.basic, args.autostart)
        trd.close()
    
    
    def get_file(args):
        trd = trdos.TRD(args.infile)
        trd.open()
        trd.extract_file(args.filename)
        trd.close()
    
    
    def create_img(args):
        trd = trdos.TRD(args.outfile)
        if args.type == 'trd':
            trd.img_type = trdos.TYPE_TRD
            trd.disc_name = args.name.ljust(11, " ")
            trd.free_sector = 159*16
        elif args.type == 'scl':
            trd.img_type = trdos.TYPE_SCL
        else:
            raise AttributeError("Unknown img type")
        trd.modified = True
        trd.close()
        
    
    argparser = ArgumentParser()
    subparsers = argparser.add_subparsers(title="Commands")
    
    list_parser = subparsers.add_parser("list", help="show image catalog")
    list_parser.add_argument('infile', nargs='?', type=str, help="image file name")
    list_parser.set_defaults(func=list_files)
    
    add_parser = subparsers.add_parser("add", help="put file into image")
    add_parser.add_argument('infile', nargs='?', type=str, help="image file name")
    add_parser.add_argument('filename', nargs='?', type=str, help="filename in format file.ext to add to image")
    add_parser.add_argument('-s', '--start', type=int, default=0, help="set start address")
    add_parser.add_argument('-l', '--length', type=int, default=-1, help="force file length")
    add_parser.add_argument('-b', '--basic', action='store_true', help="file to append is a basic file")
    add_parser.add_argument('-a', '--autostart', type=int, default=0, help="autostart line for basic file")
    add_parser.set_defaults(func=add_file)
    
    pop_parser = subparsers.add_parser("pop", help="extract file from image")
    pop_parser.add_argument('infile', nargs='?', type=str, help="image file name")
    pop_parser.add_argument('filename', nargs='?', type=str, help="filename in format file.ext to fetch from image")
    pop_parser.set_defaults(func=get_file)
    
    create_parser = subparsers.add_parser("create", help="create new image file")
    create_parser.add_argument('outfile', nargs='?', type=str, help="image file name")
    create_parser.add_argument('-n', '--name', type=str, help="disc name if trd", default="")
    create_parser.add_argument('-t', '--type', type=str, choices=['trd', 'scl'], help="image type")
    create_parser.set_defaults(func=create_img)
    
    args = argparser.parse_args()
    args.func(args)
