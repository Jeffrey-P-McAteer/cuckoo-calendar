
# Cuckoo Calendar

python script(s) which generate a `.pdf` calendar of any given year,
with images from files like `months/1.png` becoming backdrops for `January`, `months/2.png` becomes `February`, etc.

If no image under `months/<N>.png` exists, one will randomly be downloaded from `https://picsum.photos` or similar.

# Running

```bash
# env vars which change behavior
SEED=<optional integer for repeatability>
YEAR=2032
TITLE_SUBTITLE='Text on cover page smaller than year'
OUT_FILE./path/to/output.pdf # default is out/cuckoo-<year>.pdf

# Edit/manually place images under months/<N>.png if you want
# to override a month's image. 0.png is the cover image.

# run the script
python cuckoo-calendar.py
```

# Dependencies

 - https://py-pdf.github.io/fpdf2/
 - https://github.com/fengsp/color-thief-py


# Cleanup

```bash
rm -rf cache months out
```


