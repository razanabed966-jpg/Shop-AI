# مكتبة بانداس
import pandas as pd
# استيراد المكتبة
import matplotlib.pyplot as plt
# المكتبة الرياضية
import numpy as np

# دالة إنشاء اتصال ومؤشر على قاعدة البيانات
def make_connection_with_db():
  # مكتبة الاتصال مع قاعدة البيانات
  import mysql.connector
  # الاتصال مع قاعدة البيانات
  connection_mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="wp-ecommerce"
  )
  # مؤشر 
  cursor = connection_mydb.cursor(dictionary=True)
  return connection_mydb,cursor

# دالة إيجاد مجموع الكميات المباعة من كل صنف منتجات
def get_categories_sales():
    # اتصال ومؤشر على قاعدة البيانات
    _,cursor=make_connection_with_db()
    # الاستعلام عن مجموع الكميات المباعة من كل صنف منتجات
    sql='''SELECT wp_term_taxonomy.term_id , wp_terms.name ,   
    sum(wp_wc_order_product_lookup.product_qty) as sumsales
FROM wp_wc_order_product_lookup 
INNER JOIN wp_term_relationships  ON wp_term_relationships.object_id=wp_wc_order_product_lookup.product_id
INNER JOIN wp_term_taxonomy ON wp_term_relationships.term_taxonomy_id = wp_term_taxonomy.term_taxonomy_id
INNER JOIN wp_terms ON wp_terms.term_id = wp_term_taxonomy.term_id
WHERE wp_term_taxonomy.taxonomy ='product_cat' 
group by wp_term_taxonomy.term_id '''

    # تنفيذ الاستعلام
    cursor.execute(sql)
    # جلب كل النتائج
    results = cursor.fetchall()
    #إطار بيانات للنتائج
    df=pd.DataFrame(columns=['category_id','Category','Sales'])
    # الدورن على النتائج
    for row in results:
            # معرف الصنف
            category_id=row['term_id']
            # اسم الصنف
            Category=row['name']
            # مجموع الكميات المباعة من منتجات الصنف
            Sales=row['sumsales']
            # إنشاء غرض مفتاح/قيمة
            obj={
                "category_id":[category_id],
                "Category":[Category],
                "Sales":[Sales]
                }
            df_obj=pd.DataFrame(obj)
            # إضافة صف إلى إطار البيانات
            df=pd.concat([df,df_obj], ignore_index=True)     
    return df

# دالة إظهار مخطط أشرطة لمبيعات أصناف المنتجات
def show_customers_by_countries_bars():
    df=get_categories_sales()
    # مكتبة لإظهار اللغة العربية بشكل صحيح
    import arabic_reshaper
    from bidi.algorithm import get_display
    # تحويل أسماء الأصناف إلى لغة عربية قابلة للإظهار
    df['Category']=df['Category'].apply(lambda a: get_display(arabic_reshaper.reshape(a)))
    # رسم الفطيرة
    # تحديد المحور الأفقي
    x = df['Category']
    # تحديد المحور العمودي
    y = df['Sales']
    # قياس الرسم
    plt.figure(figsize=(10,6))
    # إضافة تسميات المحاور
    plt.xlabel("Category")
    plt.ylabel("Sales")
    # إضافة العنوان
    plt.title('Sales per Categories')
    # ألوان الأشرطة
    colors=[]
    for i in range(len(x)):
        # توليد قائمة بالوان عشوائية
        colors.append([np.random.rand(),np.random.rand(),np.random.rand()])
        # إظهار القيم على الأشرطة
        plt.text(x=i, y=y[i], s=y[i])
    
    # رسم الأشرطة
    plt.bar(x,y, color=colors)
    # إظهار الرسم
    plt.show()

    # استدعاء الدالة
show_customers_by_countries_bars()
