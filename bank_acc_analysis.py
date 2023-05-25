#program na zaklade vypisu z elektronickeho bankovnictvi zpracovava prijmy a vydaje 
#za specifikovane casove obdobi do grafu umoznujicich prehlednou kontrolu prijmu a vydaju.
#
#Problemy:
#
#   1. kazda banka bude mit rochu jinou podobu vypisu. Tento je nachystany pro raifeissen bank. 
#           -kodovani (asi v pohode krome cesiny) ... Vyreseno v pd.read_csv
#           -mezera/tecka u tisicu, desetinna carka ... Vyreseno v pd.read_csv
#      
#   2. nekdy vypis muze obsahovat velke castky, kvuli kterym jsou pak ve sloupcovych grafech ostatni spatne viditelne
#   3. vetsina opakujicich se transakci je rozdelena do kategorii. Ty co nejsou, spadnou do 'Other'.
#           -da se neco delat s 'neznamym' obchodnikem? (jina mena, dalsi slovnik...)
#           -        
#   4. problem s vklady bakomatem, nekdy spatne zarazuje


import pandas as pd
import plotly.express as px
import argparse
import os



def add_categories(df): # prirazuje kategorie jednotlivym prevazne odchozim transakcim z promenne dict_of_categories

    #finds Labels in dict_of_categories
    for key in dict_of_categories.keys():
        for vendor in dict_of_categories[key]:
            df.loc[df['Label'] == vendor, ['Category']] = key
        
    #Label not found in dict_of_categories
    df.loc[df['Category'] == '', 'Category'] = 'Other' 
    df.loc[df['Label'].str.contains('ucb'), ['Category']] = 'savings'
    df.loc[df['Label'].str.contains('prevod'), ['Category']] = 'savings'
    df.loc[df['Label'].str.contains('UNIQA'), ['Category']] = 'savings'
    df.loc[df['Label'].str.contains('sporeni'), ['Category']] = 'savings'
    df.loc[df['Číslo protiúčtu'].str.contains('2070'), ['Category']] = 'savings'

    
def identify_income_savings(df):
    df.loc[df['Zaúčtovaná částka'] > 0, 'Expense/Income'] = 'income'
    df.loc[df['Category'] == 'savings', 'Expense/Income'] = 'savings'



# Initialize parser
parser = argparse.ArgumentParser(prog="BankLogAnalyzer",
description="accepts csv input file and performs basic statistics")
 
# arguments for parser
parser.add_argument("filename", help="datafile name, file must be in the same folder as bank_acc_analysis.py", type=str, default="Pohyby_short.csv")
parser.add_argument("date_begining", help="specifies date for transactions analysis - first day", type=str)
parser.add_argument("date_end", help="specifies date for transactions analysis - last day", type=str)
parser.add_argument("--stats", action="store_true", help="displays basic statistics of transactions dataset")
parser.add_argument("--makeiplot", action="store_true", help="displays interactive plot in browser")
parser.add_argument("--bycategories", action="store_true", help="groups expanses by categories")

##

