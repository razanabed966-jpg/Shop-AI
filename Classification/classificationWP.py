print("Start building classifier ...")
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

# التصريح عن دالة نُمرر لها معرف منتج
# تُعيد قائمة بمعرفات أصناف المنتج
def get_product_categories(product_id):
    sql='''SELECT wp_term_relationships.object_id,wp_term_taxonomy.term_id
FROM  wp_term_relationships
INNER JOIN wp_term_taxonomy ON wp_term_relationships.term_taxonomy_id = wp_term_taxonomy.term_taxonomy_id
WHERE wp_term_taxonomy.taxonomy ='product_cat' and object_id=(%s)
'''
    # معامل الاستعلام
    param = (product_id, )
    # التنفيذ وتمرير قيمة المعامل
    cursor.execute(sql,param)
    # جلب كل النتائج
    results = cursor.fetchall()
    # قائمة معرفات صنف المنتج
    ar_ids=[]
    # الدوران على النتائج وإضافة معرف الصنف
    for row in results:
        ar_ids.append(row['term_id'])
    return ar_ids

# التصريح عن دالة تمرر لها معرف صنف
# تُعيد تسمية الصنف
def get_category_name_from_id(term_id):

    sql='''    SELECT wp_terms.* FROM wp_terms
         LEFT JOIN wp_term_taxonomy 
         ON wp_terms.term_id = wp_term_taxonomy.term_id
         WHERE wp_term_taxonomy.taxonomy = 'product_cat' and  wp_terms.term_id=(%s)'''
    param = (term_id, )
    # التنفيذ وتمرير قيمة المعامل
    cursor.execute(sql,param)
    # استحضار كل النتائج
    results = cursor.fetchall()
    if results!=None and len(results)>0:
        return results[0]['name']  
    # في حال كانت نتيجة الاستعلام فارغة
    return "Unknown Category"


# دالة بناء إطار بيانات
# يحوي معلومات الزبائن
def construct_customers_data():
    # الاستعلام عن كافة المستخدمين
    sql="SELECT distinct(user_id) FROM wp_usermeta order by user_id "
    cursor.execute(sql)
    users_results = cursor.fetchall()
    #إطار بيانات للنتائج
    df=pd.DataFrame(columns=['user_id','customer_id','country','age',
    'gender','term_id','term_name','count_term_id'])
    # الدوران على المستخدمين
    for user in users_results:
        # البلد
        country="UNKNOWN"
        # العمر
        age=0
        # الجنس
        gender="UNKNOWN"
        # معرف المستخدم
        user_id=user['user_id']
        customer_id=0
        # استعلام البلد
        sql = "SELECT * FROM wp_usermeta  WHERE user_id=(%s) and meta_key='country'"
        param = (user_id, )
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result!=None and len(result)>0:
            country=result[0]['meta_value']
        # استعلام العمر
        sql = "SELECT * FROM wp_usermeta  WHERE user_id=(%s) and meta_key='age'"
        param = (user_id, )
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result!=None and len(result)>0:
            age=result[0]['meta_value']
        # استعلام الجنس
        sql = "SELECT * FROM wp_usermeta  WHERE user_id=(%s) and meta_key='gender'"
        param = (user_id, )
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result!=None and len(result)>0:
            gender=result[0]['meta_value']
        # استعلام لإيجاد معرف الزبون
        sql = "SELECT * FROM wp_wc_customer_lookup  WHERE user_id=(%s) "
        param = (user_id, )
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result!=None and len(result)>0:
            customer_id=result[0]['customer_id']  
        # استعلام لإيجاد طلبيات الزبون
        sql="SELECT * from wp_wc_order_product_lookup where customer_id=(%s)"
        param = (customer_id, )
        cursor.execute(sql, param)
        results_orders = cursor.fetchall()
        # قائمة أصناف المنتجات التي اشتراها الزبون
        categories_list=[]
        # قائمة  المنتجات التي اشتراها الزبون
        products_list=[]
        # معرف الصنف
        term_id=0
        # اسم الصنف
        term_name=""
        # عدد مرات الشراء من الصنف
        count_term_id=0

        for row in results_orders:
            customer_id=row['customer_id']
            product_id=row['product_id']
            # إيجاد معرفات أصناف المنتج
            term_ids=get_product_categories(product_id)
            for term_id in term_ids:
                add_1_category_customer(categories_list, customer_id, term_id)

        # ترتيب قائمة الأصناف تنازليا وفق عدد الطلبيات
        for k in range(len(categories_list)):
            for m in range(k+1,len(categories_list)):
                if (categories_list[k]['count']<categories_list[m]['count']):
                    z=categories_list[k]
                    categories_list[k]=categories_list[m]
                    categories_list[m]=z


        # إضافة أكثر صنف شراء من قبل الزبون
        if len(categories_list)>0:
            term_id=categories_list[0]['term_id']
            count_term_id=categories_list[0]['count']
            term_name=get_category_name_from_id(term_id)
            x={
                "user_id":user_id,
                "customer_id":customer_id,
                "country":country,
                "age":age,
                "gender":gender,
                'term_id':term_id,
                'term_name':term_name,
                'count_term_id':count_term_id
            }
            df = pd.concat([df, pd.DataFrame([x])], ignore_index=True)
    return df

