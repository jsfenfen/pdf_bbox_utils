"""
Turn characters into words with a set of very strong assumptions:

This will probably not work for documents where the text has been created
from OCR, or where text is not aligned vertically.

"""

import argparse, csv, sys, json

# Because we're outputting to stdout, setting to true will hose the output. 
debug = False

# not sure where this should come from, but
RETURN_PRECISION = 3

# We prob don't wanna return all of these, just leaving them in for now. 
fieldnames = ['adv', 'fontname', 'linewidth', 'pageid', 'doctop', 'text', 'top', 'object_type', 'height', 'upright', 'width', 'y1', 'y0', 'x0', 'x1', 'size']


# cut n' paste from pdfplumbers cli.py
def parse_page_spec(p_str):
    if "-" in p_str:
        return list(range(*map(int, p_str.split("-"))))
    else: return [ int(p_str) ]
    
def parse_args():
    parser = argparse.ArgumentParser("coalesce_words")

    stdin = (sys.stdin.buffer if sys.version_info[0] >= 3 else sys.stdin)
    parser.add_argument("infile", nargs="?",
        type=argparse.FileType("r"),
        default=stdin)    
    
    parser.add_argument("--pages", nargs="+",
        type=parse_page_spec)
    
    parser.add_argument('--precision', 
        default=1,
        choices=(0,1,2,3,4),
        type=int)
    
    parser.add_argument("--format",
        action="store",
        dest="format",
        choices=["csv", "json"],
        default="csv")
    
    args = parser.parse_args()
    return args


def get_chars_hashed_by_yoffset(csv_reader, precision, pages=None):
    """ Hash the characters by the y-offset height rounded to [precision] decimals. """ 
    line_hash = {}
    
    for i, row in enumerate(csv_reader):
        if pages:
            if int(row['pageid']) not in pages:
                continue
        
        if row['object_type'] == 'char':
            
            y_rounded = round(float(row['y0']), precision)

            hash_key = "%s@%s" % (row['pageid'], y_rounded)
            try:
                line_hash[hash_key]['count'] += 1
                line_hash[hash_key]['chars'].append(row)

            except KeyError:
                line_hash[hash_key] = {'count':1, 'chars':[row]}
 
    return line_hash

def coalesce_into_words(char_height_dict):
    """ Takes a dictionary of characters--where the key is the shared baseline and the value is an array of chars. Returns an array of words, where each word is an array or chars. This doesn't preserve lines, though we're assuming that's not a problem.  """
    result_word_lines = []
    
    for char_height_key in char_height_dict.keys():
        sorted_chars = sorted(char_height_dict[char_height_key]['chars'], key=lambda k: float(k['x0']))
        if len(sorted_chars) == 1:
            result_word_lines.append([sorted_chars[0]])
            continue
            
        else:
            cur_word_start = 0
            this_current_word = []
            
            is_word_boundary = False
            last_char_x1 = float(sorted_chars[0]['x1'])
            last_char_height = float(sorted_chars[0]['height'])
            for i, char in enumerate(sorted_chars):
                
                separation_width = float(char['x0'])-last_char_x1
                relevant_char_height = last_char_height
                
                last_char_x1 = float(char['x1'])
                last_char_height = float(char['height'])
               
                if char['text'] == ' ' or separation_width > relevant_char_height/3:
                    if this_current_word:
                        
                        result_word_lines.append(this_current_word)
                        if (debug):
                            prospective_word = "".join([i['text'] for i in this_current_word])
                            print("***Prospective word: '%s'" % prospective_word)

                        this_current_word = []
                        
                    if char['text'] != ' ':
                        this_current_word.append(char)
                       
                else:
                    if char['text'] != ' ':
                        this_current_word.append(char)
            
            if this_current_word:
                result_word_lines.append(this_current_word)
                if (debug):
                    prospective_word = "".join([i['text'] for i in this_current_word])
                    print("***Prospective word: '%s'" % prospective_word)
            

    
    return result_word_lines

def merge_word_arrays(words_by_array):
    word_array = []
    for i, line in enumerate(words_by_array):
        word_length = len(line)
        this_word = {}
        
        last_char = line[-1:][0]
        first_char = line[0]
        
        y1 = max([float(i['y1']) for i in line])
        y0 = min([float(i['y0']) for i in line])
        this_word_text = "".join([i['text'] for i in line]).strip()
        width = round(float(last_char['x1']) - float(first_char['x0']),RETURN_PRECISION)
        
        # just use the pageid, doctop, upright, fontname of the first char for the word
        # May not be a good assumption.
        word_array.append({'adv':first_char['adv'], 'fontname':first_char['fontname'], 'linewidth':None, 'pageid':first_char['pageid'], 'doctop':first_char['doctop'], 'text':this_word_text, 'top':first_char['top'], 'object_type':'word', 'height':first_char['height'], 'upright':first_char['upright'], 'width':width, 'y1':y1, 'y0':y0, 'x0':first_char['x0'], 'x1':last_char['x1'], 'size':round(y1-y0,RETURN_PRECISION)})

    return word_array

def to_csv(word_list, output):
    output.write(",".join(fieldnames) + "\n")
    dictwriter = csv.DictWriter(output, fieldnames=fieldnames, restval='', extrasaction='ignore')
    for word in word_list:
        dictwriter.writerow(word)
    
def to_json(word_list, output):
    output.write(json.dumps(word_list))

def process_file(infile, outfile, precision=1, format='csv', pages=None):
    
    reader = csv.DictReader(infile)
    char_height_dict = get_chars_hashed_by_yoffset(reader, precision, pages=pages)
    
    # page numbers come back as strings
    #pages_to_read = ['1']
    
    words_by_array = coalesce_into_words(char_height_dict)
    word_list = merge_word_arrays(words_by_array)
    
    if format=='csv':
        to_csv(word_list, outfile)
    
    elif format=='json':
        to_json(word_list, outfile)
    
    return 1


def main():
    args = parse_args()
    
    if (debug):
        print("args are: ", args)
    
    # argparser gives pages as [[x]] or [[x,y,z]], so pass pages[0]
    page_list = args.pages[0] if args.pages else None
    process_file(args.infile, sys.stdout, precision=args.precision, format=args.format, pages=page_list)
    

if __name__ == "__main__":
    main()
