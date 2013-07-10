#!/usr/bin/env python

import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import util

session = util.load_session()
util.update_startup_info(session)
session.close()
