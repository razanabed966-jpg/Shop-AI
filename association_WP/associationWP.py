# مكتبة الاتصال مع قاعدة البيانات
import mysql.connector
# تعريف دالة للاتصال بقاعدة البيانات
connection_mydb = None
cursor = None
def mysql_connect():
    # الاتصال مع قاعدة البيانات
    global cursor, connection_mydb
    connection_mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="wp-ecommerce"
    )
    # مؤشر
    cursor = connection_mydb.cursor(dictionary=True)

# التصريح عن دالة تمرر لها معرف منتج
# تُعيد تسمية المنتج
def get_product_name_from_id(connection_mydb, product_id):
    # مؤشر 
    cursor = connection_mydb.cursor(dictionary=True)
    sql = "SELECT * FROM wp_posts WHERE ID=(%s)"
    id = (product_id, )
    # التنفيذ وتمرير قيمة المعامل
    cursor.execute(sql,id)
    # استحضار كل النتائج
    results = cursor.fetchall()
    if  len(results)>0:
        return results[0]['post_title']  
    # في حال كانت نتيجة الاستعلام فارغة
    return "Unknown Product"

# مكتبة بانداس
import pandas as pd
# التصريح عن دالة مخصصة
# لملء إطار بيانات الإجراءات
def build_dataframe_associated_products(connection_mydb):
    # إطار بيانات للمنتجات التي تباع مع بعضها البعض
    df=pd.DataFrame(columns=[0,1,2,3,4,5,6,7,8,9])
    # مؤشر 
    cursor = connection_mydb.cursor(dictionary=True)
    # الاستعلام عن كل الطلبيات
    sql="SELECT * FROM wp_wc_order_stats order by order_id "
    cursor.execute(sql)
    results_orders = cursor.fetchall()
    # الدوران على كل الطلبيات
    for order in results_orders:
        order_id=order['order_id']
        sql="SELECT * FROM wp_wc_order_product_lookup where order_id=(%s)"
        id=(order_id,)
        cursor.execute(sql, id)
        # منتجات الطلبية الواحدة
        results_products=cursor.fetchall()
        # قائمة لمعرفات المنتجات في الطلبية الواحدة
        products_ids=[]
        for product in results_products:
            product_id=product['product_id']
            if product_id>0:
                df = pd.concat([df, pd.DataFrame([products_ids])], ignore_index=True)
        if len(products_ids)>1:
            df=df.append([products_ids], ignore_index=True)
    return df

# التصريح عن دالة مخصصة
# لإنشاء إطار البيانات اللازم
# لدخل خوارزميات الترابط
def prepare_transactions(df):
    # قلب إطار البيانات
    df =  df.T
    # حذف القيم الفارغة من كل عمود والتحويل لقائمة
    transactions =  df.apply(lambda x: x.dropna().tolist()) 
    # التحويل لمصفوفة من القوائم
    transactions_list = transactions.tolist()
    # مكتبة ترميز الإجراءات
    from mlxtend.preprocessing import TransactionEncoder
    # إنشاء غرض من الصف 
    te = TransactionEncoder()
    # ملائمة المرمز مع البيانات
    te_model = te.fit(transactions_list)
    # تحويل الإجراءات 
    rows=te_model.transform(transactions_list)
    # بناء إطار بيانات الإجراءات 
    df_transactions  = pd.DataFrame(rows, columns=te_model.columns_)
    return df_transactions
 
 # التصريح عن دالة مخصصة
# لإيجاد قواعد الترابط
def generate_association_rules(df_transactions, min_support, min_confidence):
    # مكتبة خوارزمية إيجاد العناصر المتواترة
    from mlxtend.frequent_patterns import apriori
    # توليد المجموعات المتواترة مع تحديد الحد الأدنى للدعم
    frequent_itemsets = apriori(df_transactions, min_support=min_support, use_colnames=True)
    # مكتبة خوارزمية إيجاد قواعد الترابط 
    from mlxtend.frequent_patterns import association_rules
    # توليد القواعد مع تحديد الحد الأدنى للثقة
    rules = association_rules(frequent_itemsets,metric="confidence",min_threshold=min_confidence)
    # الترتيب التنازلي وفق معامل الثقة
    rules = rules.sort_values(['confidence'], ascending =[False])
    return rules
 
