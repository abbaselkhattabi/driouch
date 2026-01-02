import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
import requests
from io import BytesIO

# --- إعدادات ووردبريس الأمنة ---
WP_URL = "https://driouchcity.com/wp-json/wp/v2"
WP_USER = "ADMIN"

# استدعاء كلمة المرور من الإعدادات السرية (Secrets) لضمان الأمان على GitHub
try:
    WP_APP_PASSWORD = st.secrets["WP_PASSWORD"]
except KeyError:
    st.error("خطأ: لم يتم العثور على 'WP_PASSWORD' في إعدادات Secrets.")
    st.stop()

def upload_to_wordpress(img, title, content):
    """وظيفة لرفع الصورة وإنشاء المقال في ووردبريس"""
    buf = BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    headers = {
        "Content-Disposition": "attachment; filename=driouch_image.png",
        "Content-Type": "image/png"
    }
    
    # 1. رفع الصورة كـ Media
    media_res = requests.post(
        f"{WP_URL}/media",
        headers=headers,
        auth=(WP_USER, WP_APP_PASSWORD),
        data=img_bytes
    )
    
    if media_res.status_code == 201:
        media_id = media_res.json()['id']
        # 2. إنشاء المقال وربط الصورة به كـ Featured Image
        post_data = {
            "title": title,
            "content": content,
            "featured_media": media_id,
            "status": "publish"
        }
        post_res = requests.post(f"{WP_URL}/posts", auth=(WP_USER, WP_APP_PASSWORD), json=post_data)
        return post_res.status_code == 201
    return False

# --- واجهة تطبيق Streamlit ---
st.set_page_config(page_title="محرر الدريوش سيتي", layout="centered", page_icon="🗞️")

st.title("🗞️ محرر ونشر الأخبار - DriouchCity")
st.markdown("---")

# خيارات جلب الصورة
source = st.radio("اختر مصدر الصورة:", ("رفع من جهازك", "رابط من الإنترنت"))
image = None

if source == "رفع من جهازك":
    file = st.file_uploader("اختر ملف الصورة", type=["jpg", "png", "jpeg"])
    if file: 
        image = Image.open(file)
else:
    url = st.text_input("ضع رابط الصورة هنا (URL):")
    if url:
        try:
            response = requests.get(url)
            image = Image.open(BytesIO(response.content))
        except: 
            st.error("فشل جلب الصورة، تأكد من صحة الرابط.")

# عمليات التعديل على الصورة
if image:
    st.subheader("🛠️ أدوات التعديل السريع")
    col1, col2 = st.columns(2)
    
    with col1:
        sat = st.slider("إشباع الألوان (Saturation)", 0.0, 2.0, 1.0)
        bright = st.slider("إضاءة الصورة (Brightness)", 0.0, 2.0, 1.0)
    
    with col2:
        if st.button("قلب الصورة أفقياً ↔️"):
            image = ImageOps.mirror(image)
        crop = st.checkbox("قص تلقائي (حواف 10%)")

    # تطبيق الفلاتر
    image = ImageEnhance.Color(image).enhance(sat)
    image = ImageEnhance.Brightness(image).enhance(bright)
    
    if crop:
        w, h = image.size
        image = image.crop((w*0.1, h*0.1, w*0.9, h*0.9))
    
    st.image(image, caption="معا
