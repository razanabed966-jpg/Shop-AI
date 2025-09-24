# دالة إيجاد معرف التصنيف المناسب
def get_category_code(filename, country, age, gender):
   
    import pickle
    # تحميل النموذج من ملف
    loaded_model = pickle.load(open(filename, 'rb'))
    # قائمة الدخل لنموذج التصنيف
    example=[country,age,gender]

    # التنبؤ
    result = loaded_model.predict([example])
    return result[0]

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

# إيجاد معرفات المنتجات الأكثر مبيعا من صنف منتجات
def category_best_seller_products(category_id, n=3):
    cursor = connection_mydb.cursor(dictionary=True)
    sql='''SELECT  wp_term_taxonomy.term_id,
                   wp_wc_order_product_lookup.product_id,  
                   sum(wp_wc_order_product_lookup.product_qty) as sumsales
FROM wp_wc_order_product_lookup 
INNER JOIN wp_term_relationships  ON wp_term_relationships.object_id=wp_wc_order_product_lookup.product_id
INNER JOIN wp_term_taxonomy ON wp_term_relationships.term_taxonomy_id = wp_term_taxonomy.term_taxonomy_id
WHERE wp_term_taxonomy.taxonomy ='product_cat'   and 
wp_term_taxonomy.term_id=(%s)
group by wp_term_taxonomy.term_id,wp_wc_order_product_lookup.product_id
order by sumsales DESC'''
    # معامل الاستعلام
    param = (category_id, )
    # التنفيذ وتمرير قيمة المعامل
    cursor.execute(sql,param)
    results = cursor.fetchall()
    products_ids=[]
    if results!=None:
        # الدوران بعدد المنتجات المطلوبة
        i=0
        while i<n and i<len(results):
            product_id=results[i]['product_id']
            products_ids.append(product_id)
            i=i+1
    return products_ids

# التصريح عن دالة تمرر لها معرف منتج
# تُعيد تسمية المنتج
def get_product_name(product_id):
    # مؤشر 
    cursor = connection_mydb.cursor(dictionary=True)
    sql = "SELECT post_title FROM wp_posts WHERE ID=(%s)"
    id = (product_id,)
    # التنفيذ وتمرير قيمة المعامل
    cursor.execute(sql,id)
    # جلب كل النتائج
    results = cursor.fetchall()
    if  len(results)>0:
        return results[0]['post_title']  
    # في حال كانت نتيجة الاستعلام فارغة
    return "Unknown Product"

# إيجاد رمز جنس
def get_gender_code(gender):
    cursor = connection_mydb.cursor(dictionary=True)
    # الاستعلام من جدول ترميز الجنس المخصص
    sql = "SELECT code FROM custom_gender_codes  WHERE gender=(%s) "
    param = (gender, )
    cursor.execute(sql, param)
    result = cursor.fetchall()
    if result!=None and len(result)>0:
        return result[0]['code']
    else:
        0
# إيجاد رمز بلد
def get_country_code(country):
    cursor = connection_mydb.cursor(dictionary=True)
    # الاستعلام من جدول ترميز البلاد المخصص
    sql = "SELECT code FROM custom_country_codes  WHERE country=(%s) "
    param = (country, )
    cursor.execute(sql, param)
    result = cursor.fetchall()
    
    if result!=None and len(result)>0:
        return result[0]['code']
    else:
        0

# إيجاد المنتجات المناسبة لزبون وفق مواصفاته
def get_customer_products(customer_id,n=3):
        cursor = connection_mydb.cursor(dictionary=True)
        user_id=0
        # استعلام لإيجاد معرف المستخدم
        sql = "SELECT user_id FROM wp_wc_customer_lookup  WHERE customer_id=(%s) "
        param = (customer_id, )
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result!=None and len(result)>0:
            user_id=result[0]['user_id']  
       
        # استعلام البلد
        country=""
        sql = "SELECT meta_value FROM wp_usermeta  WHERE user_id=(%s) and meta_key='country'"
        param = (user_id, )
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result!=None and len(result)>0:
            country=result[0]['meta_value']
        # إيجاد رمز البلد
        country_code=get_country_code(country)
 
        # استعلام العمر
        age=0
        sql = "SELECT meta_value FROM wp_usermeta  WHERE user_id=(%s) and meta_key='age'"
        param = (user_id, )
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result!=None and len(result)>0:
            age=int(result[0]['meta_value'])

        # استعلام الجنس
        gender=""
        sql = "SELECT meta_value FROM wp_usermeta  WHERE user_id=(%s) and meta_key='gender'"
        param = (user_id, )
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result!=None and len(result)>0:
            gender=result[0]['meta_value']
        # إيجاد رمز العمر
        gender_code=get_gender_code(gender)
        # إيجاد معرف صنف المنتجات المناسب
        category_code=get_category_code('classification_model', country_code, age, gender_code)
        # إيجاد معرفات المنتجات الأكثر مبيعا في صنف المنتجات المناسب
        products_ids=category_best_seller_products(int(category_code), n)
        # إيجاد أسماء المنتجات
        products=[]
        for id in products_ids:
             # إيجاد اسم المنتج
             product=get_product_name(id)
             products.append(product)
        return products