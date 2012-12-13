#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Osman Baskaya"


import os

input_path = "/data/datasets/training_set/"
output_file = "/data/datasets/netflix.csv"

os.chdir(input_path)

DELIMITER = ','

def main():
    
    files = os.listdir(input_path)
    files = (filename for filename in files if filename[-3:] == 'txt')
    
    with open(output_file, 'w') as outputfile:
        for i, filename in enumerate(files):
            f = open(filename, 'r')
            movieid = f.readline()
            movieid = movieid[:-2]
            for line in f.readlines():
                line = line.split(DELIMITER)
                userid, rat, date = line 
                line.insert(1, movieid)
                newline = ','.join(line[:-1])
                outputfile.write(newline + '\n')
            if i % 1000 == 0:
                print "%s files finished" % i
    

if __name__ == '__main__':
    main()