# إضافة واحد إلى عداد زبون/منتج
def add_1_category_customer(category_customer_list, customer_id, term_id):
    item = find_item(category_customer_list,customer_id, term_id)
    item['count'] += 1
# البحث عن زوج زبون منتج
# إن لم يكن موجودا نٌنشئ
# زوج جديد مع عداد يساوي الصفر
def find_item(category_customer_list, customer_id, term_id):
    for item in category_customer_list:
        if item['customer_id'] == customer_id and item['term_id'] == term_id:
            return item
    item = {"customer_id":customer_id,"term_id":term_id,"count":0}
    category_customer_list.append(item)
    return item

# استدعاء الدالة
df =construct_customers_data()

# مكتبة مرمز التسميات
from sklearn.preprocessing import LabelEncoder
# مرمز البلاد
country_LE=LabelEncoder()
# مرمز الجنس
gender_LE=LabelEncoder()
df['country']=country_LE.fit_transform(df['country'])
df['gender']=gender_LE.fit_transform(df['gender'])

X = df[['country','age','gender']]
# الخرج هو معرف الصنف الأكثر شراء 
y = df['term_id']
y=y.astype(int)

# موازنة الأصناف
from imblearn.over_sampling import RandomOverSampler
oversample = RandomOverSampler()
X, y = oversample.fit_resample(X, y)

# مصنف شجرة القرار
from sklearn.tree import DecisionTreeClassifier
# اختيار أشجار القرار
model=DecisionTreeClassifier  ()
# الملائمة
model.fit(X,y)

# حفظ النموذج في ملف
import pickle

filename = 'classification_model'
pickle.dump(model, open(filename, 'wb'))

# مكتبة تحويل النموذج لإجرائية
# في لغة برمجة ما
import m2cgen as m2c 
# توليد إجرائية php
model_to_php = m2c.export_to_php(model)  
# حفظ الإجرائية في ملف
f = open("predict_category.php", "w")
f.write(model_to_php)
f.close()

# حفظ ترميزات البلاد في جدول مخصص
cursor = connection_mydb.cursor(dictionary=True)
sql = '''
DROP TABLE IF EXISTS  custom_country_codes
'''
cursor.execute(sql)
sql='''
CREATE TABLE custom_country_codes (
  ID int(11) NOT NULL AUTO_INCREMENT,
  code int(11) NOT NULL,
  country char(2) NOT NULL, PRIMARY KEY (ID))ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
'''
cursor.execute(sql)
connection_mydb.commit()
# الدوران على قيم مرمز البلاد
for country in country_LE.classes_:
        code=country_LE.transform([country])[0]
        sql = "INSERT INTO custom_country_codes (code, country) VALUES (%s, %s)"
        code=int(code)
        val = (code, country)
        cursor.execute(sql, val)
        connection_mydb.commit()

# حفظ ترميزات الجنس فس جدول مخصص
cursor = connection_mydb.cursor(dictionary=True)
sql = '''
DROP TABLE IF EXISTS  custom_gender_codes
'''
cursor.execute(sql)
sql='''
CREATE TABLE custom_gender_codes (
  ID int(11) NOT NULL AUTO_INCREMENT,
  code int(11) NOT NULL,
  gender char(10) NOT NULL, PRIMARY KEY (ID))ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
'''
cursor.execute(sql)
connection_mydb.commit()
# الدوران على قيم مرمز الجنس
for gender in gender_LE.classes_:
        code=gender_LE.transform([gender])[0]
        sql = "INSERT INTO custom_gender_codes (code, gender) VALUES (%s, %s)"
        code=int(code)
        val = (code, gender)
        cursor.execute(sql, val)
        connection_mydb.commit()



print("End building classifier ...")