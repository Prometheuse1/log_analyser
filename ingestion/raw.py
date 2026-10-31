import gzip
import os
""" 
 read data logs from data directory as rows 
"""

def toRows(path):
    rows=[]
    files=os.listdir(path)
    for file in files :
        file_path=path+'/'+file
        openner=gzip.open(file_path,'rt') if file.endswith('.gz') else open(file_path)
        with openner as f:
            rows.extend(f.readlines())
    return rows

if __name__=='__main__':
    print(toRows('./data')[:10])