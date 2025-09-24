# مكتبة بانداس
import pandas as pd
# استيراد مكتبة الرسم
import matplotlib.pyplot as plt

from get_users_profiles import get_users_profiles

# دالة رسم مخطط الكثافة للعمر
def show_users_age_density():
    df_profile=get_users_profiles()
    # اختيار عمود العمر
    df_age=df_profile['age']
    # رسم مخطط الكثافة
    df_age.plot(kind='density')
    # عنوان المحور الأفقي
    plt.xlabel("Age")
    # عنوان المحور العمودي
    plt.ylabel("Density")
    # عنوان الرسم
    plt.title("Users Age Density")
    plt.show()

# استدعاء الدالة
show_users_age_density()