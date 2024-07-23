#!/usr/bin/env python

import os
import sys
import subprocess
import traceback
import random
import time
import calendar
import datetime
import urllib.request

def readall_month_images():
  month_imgs = dict()
  os.makedirs('months', exist_ok=True)
  for month_i in range(1, 12):
    month_name = calendar.month_name[month_i]
    month_img_f = os.path.abspath(os.path.join('months', f'{month_i}.png'))
    if not os.path.exists(month_img_f):
      urllib.request.urlretrieve('https://picsum.photos/1200/900', month_img_f)

    month_imgs[month_i] = month_img_f

  return month_imgs



def main(args=sys.argv):
  os.chdir(os.path.abspath(os.path.dirname(__file__)))

  seed = int(os.environ.get('SEED', str(int(time.time())) ))
  year = int(os.environ.get('YEAR', str(int( datetime.datetime.now().year + 1 )) ))

  out_file = os.environ.get('OUT_FILE', os.path.join('out', f'cuckoo-{year}.pdf'))
  os.makedirs(os.path.dirname(out_file), exist_ok=True)

  # Print config
  print(f'SEED = {seed}')
  print(f'YEAR = {year}')
  print(f'OUT_FILE = {out_file}')

  # Perform generation!
  random.seed(seed)

  month_imgs = readall_month_images()
  print(f'month_imgs = {month_imgs}')





if __name__ == '__main__':
  main()
