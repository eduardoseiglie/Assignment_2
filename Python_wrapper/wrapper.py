import pandas.io.sql as sqlio
import pandas as pd
import numpy as np
import psycopg2
import mysql.connector
import os
import sys
import datetime

def splitPath(s):
    f = os.path.basename(s)
    p = s[:-(len(f))-1]
    return f, p

def initialize_database():
    #start connection with database
    with open ('db_login.txt', 'r') as myfile:
        data = myfile.read()
    conn = psycopg2.connect(data)
    cur = conn.cursor()

    current_path = os.path.dirname(os.path.abspath(__file__))
    f,root = splitPath(current_path)

    sql_files = ['create_cbs_tables.sql', 'create_funda_table.sql','cbs_cleaning.sql', 'funda_cleaning.sql']
    path_prefix = 'SQL/'

    for sql_script in sql_files:
        print(os.path.join(root, path_prefix, sql_script))

    #Read csv input files:
    funda = pd.read_csv(os.path.join(root, 'Input_data/housing_data.csv'))
    #brt_2020 = pd.read_csv(os.path.join(root, 'Input_data/brt2020.csv'), sep=";")
    cbs_data = pd.read_csv(os.path.join(root, 'Input_data/cbs_data.csv'), sep=";")
    #gem_2020 = pd.read_csv(os.path.join(root, 'Input_data/gem2020.csv'), sep=";")
    #postcodes = pd.read_csv(os.path.join(root, 'Input_data/pc6-gwb2020.csv'), sep=";")
    #wijk2020 = pd.read_csv(os.path.join(root, 'Input_data/wijk2020.csv'), sep=";")

    #print(brt_2020)
    #print(cbs_data)
    #print(gem_2020)
    #print(postcodes)
    #print(wijk2020)

    #remove NoneTypes, rename columns to english and drop unnecessary columns
    #also cleaning the category objects to python list types for later usage and calculating the sellingtime
    '''
    funda_cleaned = funda.fillna(0).rename(columns={'publicatieDatum':'publicationDate','postcode':'zipcode','koopPrijs':'sellingPrice',\
    'volledigeOmschrijving':'fullDescription','soortWoning':'houseType','categorieObject':'categoryObject','bouwjaar':'yearOfBuilding', \
    'indTuin':'garden','perceelOppervlakte':'parcelSurface','aantalKamers':'numberRooms','aantalBadkamers':'numberBathrooms','energielabelKlasse':'energylabelClass',\
    'oppervlakte':'surface','datum_ondertekening':'sellingDate'}).drop(['globalId', 'globalId.1','kantoor_naam_MD5hash'], axis=1)

    def category_to_list(item):
        item_list = item.split(' ')
        cleaned_item_list = []
        for i in item_list:
            cleaned_item = i.replace('<','').replace('{','').replace('>','').replace('}','').replace('(','').replace(')','')
            cleaned_item_list.append(cleaned_item)
        return str(cleaned_item_list)

    funda_cleaned['houseType'] = funda_cleaned['houseType'].apply(lambda x: category_to_list(x))
    funda_cleaned['categoryObject'] = funda_cleaned['categoryObject'].apply(lambda x: str(x).replace('<','').replace('{','').replace('>','').replace('}',''))
    funda_cleaned['sellingDate'] = pd.to_datetime(funda_cleaned['sellingDate'])
    funda_cleaned['publicationDate'] = pd.to_datetime(funda_cleaned['publicationDate'])
    funda_cleaned['sellingTime'] = funda_cleaned.sellingDate - funda_cleaned.publicationDate
    funda_cleaned['sellingTime'] = funda_cleaned['sellingTime'].apply(lambda x: int(x.days))
    '''

    cbs_cleaned = cbs_data.fillna(0).rename(columns={'WijkenEnBuurten':'NeighborhoodsAndDistricts','Gemeentenaam_1':'NameOfMunicipality','Mannen_6':'NumberOfMen',\
    'Vrouwen_7':'NumberOfWomen','k_0Tot15Jaar_8':'AgeFrom0to15years','k_15Tot25Jaar_9':'AgeFrom15to25years',\
    'k_25Tot45Jaar_10' : 'AgeFrom25to45years','k_45Tot65Jaar_11' : 'AgeFrom45to65years','k_65JaarOfOuder_12' : 'AgeFrom65AndOlder',\
    'Bevolkingsdichtheid_33' : 'PopulationDensity','Woningvoorraad_34' : 'HousingStock','PercentageBewoond_38' : 'PercentageInhabited',\
    'PercentageOnbewoond_39' : 'PercentageUninhabited','Koopwoningen_40' : 'OwnerOccupiedHouses','HuurwoningenTotaal_41' : 'RentalHouses',\
    'BouwjaarVoor2000_45' : 'ConstructionYearBefore2000','BouwjaarVanaf2000_46' : 'ConstructionYearAfter2000',\
    'GemiddeldInkomenPerInwoner_66' : 'AverageIncomePerCitizen','MeestVoorkomendePostcode_103' : 'MostCommonPostalCode','Dekkingspercentage_104' : 'CoveragePercentage'}).drop(['Codering_3','NameOfMunicipality'], axis=1).replace(' ','').replace('       .',0)
    cbs_cleaned = cbs_cleaned.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    print(cbs_cleaned.columns)
    type_dict = {'PopulationDensity': 'float64','PercentageInhabited':'float64','PercentageUninhabited': 'float64','OwnerOccupiedHouses': 'float64','RentalHouses': 'float64','ConstructionYearBefore2000 ': 'float64','ConstructionYearAfter2000': 'float64','AverageIncomePerCitizen': 'float64','MostCommonPostalCode': 'int64','CoveragePercentage ': 'int64'}

    for k,v in type_dict.items():
        print(k)
        cbs_cleaned = cbs_cleaned.astype({k: v})#,'PercentageInhabited':'int64','PercentageUninhabited': 'int64','OwnerOccupiedHouses': 'int64','RentalHouses': 'int64','ConstructionYearBefore2000 ': 'int64','ConstructionYearAfter2000': 'int64','AverageIncomePerCitizen': 'float64','MostCommonPostalCode': 'int64','CoveragePercentage ': 'int64'}, errors='ignore')
    
    #'PercentageInhabited': 'int64','PercentageUninhabited': 'int64','OwnerOccupiedHouses': 'int64','RentalHouses': 'int64','ConstructionYearBefore2000 ': 'int64','ConstructionYearAfter2000': 'int64','AverageIncomePerCitizen': 'float64','MostCommonPostalCode': 'int64','CoveragePercentage ': 'int64'
    cbs_cleaned['NeighborhoodsAndDistricts'] = cbs_cleaned['NeighborhoodsAndDistricts'].replace(' ','')
    cbs_cleaned['MunicipalityCode'] = cbs_cleaned['NeighborhoodsAndDistricts'].apply(lambda x: str(x) if str(x).startswith('GM') else '-')
    cbs_cleaned['DistrictCode'] = cbs_cleaned['NeighborhoodsAndDistricts'].apply(lambda x: str(x) if str(x).startswith('WK') else '-')
    cbs_cleaned['NeighborhoodCode'] = cbs_cleaned['NeighborhoodsAndDistricts'].apply(lambda x: str(x) if str(x).startswith('BU') else '-')
    
    print(cbs_cleaned.dtypes)

    demographic_info_db = cbs_cleaned[['MunicipalityCode','DistrictCode','NeighborhoodCode','NumberOfMen','NumberOfWomen','AgeFrom0to15years','AgeFrom15to25years',\
    'AgeFrom25to45years','AgeFrom45to65years','AgeFrom65AndOlder','PopulationDensity']]
    housing_info_db = cbs_cleaned[['MunicipalityCode','DistrictCode','NeighborhoodCode','HousingStock','PercentageInhabited',\
    'PercentageUninhabited','OwnerOccupiedHouses','RentalHouses','ConstructionYearBefore2000','ConstructionYearAfter2000',\
    'AverageIncomePerCitizen','MostCommonPostalCode','CoveragePercentage']]

    print(demographic_info_db)
    print(housing_info_db)
    print(housing_info_db['CoveragePercentage'].drop_duplicates().to_list())
    

    '''
    #open the sql file and execute each command seperatly after extracting the lines that are comments
    with open(os.path.join(root, path_prefix, 'cbs_cleaning.sql'), 'r') as sql_file:
        commands = sql_file.read()
    for sql in commands.split(';'):
        executing_command = str(sql.replace('\n',''))+';'
        if executing_command.startswith('--') == True:
            print('comment')
        else:
            try:
                cur.execute(executing_command, conn)
                conn.commit()
            except Exception as e:
                print(e)
                conn.rollback()
        #conn.commit()
    '''
    
    #Make changes to db persistent
    #conn.commit()

    #End connection
    cur.close()
    conn.close()

    return print('Database successfully loaded and initialized')
