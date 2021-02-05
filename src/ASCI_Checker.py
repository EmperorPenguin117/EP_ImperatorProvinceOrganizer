import pandas as pd

broken_filename = 'broken_province_names.csv'
data = pd.read_csv(broken_filename, encoding= 'unicode_escape')
x = 1