# -*- coding: utf-8 -*-
import re
import urllib.request as ur
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader, PdfFileWriter
from camelot import read_pdf
import tempfile
import numpy as np
import csv, sqlite3
import sqlalchemy
import random

def fetchincidents(url2):
#Find all links at the specified URL. Then, use Beautiful Soup to search for all links that contain the word 'Arrest'
#Return the needed html links as a list.

    data = ur.urlopen(url2).read()
    soup = BeautifulSoup(data, features="html.parser")
    List = []
    for link in soup.find_all("a", href = re.compile("Arrest")):
        current_link = link.get('href')
        List.append("http://normanpd.normanok.gov" + current_link)
    return List

#Open the arrest files, parse the tables, and return a pandas data frame.
def extractincidents(List):

    data = ur.urlopen(List[0])
    testfile = ur.URLopener()
    testfile.retrieve(List[0], "file.pdf")
    #Create the df for allArrests...we just want the structure of whatever is in there, 
    #so make a df with that form and then delete all the data in it
    df = read_pdf("file.pdf", flavor = 'stream', columns=['112,162,241,342,425,465,525,570,599,634,685'],split_text=True,pages='1')
    allArrests = df[0].df
    #header = allArrests.iloc[2,:]
    #header[5] = 'Arestee Birthday'
    header = ['arrest_time','case_number','arrest_location','offense','arrestee_name','arrestee_birthday','arrestee_address','City','State','Zip','status','officer']
    allArrests.drop(allArrests.index, inplace=True)
#Loop through all URLs found in the list 
    for urlNum in range(0,len(List),1):
#    for urlNum in range(0,1,1):

    #Open a URL in the list of URLs
        data = ur.urlopen(List[urlNum])
        testfile = ur.URLopener()
        testfile.retrieve(List[urlNum], "file.pdf")
    #Create a temporary file for pdfReader
        fp = tempfile.TemporaryFile()
        fp.write(data.read())
        fp.seek(0)
    #Extract the number of pages in the PDF
        pdfReader = PdfFileReader(fp)
        pages = PdfFileReader(fp).getNumPages()

    #An alternative method of parsing the PDF is below
    #    page1 = pdfReader.getPage(0).extractText()

    #    content = ""

    #    for i in range (0, pdfReader.getNumPages()):
    #        extractedText = pdfReader.getPage(i).extractText()
    #        content += extractedText + "\n"

    #    content = " ".join(content.replace("\xa0", " ").strip().split())

        for pageNum in range(1,pages+1,1):
