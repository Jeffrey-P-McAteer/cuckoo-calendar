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

try:
  import colormath
  import colormath.color_objects # using  sRGBColor, LabColor
  import colormath.color_conversions # using  convert_color
  import colormath.color_diff # using  delta_e_cie2000
except:
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_packages}', 'colormath'
  ])
  import colormath
  import colormath.color_objects # using  sRGBColor, LabColor
  import colormath.color_conversions # using  convert_color
  import colormath.color_diff # using  delta_e_cie2000

try:
  # colormath needs to update the numpy functions they're using, but for now we monkey-patch numpy.
  import numpy
  def patch_asscalar(a):
      return a.item()
  setattr(numpy, "asscalar", patch_asscalar)
except:
  traceback.print_exc()


try:
  import dateparser
except:
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_packages}', 'dateparser'
  ])
  import dateparser

cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
os.makedirs(cache_dir, exist_ok=True)
cache_me = joblib.Memory(cache_dir, verbose=0)


def readall_month_images(flip_month_imgs=False):
  month_imgs = dict()
  os.makedirs('months', exist_ok=True)
  for month_i in range(0, 13):
    # month_name = calendar.month_name[month_i] # 0 == '', 1 == January.
    month_img_f = os.path.abspath(os.path.join('months', f'{month_i}.png'))
    if not os.path.exists(month_img_f):
      urllib.request.urlretrieve('https://picsum.photos/1200/900', month_img_f)

    month_imgs[month_i] = month_img_f

    if flip_month_imgs:
      if month_i >= 1:
        # Flip all month photos!
        flipped_img = os.path.abspath(os.path.join('months', f'{month_i}.flip.png'))
        if not os.path.exists(flipped_img):
          img = PIL.Image.open(month_img_f)
          im_flip = PIL.ImageOps.flip(img)
          im_flip.save(flipped_img)

        month_imgs[month_i] = flipped_img

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

def color_similarity(color1, color2):
  return colormath.color_diff.delta_e_cie2000(
    colormath.color_conversions.convert_color(
      colormath.color_objects.sRGBColor(color1[0], color1[1], color1[2], is_upscaled=True),
      colormath.color_objects.LabColor
    ),
    colormath.color_conversions.convert_color(
      colormath.color_objects.sRGBColor(color2[0], color2[1], color2[2], is_upscaled=True),
      colormath.color_objects.LabColor
    )
  )

# Converter to get Sunday == 0, Monday == 1, Tuesday == 2, .. until Saturday == 6
def weekday_to_dow_idx(weekday):
  return (weekday + 1) % 7

