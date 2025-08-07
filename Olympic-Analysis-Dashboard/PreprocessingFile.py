import pandas as pd
import numpy as np



def dataCleaner(df,reg,default = None):
    df = pd.merge(df, reg, on='NOC', how='left')
    df = df[df['Season'] == 'Summer']
    df = df.drop_duplicates()
    if default == 'athWise':
        return df
    if default == 1:                                  # For Choosing unique Sports with region
        return df
    df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'Season', 'City', 'Sport', 'Event', 'Medal'])
    if default == 'cw':                               # country wise Analysis
        df = df.dropna(subset = ['Medal'])
        return  df

    df = pd.get_dummies(data=df, columns=['Medal'])
    new_column_names = {'Medal_Bronze': 'Bronze', 'Medal_Gold': 'Gold', 'Medal_Silver': 'Silver'}
    df = df.rename(columns=new_column_names)
    return df

