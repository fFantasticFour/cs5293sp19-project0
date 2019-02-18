This project code is a web scraping exercise in Python, using police records in Norman, OK.

Installation:
pipenv install .

Usage:
pipenv run python project0/main.py --arrests <url>

where <url> is the url containing police records, typically http://normanpd.normanok.gov/content/daily-activity

Testing:
By far the best test for the completeness of the data table, the quality of text splitting, etc. is to examine
the file.csv datafile created while executing the program. It contains all arrest records--all pages--for one week--all pdf files--held at the Norman PD website! And, it's spot-on!!!

In addition, use

pipenv run python -m pytest

Test functions:

test_list_sanity():
tests that the list of links is not empty

test_list_size():
tests whether the link scraper has returned 7 days worth of arrests

Using the file 'file.pdf'--arrests on 2/11--in the test directory
test_extract()
Tests whether the database has captured all 9 keys x 24 records = 216 cells

test_populate()
Tests whether the populated SQL database has the correct first record

test_random_title()
Tests whether the random record returned is of the correct size and type

Methods defined in project0.py:

The file ./Project0/project0.py defines several functions. Here are the modules used and my process while I was writing the code:

*fetchincidents(url)*
Look at the url defined in the input. Extract any html links which contain the word 'Arrest'--i.e. the arrest records of interest. The Norman PD changes these daily and generally retains seven days of historical data

The fetchincidents method uses BeautifulSoup to find html links within the page <url>. In addition, links are filtered through a regular expression for the word 'Arrest'

*extractincidents(List URLS)*
Using the list of URLs defined by the previous method, extractincidents seeks to parse the PDFs, combine them, and output a pandas data frame containing all arrest records held at the website at <url>

There were a number of difficulties with parsing Norman PD's arrest tables. First, some of the records are missing. Arrestees who are homeless
do not have an address, for example. Because of blanks in the row, you couldn't say that the 8th string over, say, was the ZIP code. Second, the text in each cell is wrapped, so that needed information appears on several rows.
Third, the table has no lines, so graphical methods like a hough transformation fail. These difficulties lead me two directions:

1) A pdf-to-string parser like pyPDF2, combined with Regular expressions. You could search for a record's ZIP code, for example, by looking for numerical strings with 5 digits. 
But, sometimes the data input by the Norman PD has typos--857060000 for example. And, more importantly, the regular expressions used would only apply to this particular project. 
I wanted to investigate methods of parsing that I could use again!

2) Modules for parsing tables like tabula, PDFminer, and camelot. I settled on Camelot, as it was written for python (unlike Tabula which is just a wrapper for a java method). As mentioned,
the PDF does not have lines, so camelot's more advanced flavor 'lattice' fails. Its other flavor 'stream' works by defining text edges where words begin or end and using those to create column positions.
This was a good start, but several of the records in the table are so close together that they don't look like text edges. I debugged the method visually by plotting the pdf in matplotlib and locating
the exact pixel positions of the columns. Then, I told camelot to split records so that strings of close words were placed into the appropriate column.

This works great, but I still had to address the text wrapping in cells. Camelot will put cells with more than one line in them into more than one row, which is not what I wanted. I had to write a little code
snippet to find stray information and put them into the cell it belongs to.

Finally, the parsed data table needed to be adjusted to fit into the format required by the assignment. The address is concatenated from separate address, city, state, zip keys into a single arrestee_address key.
Spelling is changed from the parsed PDF.

*createdb()*
Create a sqlite3 database using the file 'normanpd.db'

This method creates an SQL table to house the arrest data, using the sqlite3 module. It returns the connection to the file needed by later methods.

*populatedb(db, incidents)*
Bulk import the the data frame incidents into the SQL table db.

This method uses SQLalchemy to turn the pandas data frame into an sql database. I used a module because there are many keys and writing an SQL command for so many bindings would be lengthy and obtuse.
It places the data into the normanpd.db file and leaves the connection open for later use.

*fetchall(db)*
Print all records from the db

*status(db)*
Print a record from the db at random

