# Extras

Some utility scripts I'm noodling around with for dealing with csv files output by pdfplumber. Not sure if they should really be here, but putting 'em here for the time being. Thus far they leave out numpy/pandas dependencies. 

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
Read a csv with pdfplumber:

	$ pdfplumber ../examples/1.27.16_Clinton_1362500_INV.pdf > 1.27.16_Clinton_1362500_INV.csv

Then pull out the words like this:

	$ python coalesce_words.py 1.27.16_Clinton_1362500_INV.csv > 1.27.16_Clinton_1362500_INV_words.csv