# مكتبة الاتصال مع قاعدة البيانات
import mysql.connector
# مكتبة بانداس
import pandas as pd
# الاتصال مع قاعدة البيانات
connection_mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="wp-ecommerce"
)
# مؤشر 
cursor = connection_mydb.cursor(dictionary=True)

def get_daily_sales_between_2_dates(startdate, enddate):
    #إطار بيانات للنتائج
    df=pd.DataFrame(columns=['date','total'])
    # الاستعلام عن كافة الطلبيات
    sql='''SELECT left(date_created,10) as date , sum(product_net_revenue) as total
    FROM wp_wc_order_product_lookup 
    where date_created between (%s) and (%s)
    group by    date
    order by date'''
    # معاملات الاستعلام
    param = (startdate, enddate)
    # تنفيذ الاستعلام مع المعاملات
    cursor.execute(sql, param)
    # إحضار كل النتائج
    orders_results = cursor.fetchall()
    # الدوران على الطلبيات
    for order in orders_results:
        # تجهيز قاموس
        x={ "date":[order['date']], "total":[order['total']]}
        dfx=pd.DataFrame(x)
        # الإضافة لإطار البيانات
        df=pd.concat([df, dfx], ignore_index=True)
    return df

def get_last_date():
    from datetime import datetime
    # الاستعلام عن تاريخ آخر طلبية
    sql='''SELECT left(max(date_created),10) as max_date FROM wp_wc_order_product_lookup'''
    cursor.execute(sql)
    # إحضار كل النتائج
    results = cursor.fetchall()
    # آخر تاريخ
    max=results[0]['max_date']
    # التحويل من نص لتاريخ
    max_datetime=datetime.strptime(max, '%Y-%m-%d')
    return max_datetime

# مكتبات التاريخ اللازمة
from datetime import datetime
from datetime import timedelta
# تاريخ النهاية هو تاريخ آخر طلبية
#enddate=datetime.today()
enddate=get_last_date()
# تاريخ البداية هو 60 يوم للوراء
startdate=enddate-timedelta(days=60)

# التحويل إلى نص
enddate=enddate.strftime('%Y-%m-%d')
startdate=startdate.strftime('%Y-%m-%d')
df=get_daily_sales_between_2_dates(startdate, enddate)

# التحويل إلى تاريخ
df['date'] = pd.to_datetime(df['date'])

# ملء الأيام الناقصة

# جعل عمود التاريخ فهرس إطار البيانات
df=df.set_index("date")
# ملء الأيام الناقصة
df = df.resample('D').mean()
# ملء القيم الناقصة بمتوسط الطلبيات
df['total']=df['total'].fillna(df['total'].mean())
# مسح فهرس التاريخ
df=df.reset_index()


# مكتبة السلاسل الزمنية
from autots import AutoTS
# إلغاء إظهار التنبيهات
import warnings
warnings.filterwarnings('ignore')

# طول سلسلة التوقع
forecast_length=10
# التصريح عن نموذج التوقع
model = AutoTS(forecast_length=forecast_length,  frequency='infer')
# ملائمة النموذج
model = model.fit(df, date_col='date', value_col='total')

# تنبؤ النموذج 
prediction = model.predict()
# إطار بيانات نتائج التنبؤ
forecast = prediction.forecast

# حفظ النتائج
# حذف الجدول المخصص مع بياناته
sql = '''
DROP TABLE IF EXISTS  custom_forecast
'''
cursor.execute(sql)
# تعليمة بناء الجدول المخصص
sql='''
CREATE TABLE custom_forecast 
( ID INT NOT NULL AUTO_INCREMENT , 
date datetime NOT NULL , 
total float NOT NULL , 
PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
'''
cursor.execute(sql)
connection_mydb.commit()
# الدوران على نتائج التنبؤ لإضافتها إلى الجدول المخصص
for index,row in forecast.iterrows():
        date=index.strftime('%Y-%m-%d %H:%M:%S')
        total=float(row['total'])
        sql = "INSERT INTO custom_forecast (date, total) VALUES (%s, %s)"
        params = (date, total)
        cursor.execute(sql, params)
        connection_mydb.commit()

# رسم التنبؤ
# مكتبة الرسم
import matplotlib.pyplot as plt
# قياس الرسم
plt.figure(figsize=(12,10)) 
# رسم خط
# المحور الأفقي هو التاريخ
# المحور العمودي هو المبيعات اليومية
plt.plot(forecast.index,forecast['total'])
# تسمية المحور الأفقي
plt.xlabel("Date")   
# تسمية المحور العمودي 
plt.ylabel("Expected Total")
# عنوان الرسم
plt.title("Sales Forecast")
plt.show()