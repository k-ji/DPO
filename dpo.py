import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

def format_PI_data(df):
    
    df['Date'] = [x.split(" ")[0] for x in df.MessageTime]
    #df['EntryTime'] = [x.split(" ")[1] for x in df.MessageTime]

    #df['EntryTime'],format='%H:%M:%S')

    #df['Date'] = [pd.to_datetime(x.split(" ")[0],format='%H:%M:%S') for x in df.MessageTime]
    df['EntryTime'] = [pd.to_datetime(x.split(" ")[1],format='%H:%M:%S') for x in df.MessageTime]    
    
    df['LastUpdateTime'] = [pd.to_datetime(x.split(" ")[1],format='%H:%M:%S') for x in df.CompletionTime]

    cols = ['Date','EntryTime','CompletionTime','Status', 'Symbol', 'Side', 
            'OrdType','OrderQty', 'CumQty', 'Price', 'LeavesQty', 'AvgPx',
            'LEVEL', 'LOB_SLOPE_TYPE', 'ADV_INT',
            'ADJ_SPREAD', 'SHORT_OT', 'BALANCER_NAME']

    df['LEVEL'] = df['LEVEL'].fillna(value="NA")
    #df['Mode'] = [x.split(" ")[0] for x in df.LEVEL]
    
    def get_mode(level):
        x = level.split(" ")
        if len(x) > 1:
            return x[0]
        else:
            return level.split(" :: ")[0]
    
    def get_improvement(level):
        x = level.split(" :: ")
        if len(x) > 2:
            return x[1]
        else:
            return "0"


    def get_price_origin(level):
        x = level.split(" :: ")
        #print(x)
        if len(x) > 2:
            return x[2].split(" >> ")[0]
        else:
            return "0"


    def get_price_improved(level):
        x = level.split(" :: ")
        #print(x)
        if len(x) > 2:
            return x[2].split(" >> ")[1]
        else:
            return "0"
    
    df['Mode'] = df.LEVEL.apply(get_mode)
    df['IP'] = df.LEVEL.apply(get_improvement)
    df['PriceOrig'] = df.LEVEL.apply(get_price_origin)
    df['PriceImp'] = df.LEVEL.apply(get_price_improved)


    def convert_to_int(y,v):
        y = y.fillna(value=v)
        y = [int(x) for x in y]
        return y
    
    def convert_to_float(y,v):
        y = y.fillna(value=v)
        y = [float(x) for x in y]
        return y
    
    df['PriceImp'] = convert_to_float(df['PriceImp'],"0")
    df['IP'] = convert_to_float(df['IP'],"0")
    df['PriceOrig'] = convert_to_float(df['PriceOrig'],"0")
    df['Price'] = convert_to_float(df['Price'],"0")
    df['AvgPx'] = convert_to_float(df['AvgPx'],"0")
    df['ADJ_SPREAD'] = convert_to_float(df['ADJ_SPREAD'],"0")
    
    df['OrderQty'] = convert_to_int(df['OrderQty'],"0")
    df['CumQty'] = convert_to_int(df['CumQty'],"0")
    df['ADV_INT'] = convert_to_int(df['ADV_INT'],"0")
    df['ADV_BUCKET'] = convert_to_int(df['ADV_BUCKET'],"0")
    
    cols = ['Date','EntryTime', 'LastUpdateTime','Symbol','Mode','PriceImp', 'IP', 'PriceOrig',
            'Side', 'OrdType', 'OrderQty', 'CumQty', 'Price', 'AvgPx',
            'CLIENT_BASKET',  'LOB_SLOPE_TYPE', 'ADV_INT','ADV_BUCKET', 'ADJ_SPREAD', 'SHORT_OT']

    df = df[cols]
    
    #df.loc[:,'EntryTime'] = df['EntryTime'].dt.time
    #df.loc[:,'LastUpdateTime'] = df['LastUpdateTime'].dt.time
    #df['EntryTime'] = df['EntryTime'].dt.time
    #df['LastUpdateTime'] = df['LastUpdateTime'].dt.time
    #df.loc[:,'EntryTime'] = pd.to_datetime(df['EntryTime'],format='%H:%M:%S').dt.time
    #df.loc[:,'LastUpdateTime'] = pd.to_datetime(df['LastUpdateTime'],format='%H:%M:%S').dt.time
    #df['EndTime'] = df.LastUpdateTime
    
    return df


def get_all_mode_summary(df):
    cum_qty_mode = pd.DataFrame(df.groupby(['Mode']).CumQty.sum())
    cum_qty_mode['Percentage'] = cum_qty_mode.CumQty / cum_qty_mode.CumQty.sum()


    plt.figure(figsize=(10, 6))

    sns.barplot(x=cum_qty_mode.index,
            y = cum_qty_mode.CumQty,
            palette =['#275380','#275380',
                      '#30689F','#30689F',
                      '#3A7DBF','#3A7DBF',
                      '#4391DF','#4391DF','#4391DF','#4391DF','#4391DF',
                      '#4DA6FF','#4DA6FF','#4DA6FF','#4DA6FF'])
    plt.ylabel('Size')
    plt.title('Price Improvement by Time')
    plt.xticks(rotation=45)
    
    date = datetime.datetime.now().strftime("%Y%m%d")
    file_name = 'F:/UserFolders/KJ/data/wqt/' + date + '-Overall.png'
    
    plt.savefig(file_name)
    plt.show()
    return cum_qty_mode


