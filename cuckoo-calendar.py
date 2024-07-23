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
import webbrowser

os.chdir(os.path.abspath(os.path.dirname(__file__)))

site_packages = os.path.join(os.path.dirname(__file__), 'site-packages')
os.makedirs(site_packages, exist_ok=True)
sys.path.append(site_packages)

try:
  import fpdf
except:
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_packages}', 'fpdf2'
  ])
  import fpdf


try:
  import PIL
except:
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_packages}', 'pillow'
  ])
  import PIL

try:
  import colorthief
except:
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_packages}', 'colorthief'
  ])
  import colorthief


try:
  import joblib
except:
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_packages}', 'joblib'
  ])
  import joblib

cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
os.makedirs(cache_dir, exist_ok=True)
cache_me = joblib.Memory(cache_dir, verbose=0)


def readall_month_images():
  month_imgs = dict()
  os.makedirs('months', exist_ok=True)
  for month_i in range(0, 12):
    # month_name = calendar.month_name[month_i] # 0 == '', 1 == January.
    month_img_f = os.path.abspath(os.path.join('months', f'{month_i}.png'))
    if not os.path.exists(month_img_f):
      urllib.request.urlretrieve('https://picsum.photos/1200/900', month_img_f)

    month_imgs[month_i] = month_img_f

  return month_imgs

@cache_me.cache
def get_avg_color(path_to_img):
  return colorthief.ColorThief(path_to_img).get_color(quality=1)

@cache_me.cache
def get_pallet(path_to_img, color_count=3):
  return colorthief.ColorThief(path_to_img).get_palette(color_count=color_count, quality=1)

def invert_color(color):
  r, g, b = color
  return ( max(0, 255 - min(255, r)), max(0, 255 - min(255, g)), max(0, 255 - min(255, b)) )

