import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_style('darkgrid')

"""constants"""

file_path = fr'raw/USGasData.xlsx'
tabs = ['Storage', 'Production', 'Demand-Actual', 'Demand-Normal', 'Prices-Cash', 'Prices-Cash Basis']
pickle_files = ['storage.pkl', 'production.pkl', 'demand_actual.pkl', 'demand_normal.pkl', 'prices.pkl', 'basis.pkl']
cap = 30
cap_prices = True
read_pickle = False

"""helpers"""

def map_month_to_season(month):
    if month in [3, 4, 5]:   # Spring: March, April, May
        return 'Spring'
    elif month in [6, 7, 8]: # Summer: June, July, August
        return 'Summer'
    elif month in [9, 10, 11]:  # Fall: September, October, November
        return 'Fall'
    else:  # Winter: December, January, February
        return 'Winter'


def read_gas_data(file_path, cap_prices, cap, read_pickle=False):
    
    dfs = {}
    
    if read_pickle==True:
        for pickle_file, tab in zip(pickle_files, tabs):
            with open(fr'pickles/{pickle_file}', 'rb') as f:
                dfs[tab] = pd.read_pickle(f).sort_index()
    else:
        for i, tab in enumerate(tabs):
            df = pd.read_excel(file_path, sheet_name=tab, header=[0, 1], index_col=0, parse_dates=True).sort_index()
            df.index.name = 'Date'
            pickle_file = fr'pickles/{pickle_files[i]}'

            with open(pickle_file, 'wb') as f:
                df.to_pickle(f)

            dfs[tab] = df

    if cap_prices:
        dfs['Prices-Cash'] = dfs['Prices-Cash'].clip(0, cap)
        dfs['Prices-Cash Basis'] = dfs['Prices-Cash Basis'].clip(0, cap)

    return dfs['Storage'].iloc[:,:-1], dfs['Production'], dfs['Demand-Actual'].iloc[:,:-1], dfs['Demand-Normal'].iloc[:,:-1], dfs['Prices-Cash'].iloc[:-1], dfs['Prices-Cash Basis'].iloc[:-1]

def create_feature_df(storage, prod, demand_actual, demand_normal, actual=True):
    
    
    cum_storage = storage.cumsum()
    cum_storage.columns =  pd.MultiIndex.from_tuples([(level1, f"{level2} CUM") if level2 else (level1, '') for level1, level2 in storage.columns])

    # prod.columns =  pd.MultiIndex.from_tuples([(level1, f"{level2} S") if level2 else (level1, '') for level1, level2 in prod.columns])
    # demand_actual.columns =  pd.MultiIndex.from_tuples([(level1, f"{level2} D") if level2 else (level1, '') for level1, level2 in demand_actual.columns])
    # demand_normal.columns =  pd.MultiIndex.from_tuples([(level1, f"{level2} DN") if level2 else (level1, '') for level1, level2 in demand_normal.columns])

    demand = demand_actual if actual else demand_normal 
    balance = prod - demand 

    features = balance\
               .join(storage, how='outer') \
               .sort_index(axis=1) \
    #            .assign(month = lambda x:x.index.month) \
    #            .assign(dow = lambda x:x.index.dayofweek) \

    # features['month'] = features['month'].astype('category')
    # features['dow'] = features['dow'].astype('category')
    # features['season'] = features.index.month.map(map_month_to_season)
    # features['season'] = features['season'].astype('category')

    

    return features

def train_model(area, features, prices, model, **kwargs):

    target = prices.loc[:,area]  
    for lookahead in range(1,14):

        target = target.shift(-lookahead).dropna()
        features = features.iloc[:-lookahead]
        

    return 0


"""run"""
# storage, prod, demand_actual, demand_normal, prices, basis = read_gas_data(file_path, cap_prices=cap_prices, cap=cap, read_pickle=read_pickle)
# features = create_feature_df(storage, prod, demand_actual, demand_normal, actual=True)
