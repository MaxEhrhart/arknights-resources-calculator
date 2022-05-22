import pandas as pd
if __name__ == "__main__":
    # Event resources
    event_resources = pd.read_csv('./files/event_resources.csv', sep=',', encoding='utf-8')
    event_resources = event_resources[~event_resources['done']].drop(columns=['done', 'event']).sum(axis=0).to_frame()
    event_resources.reset_index(inplace=True)
    event_resources.columns = ['resource', 'quantity']
    event_resources.set_index('resource', inplace=True)

    # User resoruces
    user_resources = pd.read_csv('./files/user_resources.csv', sep=',', encoding='utf-8', header=None)
    user_resources.columns = ['resource', 'quantity']
    user_resources.set_index('resource', inplace=True)

    # Merge resources
    user_events_resources = pd.concat([user_resources, event_resources]).groupby(['resource']).sum()
    user_events_resources.to_csv('./files/user_events_resources.csv', encoding='utf-8', sep=',', header=None)

    # Print
    # pd.set_option('display.max_rows', None)
    # print(event_resources, '\n')
    # print(user_resources, '\n')
    # print(user_events_resources, '\n')
