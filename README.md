
Some utility scripts I'm noodling around with for helping standardize word-based output into a csv format. In general there are three cases I want to address: 1. text-based pdfs, 2. pdfs that have already been OCR'ed and had text 'attached' to them, and 3. image-based pdfs that need to be scanned. For cases 1. and 2. the first step is to use jsvine's convenient PDFMiner wrapper [pdfplumber](https://github.com/jsvine/pdfplumber), to output the character-bounding boxes, and then coalesce them into words. Coalesce_words.py assumes the output of pdfplumber. 

The same approach will work for #2 if we know that the pdfs are not rotated. More complex tooling is needed if the pdfs are rotated.

For case #3 we're going to assume that the pdfs have been tesseracted, and we're dealing with .html files in HOCR format. Tessereact is not necessarily the best choice for high-quality OCR, but it's freely available… 
 

## coalesce_words.py

	usage: coalesce_words [-h] [--pages PAGES [PAGES ...]]
	                      [--precision {0,1,2,3,4}] [--format {csv,json}]
	                      [infile]
	
	positional arguments:
	  infile
	
	optional arguments:
	  -h, --help            show this help message and exit
	  --pages PAGES [PAGES ...]
	  --precision {0,1,2,3,4}
	  --format {csv,json}
 

Reads a csv of single letters (such as is output by pdfplumber) and outputs a similarly formatted file of words with some fairly strict assumptions: that char y0s are the same when rounded to `--precision` precision, and that words are separated by a space character or are physically separated by a distance greater than a third of the font height. This heuristic is just a guess, and might need to change. 

These assumptions *may not* hold for pdfs that have OCR'ed text attached to them, and won't work if the text is slanted. 

### example usage:
The file `../examples/1.27.16_Clinton_1362500_INV.csv` is pdfplumber's output of `../examples/1.27.16_Clinton_1362500_INV.pdf`. It consists of a .csv file with one line per character (or a few other detected types) and a bounding box defined by x0, x1, y0 and y1 for each char. To get word-level bounding boxes, run:



	$ python coalesce_words.py ../examples/1.27.16_Clinton_1362500_INV.csv > 1.27.16_Clinton_1362500_INV_words.csv