def export_to_db(connection_mydb, rules):
    # إنشاء مؤشر على قاعدة البيانات
    cursor = connection_mydb.cursor()
    # تعليمة حذف الجدول وبياناته 
    sql = '''
    DROP TABLE IF EXISTS  custom_products_association
    '''
    # تنفيذ التعليمة
    cursor.execute(sql)
    # تعليمة إنشاء الجدول
    sql = '''
    CREATE TABLE custom_products_association ( ID int(11) NOT NULL AUTO_INCREMENT,
      product_id_in int(11) NOT NULL,
      post_title_in text NOT NULL,
      product_id_out int(11) NOT NULL,
      post_title_out text NOT NULL,
      confidence double NOT NULL , PRIMARY KEY (ID))ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    '''
    # تنفيذ التعليمة
    cursor.execute(sql)
    # تثبيت نتائج التعليمات في قاعدة البيانات
    connection_mydb.commit()
    # الدوران على صفوف القواعد
    for row in rules.itertuples():
      # مقدمة القاعدة
      antecedents=row.antecedents
      # نتيجة القاعدة
      consequents=row.consequents
      # معامل الثقة
      confidence=row.confidence*100
      # الدوران على معرفات المنتجات في مقدمة القاعدة
      for product1 in antecedents:
        # الحصول على اسم المنتج
        post_title_in=get_product_name_from_id(connection_mydb,product1)
        # الدوران على معرفات المنتجات في نتيجة القاعدة
        for product2 in consequents:
          # الحصول على معرف المنتج
          post_title_out=get_product_name_from_id(connection_mydb,product2)
          # حذف كل الارتباطات لنفس المنتجين مع
          # معامل ثقة أصغر من المعامل الجديد
          sql='''DELETE FROM custom_products_association where product_id_in=(%s) and
          product_id_out=(%s) and confidence <= (%s) '''
          # إعداد معاملات الاستعلام
          params = (product1,product2,confidence )
          # التنفيذ وتمرير قيم المعاملات
          cursor.execute(sql,params)
          # الاستعلام عن وجود ارتباط بين نفس
          # المنتجين إنما بمعامل ثقة أكبر
          sql='''SELECT * FROM custom_products_association where product_id_in=(%s) and
          product_id_out=(%s) and confidence >= (%s) '''
          params = (product1,product2,confidence )
          # التنفيذ وتمرير قيمة المعامل
          cursor.execute(sql,params)
          results=cursor.fetchall()
          # في حال وجود ارتباط سابق
          # مع معامل ثقة أكبر
          # لانضيف الارتباط الحالي
          must_add=True
          if results!=None and len(results)>0:
            must_add=False
          if must_add:  
          # إدراج الارتباط في جدول الارتباطات
            sql = "INSERT INTO custom_products_association (product_id_in, post_title_in,product_id_out,post_title_out,confidence) VALUES (%s, %s,%s,%s,%s)"
            # إعداد معملات التعليمة
            val = (product1, post_title_in, product2,  post_title_out, confidence)
            # تنفيذ التعليمة
            cursor.execute(sql, val)
            # التثبيت في قاعدة البيانات 
            connection_mydb.commit()

def start_generate_association_rules():
    mysql_connect()
    # استدعاء الكل
    # بناء إطار الإجراءات للطلبيات
    df=build_dataframe_associated_products(connection_mydb)
    # بناء إطار الإجراءات للترابطات
    transactions_df=prepare_transactions(df)
    # توليد قواعد الترابط
    # معامل الدعم
    min_support = 0.001
    # معامل الثقة
    min_confidence = 0.001
    rules=generate_association_rules(transactions_df,min_support ,min_confidence)
    # التصدير إلى قاعدة البيانات
    export_to_db(connection_mydb, rules)
    # غلق الاتصال مع قاعدة البيانات
    connection_mydb.close()







