# مكتبة بانداس
import pandas as pd
# استيراد مكتبة الرسم
import matplotlib.pyplot as plt
# استيراد مكتبة الرسم
import seaborn as sns

from get_users_profiles import get_users_profiles

# دالة عدد قيم الجنس
def show_users_gender_countplot():
    # مكتبة لإظهار اللغة العربية بشكل صحيح
    import arabic_reshaper
    from bidi.algorithm import get_display
    df_profile=get_users_profiles()
    # تحديد قياس الرسم
    plt.subplots(figsize=(8, 6))
    # عنوان الرسم
    plt.title("Users Gender Count")
    # تحويل قيم الجنس إلى لغة عربية قابلة للإظهار
    df_profile['gender']=df_profile['gender'].apply(lambda a: get_display(arabic_reshaper.reshape(a)))
    # رسم العدد
    ax=sns.countplot(x=df_profile['gender'])
    # إظهار الأعداد على الأشرطة
    ax.bar_label(ax.containers[0])
    # إظهار الرسم
    plt.show()

# استدعاء الدالة
show_users_gender_countplot()