dict_of_categories = {
    'Supermarket' : ['Albert', 'BILLA', 'Tesco', 'Breat Market', 'Breat Market; Dolni Brezany', 'COOP', 'Enpeka', 'Kaufland', 'Lidl', 'Tesco', 'RYNEK', 'Řeznictvní a uzenářství Malec', 'Enpeka', 'Maslove trubicky s.r.; Brno', 
                    'Uzenářství a lahůdky Sláma', 'Restaurace na Holecku; Trebic', 'PENNY', 'Marks and Spencer', 'TCHIBO 7709; PRAHA 4 - CHO', 'Hofer', 'M-S CHODOV; PRAHA 4', 'M&S CHODOV; PRAHA 4; CZE',
                    'Breat Market; Dolni Brezany; CZE', 'RYNEK JIHLAVA - BRNEN; JIHLAVA; CZE'], 
    'CashWithdraw' : ['ATM UniCredit Bank', 'ATM ČSOB', 'ATM Air Bank', 'ATM KB', 'ATM', 'ATM MONETA Money Bank'],
    'Household' : ['AMICUS', 'Zara Home', 'IKEA', 'Haus Spezi', 'AUTOCOLOR DS s.r.o.', 'Stavebniny DEK', 'dm drogerie', 'HORNBACH', 'OBI', 'JYSK', 'Tipa', 'Mountfield', 'LIGNO MAT S R O; VELKE MEZIRIC',
                    'DM DROGERIE S.R.O. 47; JIHLAVA', 'GOPAY -LEVNE-NARADI.C; levne-naradi.', 'Květiny Flamengo', 'AMICUS; VELKE MEZIRIC; CZE', 'IMAO CZ; V. MEZIRICI; CZE', 
                    'AUTOCOLOR DS s.r.o.; Velke Meziric; CZE', 'TETA drogerie', 'PP PROFI; VELKE MEZIRIC; CZE', 'AUTOCOLOR DS s.r.o.; Velke Meziric; CZE', 'ZZN Polabí', 'LIGNO MAT S R O; VELKE MEZIRIC; CZE'],
    'Electricity_Gas_Insurance_Services' : ['E.ON', 'eon.cz', 'Primagas', 'O2', 'Top-Pojištění.cz', 'UNIQA', 'eon.cz; *esk* Bud*jov; CZE'],
    'Gasoline_diesel' : ['CERPACI STANICE', 'OMV', 'OMV 2001', 'ORLEN Benzina', 'Tank ONO', 'Tesco Gas Station', 'Horácké autodružstvo', 'ICOM transport', 'INA Vukova Gorica', 'MOL', 'Shell',
                        'CERPACI STANICE; VELKE MEZ.', 'ARMEX Oil', 'BENZINA CS 0246; STRECHOV N/S.', 'OMV 2001; Pavov', 'Jihlava - PFS CAT; Jihlava', 'CERPACI STANICE; VELKE MEZ.; CZE',
                        'ONO, JIHLAVA; JIHLAVA; CZE'],
    'Car' : ['AUTOBATERIE KOPECNY', 'AUTOBATERIE KOPECNY,; VELKE MEZIRIC', 'Auto Kelly', 'Autoservis Prchal', 'Elektronická dálniční známka', 'motora.cz', 'Autoservis Prchal; Trebic - Tyn'], 
    'Travelling_PublicTransport' : ['Dopravní podnik hlavního města Prahy - DPP', 'Technická správa komunikací hlavního města Prahy', 'Čedok', 'prg.aero; Praha 6', 'Služby města Jihlavy - Parkování',
                                    'PARKOVANI 1-01-05; BRNO', 'Parkoviště Arkády Pankrác', 'STUDENT AGENCY'],
    'Restaurants_Melas' : ['AVOKADO', 'Apetit', 'BALKAN RESTAURANTS', 'Bageterie Boulevard', 'Centrum Lihovar', 'Jelínkova vila - hotel, pivovar', 'Jídelna u Šimůnků', "McDonald's", 'Nature Spot',
                            'Ovocný Světozor', 'PRAGUE HOT-DOG', 'Passage restaurant', 'Pizza & bistro, uzenářské speciality', 'Pizzeria Laguna', 'The Pub', 'U BILEHO KONICKA; VELKE MEZIRIC; CZE', 'Ugo Salaterie',
                            'Velkopopovická Kozlovna', 'RESTAURACE NOVY SVIT; VELKE MEZIRIC', 'KFC', 'Pizza Restaurant Periferie', 'Pizza360 NS s.r.o.; Praha 5', 'Ugo Freshbar', 'Tom\'s Burger',
                            'Potrefená husa', 'SAN MARCO; TREBIC 1', 'Restaurace Tradice', 'Running sushi WANG', 'Cukrárna u Zdubů', 'Makakiko Chodov; Praha Chodov', 'RESTAURACE U MATEJE; MOR. KRUMLOV',
                            'PIZZA PIAZZA - BYSTRI; BYSTRICE NAD', 'GOLDEN SUN; JIHLAVA', 'SPV - středisko praktického vyučování', 'CUKRARNA A KAVARNA PO; TREBIC 1', 'RESTAURACE; VELKE MEZIRIC',
                            'U BILEHO KONICKA; VELKE MEZIRIC', 'Hotel Snezne; Brno', 'MARSOVSKA RYCHTA; NOVE MESTO NA', 'BALKAN RESTAURANTS, S; TUCHOMERICE; CZE', 'PRAGUE HOT-DOG; PRAHA 8; CZE',
                            'Makakiko Chodov; Praha Chodov; CZE', 'Rodeo steak house'], 
    'Electronics_and_office' : ['ESET software', 'DATART', 'CZC', 'T.S.BOHEMIA', 'Česká pošta', 'GOPAY -DIKY OKAY.CZ; https://okay.', 'Alza', 'PAPIR TABAK; VELKE MEZIRIC', 'Mironet', 'RETINO - SHIPPING; PRAHA',
                                'CZC; Pribram V-Zda', 'KOH-I-NOOR', 'McPen', 'MALL'],
    'Clothes_Accessories' : ['ALPINE PRO STORES-A119; Jihlava', 'GATE', 'Takko', 'Lindex', 'SPORTISIMO', 'Dedoles', 'Decathlon', 'Esprit', 'CCC', 'HUDYsport', '4camping', 'Apart', 'NEW YORKER',
                            'C - A 114 Centrum Chod; Praha 4 Chodo','H-M; Prague', 'Baťa', 'Calzedonia', 'Sportisimo; Praha 4', 'Next', 'CYKLO SKI SPORT JAN J; VELKE MEZIRIC; CZE', 'Deichmann', 
                            'ZLATNICTVI; VEL. MEZIRICI; CZE'],
    'Kids' : ['Honzik tenis', 'LABYRINT; Trebic', 'OBCHODTH.cz', 'ŠJ SOKOLOVSKÁ', 'HRACKY BAMBULE; VELKE MEZIRIC', 'maxikovy-hracky.cz', 'PEPCO', 'Wiky', 'SPARKYS s.r.o., JI; Jihlava',
                'TWINSPORT JIRI STOLP; TREBIC', 'H&M', 'Honzík - Míčové hry', 'Honzík - Abeceda sportu', 'Honzík, tenis', 'Honzik - plavani Trebic, pololetni', 'Honzik - atletika', 'školka H', 
                'skolka Honzik', 'skolka 11/2022'],
    'Pharmacy' : ['BENU LEKARNA VELKE; VELKE MEZIRIC', 'Benu lékárna', 'Dr.Max', 'BENU LEKARNA VELKE; VELKE MEZIRIC; CZE'],
    'Books_Press' : ['KNIHKUPECTVI A CAJOVN; JIHLAVA 1', 'GGT Tabák-Tisk', 'Knihkupectví Luxor', 'trhknih.cz', 'booktook.cz', 'Knihobot', 'Grada Publishing', 'Economia', 'Knihkupectví Jakuba Demla',
                    'PRESSMEDIA SPOL.S.R; VELKE MEZIRIC; CZE'],
    'HealthCare' : ['B SMILE S.R.O.; OSOVA BITYSKA'],
    'Accommodation' : ['HTL.ZAMEK STIRIN-GOLF; KAMENICE', 'Zámek Štiřín', 'Reso Hotels', 'LIN TERMINAL RP; LITOMYSL', 'Booking'],
    'Culture_Sport' : ['BIOTOP JEMNICE; JEMNICE', 'Aquapark Laguna Třebíč', 'MESTSKE KULTURNI STRE; TREBIC 1; CZE', 'Skiareál Fajtův kopec', 'DINOSAURI VR; TUCHOMERICE; CZE'], 
    'Other' : [],
}


