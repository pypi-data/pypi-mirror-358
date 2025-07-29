import os as o0s
import pickle as p1k
import sys as s1s
import datetime as d7t
import logging as glng
import platform as plt
import random as rnd
from functools import wraps as wz
from time import sleep as t

logget = glng.getLogger
inflog = glng.INFO
strmhndl = glng.StreamHandler
fmtrbs = glng.Formatter

boink = o0s.path.join
path_exists = o0s.path.exists
path_join = o0s.path.join
list_dir = o0s.listdir
is_dir = o0s.path.isdir

plld = p1k.load

stdout = s1s.stdout

dt_y = d7t.date.today
dt_mk = d7t.date

plss = plt.system

ufrm = rnd.uniform
rnt = rnd.randint
chc = rnd.choice

wdeco = wz