def main(args=sys.argv):

  seed = int(os.environ.get('SEED', str(int(time.time())) ))
  year = int(os.environ.get('YEAR', str(int( datetime.datetime.now().year + 1 )) ))

  title_subtitle = os.environ.get('TITLE_SUBTITLE', f'A Calendar')

  out_file = os.environ.get('OUT_FILE', os.path.join('out', f'cuckoo-{year}.pdf'))
  if not out_file.lower().endswith(".pdf"):
    print(f'[ ERROR ] OUT_FILE must end in ".pdf"! (OUT_FILE = {out_file})')
    return

  os.makedirs(os.path.dirname(out_file), exist_ok=True)

  # Print config
  print(f'SEED = {seed}')
  print(f'YEAR = {year}')
  print(f'TITLE_SUBTITLE = {title_subtitle}')
  print(f'OUT_FILE = {out_file}')

  # Perform generation 2X!
  out_file_and_flip_states = [
    (out_file,                        False),
    (out_file[:-4]+'.print-flip.pdf', True)
  ]

  for out_file, flip_month_imgs in out_file_and_flip_states:

    #random.seed(seed)
    rand = random.Random()
    rand.seed(seed)

    month_imgs = readall_month_images(flip_month_imgs=flip_month_imgs)
    # print(f'month_imgs = {month_imgs}')

    pdf = fpdf.FPDF(orientation='landscape', format='A4', unit='in')

    # Margins are in inches b/c we passed unit='in' to constructor
    pdf.set_margins(
      # left, top, right
      0.75, 1.0, 0.75
    )
    # pdf.epw & pdf.eph hold our unit dimensions!

    # Title page - Front
    pdf.set_page_background(month_imgs[0])
    pdf.add_page()
    title_page_color = get_avg_color(month_imgs[0])
    title_page_pallet = get_pallet(month_imgs[0], color_count=4)
    #title_text_color = invert_color(title_page_color)
    title_text_color = invert_color(rand.choice(title_page_pallet))
    title_text_outline_possibilities = [ c for c in title_page_pallet if color_similarity(c, title_text_color) > 20.0 ]
    if len(title_text_outline_possibilities) < 1:
      title_text_outline_possibilities.append( title_page_color )
    title_text_outline = rand.choice(title_text_outline_possibilities)

    year_x = rand.uniform(0.9, 6.6)
    year_y = rand.uniform(1.3, 6.0)

    pdf.set_font('helvetica', size=164)

    outline_offset = 0.014
    pdf.set_text_color(title_text_outline)
    pdf.text(year_x-outline_offset, year_y-outline_offset, text=f'{year}')
    pdf.text(year_x-outline_offset, year_y+outline_offset, text=f'{year}')
    pdf.text(year_x+outline_offset, year_y-outline_offset, text=f'{year}')
    pdf.text(year_x+outline_offset, year_y+outline_offset, text=f'{year}')

    pdf.set_text_color(title_text_color)
    pdf.text(year_x, year_y, text=f'{year}')

    while True:
      subtitle_x, subtitle_alignment = rand.choice([
        (0.75, 'L'),
        (9.25, 'R'),
      ])
      subtitle_y = rand.uniform(0.9, 6.0)
      # If they are within 1.0 of the year_x/y, continue
      dist_to_year = abs(year_x-subtitle_x) + abs(year_y-subtitle_y)
      if dist_to_year > 7.0:
        break

    title_subtitle_size_pt = 32
    pdf.set_font('helvetica', size=title_subtitle_size_pt)


    title_subtitle_h, title_subtitle_w = pdf.current_font.get_text_width(f'{title_subtitle}', title_subtitle_size_pt, {})
    subtitle_alinment_offset = 0.0
    if subtitle_alignment == 'R':
      subtitle_alinment_offset = -(title_subtitle_w / 150.0) # 300.0 points-per-inch?

    outline_offset = 0.008
    pdf.set_text_color(title_text_outline)
    pdf.text((subtitle_x-outline_offset)+subtitle_alinment_offset, subtitle_y-outline_offset, text=f'{title_subtitle}')
    pdf.text((subtitle_x-outline_offset)+subtitle_alinment_offset, subtitle_y+outline_offset, text=f'{title_subtitle}')
    pdf.text((subtitle_x+outline_offset)+subtitle_alinment_offset, subtitle_y-outline_offset, text=f'{title_subtitle}')
    pdf.text((subtitle_x+outline_offset)+subtitle_alinment_offset, subtitle_y+outline_offset, text=f'{title_subtitle}')

    pdf.set_text_color(title_text_color)
    pdf.text(subtitle_x+subtitle_alinment_offset, subtitle_y, text=f'{title_subtitle}')


    # End Title Front

    single_day_padding=(0.02, 0.08, 0.6, 0.02) # top, right, bottom, and left in... inches?

    # We begin January 1, and keep track of that plus any deltas we want to apply.
    # Early on it is important that the days follow eachother, but we have additional dimensions to mess
    # with as the year goes on!
    today = datetime.datetime(year, 1, 1, 0, 0, 0)
    today_render_delta = datetime.timedelta(days=0)

    cuckoo_begin_date = dateparser.parse(
      os.environ.get('CUCKOO_BEGIN', 'in 1 month'),
      settings={
        'RELATIVE_BASE': today,
        'PREFER_DATES_FROM': 'future',
      }
    )
    print(f'CUCKOO_BEGIN = {cuckoo_begin_date}')
    cuckoos_performed = []

    num_skipped_days_at_month_break = 0

    for month_i in range(1, 13):
      month_name = calendar.month_name[month_i] # 0 == '', 1 == January.

      # BACK of previous page, therefore the top-most page when calendar is hung.
      pdf.set_page_background(month_imgs[month_i])
      pdf.add_page()

      page_rotation_angle = 0
      if flip_month_imgs:
        page_rotation_angle = 180

      with pdf.rotation(angle=page_rotation_angle, x=(pdf.epw + pdf.l_margin + pdf.r_margin)/2.0, y=(pdf.eph + pdf.t_margin + pdf.b_margin)/2.0):

        image_page_color = get_avg_color(month_imgs[month_i])
        image_page_pallet = get_pallet(month_imgs[month_i], color_count=3)
        #image_text_color = invert_color(image_page_color)
        image_text_color = rand.choice(image_page_pallet)
        title_text_outline_possibilities = [ c for c in image_page_pallet if color_similarity(c, image_text_color) > 20.0 ]
        if len(title_text_outline_possibilities) < 1:
          title_text_outline_possibilities.append( title_page_color )
        title_text_outline = rand.choice(title_text_outline_possibilities)

        month_x = rand.uniform(0.9, 7.0)
        month_y = rand.uniform(0.9, 6.0)

        pdf.set_font('helvetica', size=78)

        outline_offset = 0.009
        pdf.set_text_color(title_text_outline)
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

      # Create a 7x4 grid
      with pdf.table() as table:
        day_of_week_row = table.row()

        for day_of_week in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
          day_of_week_row.cell(f'{day_of_week}')

        skip_a_day = False
        if today >= cuckoo_begin_date:
          if rand.choice([True] + (1*[False])):
            num_skipped_days_at_month_break += 1
            skip_a_day = True
            cuckoos_performed.append(f'Skipping a day at {today}')

        # We render here so we can remove empty weeks / fix up any chaos
        month_day_nums_grid = []

        for row_i in range(0, 6):
          week_of_day_nums = []
          for day_of_week_i in range(0, 7):
            if (today+today_render_delta).month == month_i and weekday_to_dow_idx((today).weekday()) == day_of_week_i:
              if skip_a_day:
                skip_a_day = False
                today_render_delta -= datetime.timedelta(days=1)
                week_of_day_nums.append('')
              else:
                week_of_day_nums.append(f'{(today+today_render_delta).day}')
              today = today + datetime.timedelta(days=1) # always advance time 1 day
            else:
              week_of_day_nums.append('')

          month_day_nums_grid.append(week_of_day_nums)

          if (today+today_render_delta).month != month_i:
            break


        if all(len(t) < 1 for t in month_day_nums_grid[0]):
          month_day_nums_grid = month_day_nums_grid[1:] # remove first week if all text is empty

        # Do the pdf table render
        for week_of_day_nums in month_day_nums_grid:
          row = table.row()
          for day_text in week_of_day_nums:
            row.cell(f'{day_text}', padding=single_day_padding)

    for c in cuckoos_performed:
      print(c)

    # Finally, put this config on final page
    pdf.set_page_background(None)
    pdf.add_page()
    pdf.set_font('helvetica', size=12)
    pdf.set_text_color((6, 6, 6))
    pdf.cell(text=f'= = = = CONFIG = = = =')
    pdf.ln()
    pdf.cell(text=f'SEED = {seed}')
    pdf.ln()
    pdf.cell(text=f'YEAR = {year}')
    pdf.ln()
    pdf.cell(text=f'TITLE_SUBTITLE = {title_subtitle}')
    pdf.ln()
    pdf.cell(text=f'CUCKOO_BEGIN = {cuckoo_begin_date}')
    pdf.ln()
    pdf.cell(text=f'OUT_FILE = {out_file}')
    pdf.ln()
    pdf.ln()
    pdf.cell(text=f'= = = = CUCKOOS = = = =')
    pdf.ln()
    for c in cuckoos_performed:
      pdf.cell(text=f'{c}')
      pdf.ln()

    pdf.output(out_file)

    print(f'Done! See {out_file}')

    webbrowser.open(f'{out_file}')





if __name__ == '__main__':
  main()

