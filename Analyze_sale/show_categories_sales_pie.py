# مكتبة بانداس
import pandas as pd
# استيراد المكتبة
import matplotlib.pyplot as plt


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

# دالة رسم فطيرة توزع مبيعات الأصناف
def show_categories_sales_pie():
    # إطار لبيانات المستخدمين
    df=get_categories_sales()
    # مكتبة لإظهار اللغة العربية بشكل صحيح
    import arabic_reshaper
    from bidi.algorithm import get_display
    # تحويل قيم الجنس إلى لغة عربية قابلة للإظهار
    df['Category']=df['Category'].apply(lambda a: get_display(arabic_reshaper.reshape(a)))
    # قياس الرسم
    plt.figure(figsize=(10,6))
    # رسم الفطيرة
    plt.pie(df['Sales'], labels = df['Category'], autopct='%1.1f%%')
    # عنوان الرسم
    plt.title('Categories Sales Pie')
    # الإظهار
    plt.show()

# استدعاء الدالة
show_categories_sales_pie()
