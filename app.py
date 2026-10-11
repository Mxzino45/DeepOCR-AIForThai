import streamlit as st
import requests
from PIL import Image
import io

# กำหนดการตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="DeepOCR: ระบบสกัดตัวอักษรจากภาพ",
    page_icon="🔍",
    layout="centered"
)

# ส่วน Header
st.title("DeepOCR: ระบบสกัดตัวอักษรจากภาพ")
st.markdown("---")

# กำหนด API Key (สามารถแก้ไขตรงนี้หรือใส่ใน Sidebar ได้)
API_KEY = "YOUR_API_KEY"

# หรือให้ผู้ใช้กรอก API Key เองหากยังไม่ได้ระบุในโค้ด
with st.sidebar:
    st.header("⚙️ การตั้งค่า API")
    user_api_key = st.text_input("ระบุ AIForThai API Key (ถ้ามี):", value=API_KEY if API_KEY != "YOUR_API_KEY" else "", type="password")
    if user_api_key:
        API_KEY = user_api_key
    st.caption("สมัครรับ API Key ได้ที่ [aiforthai.in.th](https://aiforthai.in.th)")

# File Uploader อนุญาตเฉพาะ .jpg และ .jpeg
uploaded_file = st.file_uploader(
    "เลือกไฟล์รูปภาพที่ต้องการแปลงเป็นข้อความ (รองรับเฉพาะ .jpg, .jpeg)",
    type=["jpg", "jpeg"]
)

if uploaded_file is not None:
    # แสดงรูปภาพพรีวิวบนหน้าเว็บ
    st.image(uploaded_file, caption="รูปภาพที่อัปโหลด", use_container_width=True)

    # ปุ่มแปลงภาพเป็นข้อความ
    if st.button("แปลงภาพเป็นข้อความ", type="primary"):
        if not API_KEY or API_KEY == "YOUR_API_KEY":
            st.warning("⚠️ กรุณาระบุ AIForThai API Key ที่ถูกต้องก่อนดำเนินการ")
        else:
            with st.spinner("กำลังประมวลผลข้อความจากภาพ..."):
                try:
                    url = "https://api.aiforthai.in.th/panyapradit-ocr"
                    headers = {
                        'Apikey': API_KEY
                    }
                    # แนบไฟล์ในรูปแบบ files={'uploadfile': (file.name, file.getvalue())}
                    # อ่านไฟล์ภาพด้วย Pillow และแปลงเป็นโหมด RGB (ตัดความโปร่งใสออก)
                    image = Image.open(uploaded_file)
                    image = image.convert('RGB')
                    
                    # แปลงภาพกลับเป็นไบต์ (Bytes) ในรูปแบบ JPEG
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()

                    # แนบไฟล์ที่แปลงแล้วส่งไปที่ API
                    files = {'file': (uploaded_file.name, img_byte_arr, 'image/jpeg')}

                    # ส่ง HTTP POST Request
                    response = requests.post(url, headers=headers, files=files, timeout=60)

                    # ตรวจสอบ HTTP Status Code
                    if response.status_code == 200:
                        try:
                            # ลองดึงข้อมูลแบบ JSON ดูก่อน
                            result = response.json()
                            if isinstance(result, dict):
                                extracted_text = result.get("text") or result.get("result") or str(result)
                            elif isinstance(result, list):
                                extracted_text = "\n".join([str(item) for item in result])
                            else:
                                extracted_text = str(result)
                        except ValueError:
                            # ถ้าไม่ใช่ JSON (เกิด Error) แสดงว่า API ตอบเป็นข้อความตรงๆ ให้ใช้ response.text ได้เลย
                            extracted_text = response.text.strip()

                        st.success("✅ สกัดข้อความสำเร็จ!")
                        st.subheader("ข้อความที่ได้:")
                        
                        # แสดงผลด้วยฟอนต์ขนาดใหญ่และอ่านง่าย
                        st.markdown(
                            f"""
                            <div style="
                                background-color: #f8f9fa;
                                border: 1px solid #dee2e6;
                                border-radius: 8px;
                                padding: 20px;
                                font-size: 22px;
                                line-height: 1.6;
                                color: #212529;
                                white-space: pre-wrap;
                                word-break: break-word;
                            ">
                                {extracted_text}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    else:
                        st.error(f"❌ เกิดข้อผิดพลาดจาก API (Status Code: {response.status_code})")
                        st.info(f"รายละเอียด: {response.text}")

                except requests.exceptions.Timeout:
                    st.error("⏳ หมดเวลาเชื่อมต่อ (Request Timeout) กรุณาลองใหม่อีกครั้ง")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้: {e}")
                except Exception as e:
                    st.error(f"⚠️ เกิดข้อผิดพลาดในการประมวลผล: {e}")
