import os

code_path = "./content/"

def get_full_code_history():
    file_path = code_path + "code_list.txt"
    result = None
    with open(file_path, 'r') as f:
        result = [line.split(' ') for line in f.readlines()]
        result.reverse()
    return result

def save_code_history(lst):
    file_path = code_path + "code_list.txt"
    with open(file_path, 'w') as f:
        for k in lst:
            f.write("%s %s\n" % (k[0], k[1]))