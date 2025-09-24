# مكتبة بانداس
import pandas as pd
# استيراد مكتبة الرسم
import matplotlib.pyplot as plt

from get_users_profiles import get_users_profiles

# دالة رسم فطيرة توزع الجنس
def show_users_gender_pie():
    # إطار لبيانات المستخدمين
    df_profile=get_users_profiles()
    # التجميع وفق الجنس وعد المستخدمين من أجل كل قيمة
    df_gender=df_profile[['gender','user_id']].groupby('gender').count()

    # مكتبة لإظهار اللغة العربية بشكل صحيح
    import arabic_reshaper
    from bidi.algorithm import get_display
    # إعادة الفهرسة
    df_gender=df_gender.reset_index()
    # تحويل قيم الجنس إلى لغة عربية قابلة للإظهار
    df_gender['gender']=df_gender['gender'].apply(lambda a: get_display(arabic_reshaper.reshape(a)))
    # رسم الفطيرة
    plt.pie(df_gender['user_id'], labels = df_gender['gender'], autopct='%1.1f%%')
    # عنوان الرسم
    plt.title('Gender Pie')
    # الإظهار
    plt.show()

# استدعاء الدالة
show_users_gender_pie()