#Use CAMELOT to parse the table. In this case, the parsing isn't prefect, however: there are no lines in the table for the lattice method to look for, and text spans multiple rows.
#And it gets worse! CAMELOT attempts to define rows by looking for consistent edges in texts, and the tables given run text so close together that CAMELOT
#thinks they're one column. So, visually debugging was done by extracting column pixel positions from a plot.
            df = read_pdf("file.pdf", flavor = 'stream', columns=['112,162,241,342,425,465,525,570,599,634,685'],split_text=True,pages=str(pageNum))
            print('Now parsing page: ' + str(pageNum) + ' on PDF number: ' + str(urlNum+1) + ' out of ' + str(len(List)))
        
        #CAMELOT does a good job, but returns spanning text above and below the record. The following code:
        #*finds the blanks in a record
        #*fills the blanks with the record above and below
        #*continues until there are no more inappropriate NAs
            nadf = df[0].df.replace('',np.nan)
            tocat = np.where(nadf.notna().iloc[:,0])[0]
            for i in tocat[::-1]:
                if (i+1 in df[0].df.index and i-1 in df[0].df.index and nadf.notna().iloc[i+1,0]==False and nadf.notna().iloc[i-1,0]==False):
                    #concatenate above and below
                    df[0].df.iloc[i,:]=df[0].df.iloc[i-1,:]+' '+df[0].df.iloc[i,:]+df[0].df.iloc[i+1,:]
                    #Strip off unnecessary spaces
                    df[0].df.iloc[i,:]=df[0].df.iloc[i,:].map(lambda x: x.strip())
                    #Remove the concatenated rows
                    df[0].df=df[0].df.drop([i-1,i+1],axis=0)

            df[0].df = df[0].df.reset_index(drop=True)
        #Second loop for more blank lines
            nadf = df[0].df.replace('',np.nan)
            tocat = np.where(nadf.notna().iloc[:,0])[0]
            for i in tocat[::-1]:
                if (i+1 in df[0].df.index and i-1 in df[0].df.index and nadf.notna().iloc[i+1,0]==False and nadf.notna().iloc[i-1,0]==False):
                    df[0].df.iloc[i,:]=df[0].df.iloc[i-1,:]+' '+df[0].df.iloc[i,:]+' '+df[0].df.iloc[i+1,:]
                    df[0].df.iloc[i,:]=df[0].df.iloc[i,:].map(lambda x: x.strip())
                    df[0].df=df[0].df.drop([i-1,i+1],axis=0)

            df[0].df = df[0].df.reset_index(drop=True)

        #Drop the header and any rows that don't contain data
            nadf = df[0].df.replace('',np.nan)
            tocat = np.where(nadf.isna().iloc[:,0])[0]
            for i in tocat[::-1]:
                    df[0].df=df[0].df.drop([i],axis=0)

            df[0].df = df[0].df[~df[0].df[0].str.contains('Arrest')]
            df[0].df = df[0].df.reset_index(drop=True)

        #Append the current page to the growing dataframe of all arrests held at the Norman splash page
            allArrests = allArrests.append(df[0].df)
    #Format the columns to match what's required in the key for the SQLite database
    allArrests.columns = header
    allArrests['arrestee_address'] = allArrests['arrestee_address'] + ' ' + allArrests['City'] + ' ' + allArrests['State'] + ' ' + allArrests['Zip']
    allArrests['arrestee_address'] = allArrests['arrestee_address'].map(lambda x: x.strip())
    allArrests.drop(['City','State','Zip'], axis=1, inplace = True)
#Prepend the header to the dataframe of all arrests at the Norman splash page
#    allArrests = allArrests.reset_index(drop = True)
#    allArrests.loc[-1] = header
#    allArrests.index = allArrests.index + 1
#    allArrests = allArrests.sort_index()

#Output every arrest on the Norman police page as a CSV; used for testing and debugging
    allArrests.to_csv("file.csv")

    return allArrests

#Create an SQLite3 database with the required form
def createdb():
    connection = sqlite3.connect("normanpd.db")

    cursor = connection.cursor()
    # delete 
    cursor.execute("""DROP TABLE IF EXISTS arrests;""")

    sql_command = """
    CREATE TABLE IF NOT EXISTS arrests (
    arrest_time TEXT,
    case_number TEXT,
    arrest_location TEXT,
    offense TEXT,
    arrestee_name TEXT,
    arrestee_birthday TEXT,
    arrestee_address TEXT,
    status TEXT,
    officer TEXT);"""
    cursor.execute(sql_command) 
    connection.commit()
    
    return connection

#Put the data frame df into the create database
def populatedb(df, conn):
    #The below is an alternative if you do no wish to pass the connection to the function
   # engine = sqlalchemy.create_engine('sqlite:///normanpd.db')
   # df.to_sql('arrests',con=engine,if_exists='append', index=False)
    df.to_sql('arrests',con=conn,if_exists='append', index=False)
    #conn.close()

#Open the database file and print all records
def fetchall(connection):
    #connection = sqlite3.connect("normanpd.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM arrests")
    print("Printing all records in database:")
    result = cursor.fetchall()
    for r in result:
        print(r)
    #connection.close()

#Open the database file and print one random record in the databse
def status(connection):
    #connection = sqlite3.connect("normanpd.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM arrests")
    print("Printing random record from database:")
    result = cursor.fetchall()
    r = random.choice(result)
    for p in r:
        print(p, end='')
        print('\xfe',end='')
    print('\n')
    return r
    #connection.close()