def main(args=sys.argv):

  seed = int(os.environ.get('SEED', str(int(time.time())) ))
  year = int(os.environ.get('YEAR', str(int( datetime.datetime.now().year + 1 )) ))

  title_subtitle = os.environ.get('TITLE_SUBTITLE', f'A Calendar')

  out_file = os.environ.get('OUT_FILE', os.path.join('out', f'cuckoo-{year}.pdf'))
  os.makedirs(os.path.dirname(out_file), exist_ok=True)

  # Print config
  print(f'SEED = {seed}')
  print(f'YEAR = {year}')
  print(f'TITLE_SUBTITLE = {title_subtitle}')
  print(f'OUT_FILE = {out_file}')

  # Perform generation!
  random.seed(seed)

  month_imgs = readall_month_images()
  # print(f'month_imgs = {month_imgs}')

  pdf = fpdf.FPDF(orientation='landscape', format='A4', unit='in')

  # Margins are in inches b/c we passed unit='in' to constructor
  pdf.set_margins(
    # left, top, right
    0.75, 1.0, 0.75
  )

  # Title page - Front
  pdf.set_page_background(month_imgs[0])
  pdf.add_page()
  title_page_color = get_avg_color(month_imgs[0])
  title_page_pallet = get_avg_color(month_imgs[0])
  title_text_color = invert_color(title_page_color)

  year_x = random.uniform(0.9, 8.0)
  year_y = random.uniform(0.9, 6.0)

  pdf.set_font('helvetica', size=72)

  outline_offset = 0.014
  pdf.set_text_color(title_page_color)
  pdf.text(year_x-outline_offset, year_y-outline_offset, text=f'{year}')
  pdf.text(year_x-outline_offset, year_y+outline_offset, text=f'{year}')
  pdf.text(year_x+outline_offset, year_y-outline_offset, text=f'{year}')
  pdf.text(year_x+outline_offset, year_y+outline_offset, text=f'{year}')

  pdf.set_text_color(title_text_color)
  pdf.text(year_x, year_y, text=f'{year}')

  while True:
    subtitle_x, subtitle_alignment = random.choice([
      (0.75, 'L'),
      (9.25, 'R'),
    ])
    subtitle_y = random.uniform(0.9, 6.0)
    # If they are within 1.0 of the year_x/y, continue
    dist_to_year = abs(year_x-subtitle_x) + abs(year_y-subtitle_y)
    if dist_to_year > 4.0:
      break

  pdf.set_font('helvetica', size=24)

  outline_offset = 0.012
  cell_w = 0
  cell_h = 0
  pdf.set_text_color(title_page_color)
  pdf.set_x(subtitle_x-outline_offset) ; pdf.set_y(subtitle_y-outline_offset)
  pdf.cell(cell_w, cell_h, text=f'{title_subtitle}', align=subtitle_alignment)
  pdf.set_x(subtitle_x-outline_offset) ; pdf.set_y(subtitle_y+outline_offset)
  pdf.cell(cell_w, cell_h, text=f'{title_subtitle}', align=subtitle_alignment)
  pdf.set_x(subtitle_x+outline_offset) ; pdf.set_y(subtitle_y-outline_offset)
  pdf.cell(cell_w, cell_h, text=f'{title_subtitle}', align=subtitle_alignment)
  pdf.set_x(subtitle_x+outline_offset) ; pdf.set_y(subtitle_y+outline_offset)
  pdf.cell(cell_w, cell_h, text=f'{title_subtitle}', align=subtitle_alignment)

  pdf.set_text_color(title_text_color)
  pdf.set_x(subtitle_x) ; pdf.set_y(subtitle_y)
  pdf.cell(cell_w, cell_h, text=f'{title_subtitle}', align=subtitle_alignment)

  # End Title Front

  for month_i in range(1, 12):
    month_name = calendar.month_name[month_i] # 0 == '', 1 == January.

    # BACK of previous page, therefore the top-most page when calendar is hung.
    pdf.set_page_background(month_imgs[month_i])
    pdf.add_page()

    image_page_color = get_avg_color(month_imgs[month_i])
    image_page_pallet = get_avg_color(month_imgs[month_i])
    image_text_color = invert_color(image_page_color)

    month_x = random.uniform(0.9, 8.0)
    month_y = random.uniform(0.9, 6.0)

    pdf.set_font('helvetica', size=26)

    outline_offset = 0.009
    pdf.set_text_color(image_page_color)
    pdf.text(month_x-outline_offset, month_y-outline_offset, text=f'{month_name}')
    pdf.text(month_x-outline_offset, month_y+outline_offset, text=f'{month_name}')
    pdf.text(month_x+outline_offset, month_y-outline_offset, text=f'{month_name}')
    pdf.text(month_x+outline_offset, month_y+outline_offset, text=f'{month_name}')

    pdf.set_text_color(image_text_color)
    pdf.text(month_x, month_y, text=f'{month_name}')


    # Begin Front of bottom-most section
    pdf.set_page_background(None)
    pdf.add_page()
    pdf.set_font('helvetica', size=14)
    pdf.set_text_color((6, 6, 6))
    pdf.cell(text=f'S/M/Tu/W/Th/F/Sat, avg color = {get_avg_color(month_imgs[month_i])}\npallet = {get_pallet(month_imgs[month_i])}')

  # Finally, put this config on final page
  pdf.set_page_background(None)
  pdf.add_page()
  pdf.set_font('helvetica', size=14)
  pdf.set_text_color((6, 6, 6))
  pdf.cell(text=f'= = = = CONFIG = = = =')
  pdf.ln()
  pdf.cell(text=f'SEED = {seed}')
  pdf.ln()
  pdf.cell(text=f'YEAR = {year}')
  pdf.ln()
  pdf.cell(text=f'TITLE_SUBTITLE = {title_subtitle}')
  pdf.ln()
  pdf.cell(text=f'OUT_FILE = {out_file}')
  pdf.ln()

  pdf.output(out_file)

  print(f'Done! See {out_file}')

  webbrowser.open(f'{out_file}')





if __name__ == '__main__':
  main()