##
args = parser.parse_args()



os_abspath = os.path.abspath('../')
os_dir_content = os.listdir(os_abspath)
data_file = args.filename #'Pohyby_short.csv'

#read and sort data from csv by day of payment
transactions = pd.read_csv(data_file, sep=';', dayfirst=True, decimal=',', thousands=' ', encoding='cp1250')

transactions["Datum provedení"] = pd.to_datetime(transactions["Datum provedení"], format="%d.%m.%Y")
transactions.sort_values(by=["Datum provedení"], inplace=True)


#adding columns for processing
transactions.insert(14, 'Expense/Income', 'expense') 
transactions.insert(15, 'Label', '')   #if name of the shop is not given it is tahen from other details of transaction
transactions.insert(16, 'Category', '') #category of expense

text_columns = ['Název účtu', 'Název protiúčtu', 'Zpráva', 'Poznámka', 'Vlastní poznámka', 'Název obchodníka', 'Město', 'Číslo účtu', 'Kategorie transakce', 
                'Číslo protiúčtu', 'Typ transakce', 'Měna účtu', 'Původní částka a měna', 'Id transakce', 'Datum zaúčtování', 'Expense/Income', 'Label', 'Category']

#convert colums that are used for analysis to string
for column in transactions.columns:
    if column in text_columns:
        transactions = transactions.astype({column:str})


