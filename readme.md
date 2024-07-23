
# Cuckoo Calendar

python script(s) which generate a `.pdf` calendar of any given year,
with images from files like `months/1.png` becoming backdrops for `January`, `months/2.png` becomes `February`, etc.

If no image under `months/<N>.png` exists, one will randomly be downloaded from `https://picsum.photos` or similar.

# Dependencies

 - https://py-pdf.github.io/fpdf2/
 - https://github.com/fengsp/color-thief-py


# Cleanup

```bash
rm -rf cache months out
```


