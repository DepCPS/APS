from iob_calculate import cal_iob_list
import os
import pandas as pd
import numpy as np

def find_filenames(path, suffix=".csv"):
    fileset = []
    
    for root, dirs, files in os.walk(path):
        for file in files:
                if file.endswith(suffix):
                        fileresult = os.path.join(root, file)
                        fileset.append(fileresult)
    
    return fileset

'''
This script calculates the IOB for extracted PSO3 data and
appends it to each csv as a new column.
'''
if __name__ == '__main__':
    file_path = 'PSO3_extracted_data/'
    filelist = find_filenames(file_path)
    print('Writing to', len(filelist), 'files')

    for i, file in enumerate(filelist):
        df = pd.read_csv(file)

        if 'IOB' in df.columns or len(df) == 0:
            continue
        
        df['IOB'] = cal_iob_list(df['rate'].tolist(), dia=3)        
        df.to_csv(file)
        
        if i > 0 and i % 1000 == 0:
            print('Passed through', i, 'files')

    print('Done!')