#I am not sure why this is working and why '', 'nan', and retyping to string was needed
transactions.loc[transactions['Label'] == '', 'Label'] = transactions['Název obchodníka'].astype(str)
transactions.loc[transactions['Label'] == 'nan', 'Label'] = transactions['Poznámka'].astype(str)
transactions.loc[transactions['Label'] == 'nan', 'Label'] = transactions['Název protiúčtu'].astype(str)

#fill category in df according to dictionary
trans_with_categories = add_categories(transactions)

#identify incomes and mark expenses to other accounts as savings
identify_income_savings(transactions)


## ANALYSIS OF SELECTED TIME PERIOD
transact_date_limited = pd.DataFrame(transactions.loc[(transactions["Datum provedení"] >= args.date_begining) & (transactions["Datum provedení"] <= args.date_end)])


#create ouptup file with added columns
transact_date_limited.to_csv('output_time_imited.csv', encoding='cp1250', sep=';')


shops_date_limited = transact_date_limited.loc[transact_date_limited["Expense/Income"] == 'expense']['Label'].to_list()#, transact_date_limited["Label"]].to_list()
shops_date_limited = list(set(shops_date_limited))
shops_date_limited.sort()
#print(shops_date_limited)



#Analysis of transactions is given to the user:   
#...statistics of expenses
if args.stats:
    print(' \n\n')
    print()
    print(f'Souhrnna data o transakcich v obdobi: {str(args.date_begining)} - {str(args.date_end)}')
    print('\n\n---------------------------------------------------------------')
    #STATISTIKA:
    total_expenses = round(transact_date_limited.loc[transact_date_limited['Expense/Income'] == 'expense']['Zaúčtovaná částka'].sum(), 2)
    total_savings = round(transact_date_limited.loc[transact_date_limited['Expense/Income'] == 'savings']['Zaúčtovaná částka'].sum(), 2)
    total_income = round(transact_date_limited.loc[transact_date_limited['Expense/Income'] == 'income']['Zaúčtovaná částka'].sum(), 2)
    
    print(f'   Celkove vydaje: {total_expenses}\t(vcetne sporeni: {round(total_expenses + total_savings, 2)})')
    print(f'   Celkove prijmy: {total_income}')
    print(f'   Bilance:        {round(total_income + total_expenses, 2)} \t(vcetne sporeni: {round(total_income + total_expenses + total_savings, 2)})')
    print('---------------------------------------------------------------\n')

