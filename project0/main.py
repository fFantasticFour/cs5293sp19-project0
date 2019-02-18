# -*- coding: utf-8 -*-
# Brandon Wolfe's main.py for project0 in cs5293
url2 = ("http://normanpd.normanok.gov/content/daily-activity")

import project0
import argparse

def main(url):
    # Download data
    print("Here are the Arrest record URLs fetched from the Norman PD:\n")
    print(project0.fetchincidents(url))
    print("\n")

    # Extract Data
    df = project0.extractincidents(project0.fetchincidents(url))
    print("\nHere are the first 5 records in the database stored from the Norman PD's arrest records:\n")
    print(df.head())
    print("\n")

    # Create Dataase
    conn = project0.createdb()
    # Insert Data
    project0.populatedb(df, conn)
    # Print Status
    randomrecord = project0.status(conn)
    print(randomrecord[0])
    type(randomrecord[0])

    # Create Dataase
#    db = project0.createdb()
	
    # Insert Data
#    project0.populatedb(db, incidents)
	
    # Print Status
#    project0.status(db)


if __name__ == '__main__':
#    main(url2)
    parser = argparse.ArgumentParser()
    parser.add_argument("--arrests", type=str, required=True, 
                         help="The arrest summary url.")
    
    args = parser.parse_args()
    if args.arrests:
        main(args.arrests)
