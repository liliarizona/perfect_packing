#!/usr/bin/env python
import os
from os import listdir
from pickle import load
from pprint import pprint

def get_perfect_packing(file_name):
	perfect_packings = load(open(file_name,'rb'))	
	pprint(perfect_packings)
'''
    for destination in perfect_packings:
        perfect_packing_at_destination = perfect_packings[destination]
        for tree_idx in perfect_packing_at_destination:
            tree = perfect_packing_at_destination[tree_idx]
            for node in tree:
                print node, " successor node in tree is ", tree[node]
'''

def main():
    location = './lab-networks/'
    file_names = listdir(location)

    for file_name in file_names:
		print file_name
		get_perfect_packing(location + file_name)
		break
		
if __name__ == '__main__':
    main()
