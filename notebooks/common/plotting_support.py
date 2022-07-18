import pandas as pd


def build_sankey(index_cols, target_col, df):
    input_df = df.copy()

    # build target/source relationships
    df_links = pd.DataFrame()
    for pos in range(0,len(index_cols)-1):
        temp_df = input_df.groupby([index_cols[pos], index_cols[pos+1]]).agg({target_col:'sum'}).reset_index()
        temp_df.columns = ['source', 'target', 'value']
        df_links = pd.concat([df_links, temp_df])
    df_links['value'] = (df_links['value']/df_links['value'].sum())

    # label encoding:
    label_list = list(df_links['source'])
    label_list.extend(list(df_links['target']))
    label_list = list(dict.fromkeys(label_list))
    label_dict = {}
    i=0
    for item in label_list:
        label_dict[item] = i
        i+=1
    label_dict

    df_links['source'] = df_links['source'].replace(label_dict)
    df_links['target'] = df_links['target'].replace(label_dict)

    return df_links, label_dict