def get_fill_by_level(df,post='PL',freq='10min'):
    if post == 'PL':
        levels = ['PL0','PL1','PL2','PL3']
    elif post == 'PDL':
        levels = ['PDL0','PDL1','PDL2','PDL3']
    elif post == 'DPL':
        levels = ['DPL0','DPL1']        
    elif post == 'IL':
        levels = ['IL0','IL1']
    elif post == 'ML':
        levels = ['ML0','ML1']
    elif post == 'All':
        levels = [x for x in list(sorted(set(df.Mode))) if x != 'NA']
        
    data = df[['LastUpdateTime','OrderQty','CumQty','Mode']].groupby([pd.Grouper(key='Mode'),
                                           pd.Grouper(key='LastUpdateTime',freq=freq)]).sum()

    df2 = pd.DataFrame([data[data.index.get_level_values('Mode')==x]['CumQty'].tolist() for x in levels]).T
    
    df2.columns = levels
    
    #Assuming each time bucket has all post types
    df2.index = [x.time() for x in pd.to_datetime(data.index.levels[1],format='%H:%M:%S')]
    
    
    df2['sum'] = df2.sum(axis=1)
    
    pct_levels = [x+'_Pct' for x in levels]
    
    for i in range(len(pct_levels)):
        df2[pct_levels[i]] = df2[levels[i]] / df2['sum']
    
    df2.drop(['sum'],axis=1,inplace=True)
    
    return df2


def plot_stacked_bar(df,post='PL',tp='Size'):
    
    if post == 'PL':
        levels = ['PL0','PL1','PL2','PL3']
    elif post == 'PDL':
        levels = ['PDL0','PDL1','PDL2','PDL3']
    elif post == 'DPL':
        levels = ['DPL0','DPL1']        
    elif post == 'IL':
        levels = ['IL0','IL1']
    elif post == 'ML':
        levels = ['ML0','ML1']
    else:
        return "Invalid tp input. TP can only be size or pct"        

    pct_levels = [x+'_Pct' for x in levels]
    
    print(levels)
    """
    if tp == 'Size':
        pl0 = df.PL0.tolist()
        pl1 = df.PL1.tolist()
        pl2 = df.PL2.tolist()
        pl3 = df.PL3.tolist()
    elif tp == 'Pct':
        pl0 = df.PL0_Pct.tolist()
        pl1 = df.PL1_Pct.tolist()
        pl2 = df.PL2_Pct.tolist()
        pl3 = df.PL3_Pct.tolist()
    else:
        return "Invalid tp input. TP can only be size or pct"
    """
    
   
    #r = [1,2,3,4,5,6]
    r = range(len(df[levels[0]]))

    if tp == 'Size':
        pl0 = df[levels[0]].tolist()
        plt.figure(figsize=(12, 8))
    elif tp == 'Pct':
        pl0 = df[pct_levels[0]].tolist()
        plt.figure(figsize=(10, 6))
        
    p0 = plt.bar(r,pl0,color='#1874CD',width=0.85)
    legend_levels = (p0[0])
        
    if len(levels) > 1:
        if tp == 'Size':
            pl1 = df[levels[1]].tolist()
        elif tp == 'Pct':
            pl1 = df[pct_levels[1]].tolist()
        
        p1 = plt.bar(r,pl1,bottom=pl0,color='#FF7256',width=0.85)
        legend_levels = (p0[0],p1[0])
        
    if len(levels) > 2: 
        if tp == 'Size':
            pl2 = df[levels[2]].tolist()
        elif tp == 'Pct':
            pl2 = df[pct_levels[2]].tolist()
        
        p2 = plt.bar(r,pl2, 
                    bottom=[i+j for i,j in zip(pl0,pl1)], 
                    color='#FFD700', width=0.85)
        legend_levels = (p0[0],p1[0],p2[0])

    if len(levels) > 3:
        if tp == 'Size':
            pl3 = df[levels[3]].tolist()
        elif tp == 'Pct':
            pl3 = df[pct_levels[3]].tolist()
                
        p3 = plt.bar(r,pl3, 
                    bottom=[i+j+k for i,j,k in zip(pl0,pl1,pl2)], 
                    color='#A2CD5A', width=0.85)
        legend_levels = (p0[0],p1[0],p2[0],p3[0])

    plt.ylabel(tp)
    plt.title(post + ' Price Improvement by Level')
    plt.xticks(r, df.index.tolist(),rotation=45)
    
    #if len(levels) == 1
    #plt.legend((p0[0], p1[0], p2[0], p3[0]), levels)
    plt.legend(legend_levels, levels, loc="upper right")
    
    date = datetime.datetime.now().strftime("%Y%m%d")
    file_name = 'F:/UserFolders/KJ/data/wqt/' + date + '-' + tp + '-' + post + '.png'
    
    plt.savefig(file_name)
    plt.show()
    
    
#Read file exported from Raptor Exchange Deep Book Tracker
file_name = "H:/dop_20191112_v3.xlsx"
data = pd.read_excel(file_name,index_col=None)
df = format_PI_data(data)

pd.set_option('display.max_columns', 999)
df.head()


#Get fill summary by post mode 
summary_by_mode = get_all_mode_summary(df)

all_modes = get_fill_by_level(df,'All')
all_modes.head()

posts = ['PL', 'DPL', 'PDL', 'IL', 'ML']
df2 = df.loc[df.LastUpdateTime < '1900-01-01 15:00:00'].copy()
for post in posts:
    freq = '15min'
    pl = get_fill_by_level(df2,post=post,freq=freq)

    #tp='Size'
    plot_stacked_bar(pl,post=post,tp='Size')
    plot_stacked_bar(pl,post=post,tp='Pct')
    
