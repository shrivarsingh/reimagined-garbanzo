ParentURL: https://www.eia.gov/electricity/data/eia923/

CurrentFileURL (downloads 2020 by month): https://www.eia.gov/electricity/data/eia923/xls/f923_2020.zip

HistoricalFileURL (change 2019 to year of choice): https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2019.zip



Scope:

Build a python scraper in python 3.6 environment to download data from EIA website from 2015-Present (using URL’s above)
Save raw data to folder on local c drive called “raw”
Extract the tab named ‘Page 5 Fuel Receipts and Costs’ from file ‘EIA923_Schedules_2_3_4_5_M_12_2019_Final.xlsx’ for each respective year
Save as separate csv file named “Form923_fuel&Receipts&Costs_YYYY” into folder named “Extracted” on c drive
If script is executed again it will not create duplicate files
2020 has new data added each month, if script is executed it will save new data if available.