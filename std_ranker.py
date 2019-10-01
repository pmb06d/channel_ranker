# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 10:57:50 2019

@author: pbonnin
"""

def get_filepath():
    import tkinter
    from tkinter import filedialog
    root = tkinter.Tk()
    root.withdraw()
    return(filedialog.askopenfilename())

# a function to get the number of lines to skip from the IBOPE csv's
def skipper(file):
    with open(file) as f:
        lines = f.readlines()
        # get list of all possible lines starting with quotation marks
        num = [i for i, l in enumerate(lines) if l.startswith('"')]
        
        # if not found value return 0 else get first value of list subtracted by 1
        num = 0 if len(num) == 0 else num[0]
        return(num)

# a function to clean the numeric features from the csv
def clean_features(test_list, cleaned_features=False):
    import re
    temp = []
    temp2 = []
  
    for i in test_list:
        try:
            temp.append(re.findall('^\w+[\%\#]\w*',i)[0])
        except:
            temp.append(i)
      
    for i in test_list:
        if bool(re.match('^\w+[\%\#]\w*',i)) == True:
            temp2.append(re.findall('^\w+[\%\#]\w*',i)[0])
  
    if cleaned_features == True:
        return(temp2, temp)
    else:
        return(temp)
  

def to_numeric(feature_name,data):
    import pandas as pd
    data.loc[:,feature_name] = data.loc[:,feature_name].astype(str)
    data.loc[:,feature_name] = data.loc[:,feature_name].str.replace(r'^[Nn]\/*\.*[Aa]\.*[Nn]*$','0', regex=True)
    data.loc[:,feature_name] = data.loc[:,feature_name].str.replace(',','', regex=True)
    return(pd.to_numeric(data.loc[:,feature_name]))


def preproc_ranker(a_dataframe, export_ranking_features=True, convert_date=True):
    import pandas as pd
    
    temp_df = a_dataframe.copy()
    
    try:
        temp_df.drop([' '], axis=1, inplace=True)
    except:
        pass
    
    temp_df.loc[:,'Target'] = temp_df.loc[:,'Target'].str.replace('Live / ', '', regex=True)
    temp_df.loc[:,'Channel'] = temp_df.loc[:,'Channel'].str.replace(' (MF)', '', regex=False)
    facts, all_columns = clean_features(list(temp_df), cleaned_features=True)
    temp_df.columns = clean_features(all_columns)
    temp_df = temp_df.dropna(how='all')
    
    for col in facts:
        try:
            temp_df.loc[:,col] = to_numeric(col,temp_df)
        except:
            temp_df.loc[:,col] = to_numeric(col,temp_df.loc[:,col].str.replace('n.a','0', regex=False))
            
    for col in all_columns:
        if col == 'Date' and convert_date == True:
            temp_df.loc[:,col] = pd.to_datetime(temp_df.loc[:,col])
        elif col == 'Year':
            temp_df.loc[:,col] = temp_df.loc[:,col].astype('int')
        else:
            continue
    
    info = pd.DataFrame(temp_df.dtypes).reset_index()
    info = list(info.loc[info[0]!='float64','index'])
    info.remove('Channel')
    
    if export_ranking_features == True:
        return(info, temp_df)
    else:
        return(temp_df)


# Pre-processing
def main(file_path):
    
    import pandas as pd
    import time
    import warnings
    
    warnings.filterwarnings("ignore")
    start_time = time.time()

    df = pd.read_csv(file_path,delimiter=';',skiprows=skipper(file_path),encoding='latin1')
    ranking_features, df = preproc_ranker(df, convert_date=False)

    # Adding a ranking variable
    df['Rank_Rat%'] = df.groupby(ranking_features)['Rat%'].rank(ascending=False,method='first')
    
    df = df.replace(to_replace='(?<=\[TOTAL\])(.+)',value='', regex=True)

    # Export back out for delivery

    output = file_path.replace('.csv','')+' (Processed).csv'
    df.to_csv(path_or_buf=output, sep=',', index=False)
    
    print('\n',"--- %s seconds ---" % (time.time() - start_time))
    print('Your file can be found at:',output)
    
if __name__== "__main__":
  main(get_filepath())
