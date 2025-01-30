import nfdrs4py
import pandas as pd
import numpy as np
import requests
import io
import time

time_start = time.time()
import nfdrs4py
config = nfdrs4py.read_config('data/NFDRSInitSample.txt')
interface = nfdrs4py.NFDRS4py.init_from_config(config)

wx = pd.read_csv('data/241513_2001_2017.fw21')
results = interface.process_df(wx,0,1,2,3,6,4,7)
results.to_csv('data/results_py.csv')
print(results)
print('Finished in: ',time.time() - time_start)