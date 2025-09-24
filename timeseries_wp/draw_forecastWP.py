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

# مكتبة الرسم
import matplotlib.pyplot as plt
# قياس الرسم
plt.figure(figsize=(12,10)) 
# الستعلام عن بيانات جدول التوقع المخصص
sql='''SELECT * from custom_forecast'''
# التنفيذ وتمرير قيمة المعامل
cursor.execute(sql)
# جلب كل النتائج
results = cursor.fetchall()
#إطار بيانات للنتائج
df=pd.DataFrame(columns=['date','total'])
# الدوران على النتائج
for row in results:
    obj={
            "date":row['date'],
            "total":row['total']}
    # الإضافة إلى إطار البيانات
    df = pd.concat([df, pd.DataFrame([obj])], ignore_index=True)

# رسم خط
# المحور الأفقي هو التاريخ
# المحور العمودي هو المبيعات
plt.plot(df['date'],df['total'])
# تسمية المحور الأفقي
plt.xlabel("Date")   
# تسمية المحور العمودي
plt.ylabel("Expected Total")
# عنوان الرسم
plt.title("Sales Forecast")
# الإظهار
plt.show()