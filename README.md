# bankAccount

Command line app that reads csv file expored from electronic banking (raiffeisen bank currently).
Application accepts user specified input file, specification of time interval for analysis of transactions: start date, end date 

Use argument
  --stats  ...  for basic output
  --makeiplot  ...  for interactive plots
  --bycategories  ...  for graphical output by categories
  
  
Example of use:

python bank_acc_analysis.py "sampledata.csv" "2023-01-01" "2023-02-20" --stats --makeiplot --bycategories

