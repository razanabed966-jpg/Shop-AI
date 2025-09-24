import pandas as pd

import matplotlib.pyplot as plt

import numpy as np

def make_connection_with_db():
    import mysql.connector
  
    connection_mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="wp-ecommerce"
    )
    cursor = connection_mydb.cursor(dictionary=True)
    return connection_mydb,cursor

def get_customers_by_country():
    _,cursor=make_connection_with_db()
    
    sql='''SELECT country, count(customer_id) as count_by_country 
        FROM  wp_wc_customer_lookup 
        group by country'''
    
    cursor.execute(sql)
    
    customers_results = cursor.fetchall()
    
    df=pd.DataFrame(columns=['country','count_by_country'])
    
    for customer in customers_results:
        obj = {
                "country":[customer['country']],
                "count_by_country":[customer['count_by_country']]
        }
        df_obj=pd.DataFrame(obj)
        df=pd.concat([df,df_obj], ignore_index=True)
    return df

def show_customers_by_countries_pie():
    
    df_customers_countries = get_customers_by_country()
    
    plt.pie(df_customers_countries['count_by_country'], 
            labels = df_customers_countries['country'], 
            autopct='%1.1f%%')
    
    plt.title('Coustomers per Countries')
    plt.show()

show_customers_by_countries_pie()