#initialize_database()
#print(cwd)

def add_funda_data(csv_path, year):
    #start connection with database
    with open ('db_login.txt', 'r') as myfile:
        data = myfile.read()
    conn = psycopg2.connect(data)
    cur = conn.cursor()

    ######WRITE THE CODE HERE############################
    with open('cbs_cleaning.sql', 'r') as sql_file:
        commands = sql_file.read()
    for i in commands.split(';'):
        print((str(i.replace('\n',''))+';'))

    '''
    (1) load the funda data from csv, 
    (2) preprocess the data, 
    (3) connect to the database, 
    (4) upload the data into a database table for year 2018,
    '''


    ######################################################


    #Make changes to db persistent
    conn.commit()

    #End connection
    cur.close()
    conn.close()
    return print('Funda Data succesfully added')
#add_funda_data('/some/path', 2018)


def funda_analysis():
    #start connection with database
    with open ('db_login.txt', 'r') as myfile:
        data = myfile.read()
    conn = psycopg2.connect(data)
    cur = conn.cursor()

    #miniumum requirements:

    # 1. Average  asking  price  per  month  for  each  of  the municipalities in the Netherlands
    #select needed columns from database and store them in a pandas dataframe
    executing_script = "SELECT sellingPrice, publicationDate, MunicipalityCode, MunicipalityName FROM funda_2018 NATURAL LEFT JOIN zipcodes NATURAL LEFT JOIN municipality_names;"
    avg_asking_price = sqlio.read_sql_query(executing_script, conn)

    #create column month and year and create columns that will be used to group by
    avg_asking_price['month'] = avg_asking_price['publicationdate'].apply(lambda x: x.month)
    avg_asking_price['year'] = avg_asking_price['publicationdate'].apply(lambda x: x.year)
    groups = ['municipalityname', 'year','month']
    
    #group by selected columns. calcualte mean and safe as pandas Dataframe
    avg_asking_price_mean = avg_asking_price.groupby(by=groups).mean().reset_index()
    print("avg_asking_price_mean.head(25)")
    print(avg_asking_price_mean.head(25))

    #2. Average asking price per bevolkingsdichtheid group or category (you might  have  to  discretize  this  variable)  for  each  gemeente  in  the  Netherlands
    #select needed columns from database and store them in a pandas dataframe
    executing_script = "SELECT DISTINCT sellingprice, districtCode, populationDensity, municipalityCode, municipalityname, zipcode FROM funda_2018 NATURAL LEFT JOIN zipcodes NATURAL LEFT JOIN district_info NATURAL LEFT JOIN municipality_names;"
    avg_asking_price_popdens = sqlio.read_sql_query(executing_script, conn)

    #define function to discretize the variable populationDensity
    def discretizing(number):
        number = str(number)
        if number == 'None':
            number = 0
        elif number =='       .':
            number = 0
        number = int(number)
        if number <= 500:
            group = '<=500'
        elif (number > 500) & (number <= 1000):
            group = "501 - 1000"
        elif (number > 1000) & (number <= 1500):
            group = "1001 - 1500"
        elif (number > 1500) & (number <= 2000):
            group = "1501 - 2000"
        elif (number > 2000) & (number <= 3000):
            group = "2001 - 3000"
        elif (number > 3000) & (number <= 5000):
            group = "3001 - 5000"
        elif (number > 5000) & (number <= 7500):
            group = "5001 - 7500"
        elif (number > 7500) & (number <= 10000):
            group = "7501 - 10000"
        elif (number > 10000) & (number <= 15000):
            group = "10001 - 15000"
        elif (number > 15000):
            group = ">1500"
        return group

    #apply discretizing on the variable populationDensity and group by the density categorys and municiaplity and calculate mean
    avg_asking_price_popdens['population_dens_cat'] = avg_asking_price_popdens['populationdensity'].apply(lambda x: discretizing(x))
    avg_asking_price_popdens_grouped = avg_asking_price_popdens.groupby(by=['municipalitycode', 'population_dens_cat']).mean().reset_index()
    
    print("avg_asking_price_popdens_grouped.head(25)")
    print(avg_asking_price_popdens_grouped.head(25))
    #3. Average  asking  price  per  gemeente,  where  the  gemeenten  are  ordered  according  to  the  average  income  per  inhabitant  (from  highest income to lowest income)
    executing_script = "SELECT sellingPrice, MunicipalityName, averageincomepercitizen FROM funda_2018 NATURAL LEFT JOIN zipcodes NATURAL LEFT JOIN municipality_names NATURAL LEFT JOIN municipality_info limit 1000;"
    avg_asking_price_by_income = sqlio.read_sql_query(executing_script, conn)
    avg_asking_price_by_income_sorted = avg_asking_price_by_income.sort_values('averageincomepercitizen',ascending=False)
    
    print("avg_asking_price_by_income_sorted.head(25)")
    print(avg_asking_price_by_income_sorted.head(25))
    #4. for  every  gemeente  in  the  Netherlands  and  every  month  in  2018-2019: the percentage increase or decrease in the average house price in that gemeente compared to the previous month
    #use the already grouped dataframe

    avg_asking_price_mean = avg_asking_price_mean.reset_index().rename(columns={'index':'Index'})

    def rel_difference(row):
        if row.month == 1:
            rel_difference = 0
        else:
            rel_difference = ((row.sellingprice/ avg_asking_price_mean[avg_asking_price_mean.Index == (row.Index -1)].sellingprice.iloc[0])-1)*100
        return rel_difference    
    
    avg_asking_price_mean['rel_diff'] = avg_asking_price_mean.apply(lambda x: rel_difference(x), axis= 1)
    

    #Felicia: For  every  gemeente  in  the  Netherlands  and  every  month  in  2018-2019:  the  absolute  difference  between  the  median  house  price  for  that month in that gemeente and the median house price for the next month in that gemeente
    def abs_difference(row):
        if row.month == 1:
            abs_difference = 0
        else:
            abs_difference = row.sellingprice - avg_asking_price_mean[avg_asking_price_mean.Index == (row.Index -1)].sellingprice.iloc[0]
        return abs_difference
    avg_asking_price_mean['abs_diff'] = avg_asking_price_mean.apply(lambda x: abs_difference(x), axis= 1)

    print("avg_asking_price_mean.head(25)")
    print(avg_asking_price_mean.head(25))
    #Baris: The  average  house  price  in  2018-2019  according  to  leftijdgroep  (in  the whole of the Netherlands)

    #Emmanuel: Average sellingtime per month and municipality

    #Make changes to db persistent
    conn.commit()

    #End connection
    cur.close()
    conn.close()

    return print('Analysis succesfully done')
#funda_analysis()

def full_text_search(text):

    '''
    SELECT title
    FROM pgweb
    WHERE to_tsvector('english',body) @@ to_tsquery('friend');
    '''

    return DF

if __name__ == '__main__':
    globals()[sys.argv[1]]()