#...bar chart of incoming and outcoming transactions AND pie chart of expenses by vendor
if args.makeiplot:
    transact_date_limited["Zaúčtovaná částka"] = transact_date_limited["Zaúčtovaná částka"].abs()


    fig = px.bar(transact_date_limited, x="Datum provedení", y="Zaúčtovaná částka",
             color="Expense/Income", hover_data=['Název obchodníka', 'Poznámka', 'Název protiúčtu'],
             barmode = 'group', title='Overview of transactions')
  
    fig.show()
    fig.write_image("./bar_chart.png")

    #print('Vypisuji celkove vydaje v danem obdobi podle obchodniku:')
    total_expenses_by_shop = dict()

    shop_names = []
    shop_vals = []
    shop_minor_amount = 'minor transactions'
    value_minor = 0

    for shop in shops_date_limited: 
        suma = transact_date_limited.loc[(transact_date_limited['Label'] == shop) & 
                                         (transact_date_limited['Expense/Income'].astype(str) == 'expense')]['Zaúčtovaná částka'].sum()
        
        if suma < 180:
            value_minor += suma
            #print(f'adding to minor transactions: {shop}')
            
        else:
            shop_names.append(shop)
            shop_vals.append(suma)
            total_expenses_by_shop[shop]=suma
    shop_names.append(shop_minor_amount)
    shop_vals.append(value_minor)



    fig2 = px.pie(values=shop_vals, names=shop_names, title='Overview of expanses')
    fig2.show()
    fig2.write_image('./pie_chart.png')

#...sum of expenses by categories
if args.bycategories:
    expenses_by_categories = dict()
    shops_by_categories = dict()
    summary_categories = {
                            'Category': [],
                            'Total': [],
                            'Num of trans': [],
                            'Average amount': [],
                            'Max amount': [],
                            'Min amount': [],
                            'Vendor list': []
    }
    summary_categories = pd.DataFrame(summary_categories)

    #POKRACOVANI STATISTIKY PODLE KATEGORII:
    for expense_category in dict_of_categories.keys():
        table = pd.DataFrame(transact_date_limited.loc[(transact_date_limited['Category'] == expense_category) & (transact_date_limited['Expense/Income'] == 'expense')]["Zaúčtovaná částka"])
        
        total_expense_in_category = table['Zaúčtovaná částka'].abs().sum()
        number_of_transactions_in_category = len(table)
        expenses_by_categories[expense_category] = total_expense_in_category
        shops_by_categories[expense_category] = ', '.join(list(set(transact_date_limited.loc[transact_date_limited['Category'] == expense_category]['Label'].to_list())))
        avg = format(table['Zaúčtovaná částka'].abs().mean(), '.2f')
        max = format(table['Zaúčtovaná částka'].abs().max(), '.2f')
        min = format(table['Zaúčtovaná částka'].abs().min(), '.2f')

        summary_categories.loc[len(summary_categories.index)] = [expense_category, 
                                                                 total_expense_in_category, 
                                                                 number_of_transactions_in_category, 
                                                                 avg, 
                                                                 max, 
                                                                 min, 
                                                                 shops_by_categories[expense_category]] 
        
    
    # summary_categories = pd.DataFrame(summary_categories.items(), columns=['Category', 'Total expenses', 'number of transactions', 'average spent', 'max spent', 'Shops'])
    summary_categories.to_csv('output_categories.csv', sep=';', decimal=',', encoding='cp1250')
    print(summary_categories)

    ## TOHLE BY SE MELO PREDELAT, ASI TO JDE LEPE...

    shops_categories_df = pd.DataFrame(shops_by_categories.items(), columns=['Categories', 'Shops']) #kategorie a seznam prislusejicich obchodu
    totExpenses_categories_df = pd.DataFrame(expenses_by_categories.items(), columns=['Categories', 'Total amount']) #kategorie a seznam prislusejicich celkovych castek za obdobi
    #spojeno do jednoho df
    result = pd.merge(shops_categories_df, totExpenses_categories_df, on="Categories") 


    fig3 = px.bar(result, x='Categories', y='Total amount',
             barmode = 'group', title='Overview of transactions', hover_data=['Shops'])
    #fig3.update_traces(hovertemplate='Date:%{x}<br>value:%{y}<br>Total_accounts:%{custom_data}')
    fig3.show()
