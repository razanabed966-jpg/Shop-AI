# مكتبة بانداس
import pandas as pd
# استيراد مكتبة الرسم
import matplotlib.pyplot as plt

from get_users_profiles import get_users_profiles

# دالة رسم المدرج التكراري للعمر
def show_users_age_hist():
    df_profile=get_users_profiles()
    # اختيار عمود العمر
    df_age=df_profile['age']
    # رسم المدرج التكراري
    df_age.hist(bins=[0,10,20,30,40,50,60,70,80])
    # عنوان المحور الأفقي
    plt.xlabel("Age")
    # عنوان المحور العمودي
    plt.ylabel("Count")
    # عنوان الرسم
    plt.title("Users Age Histogram")
    plt.show()

# استدعاء دالة رسم المدرج التكراري للعمر
show_users_age_hist()