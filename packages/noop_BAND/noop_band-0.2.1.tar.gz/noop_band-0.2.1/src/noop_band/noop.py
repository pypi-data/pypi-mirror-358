#!/usr/bin/env python

# noop.py - a NOOP program

import logging, os
logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper())

import traceback

def main():
    try:
        logging.info("nothing going on here")
    except Exception as e:
        traceback.print_exc(e)

if __name__ == "__main__":
    exit(main())
