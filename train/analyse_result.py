import pandas as pd


df = pd.read_csv('result/result_bursty.csv')
print(df.groupby('datetime').mean())
import pandas as pd