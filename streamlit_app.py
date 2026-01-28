"""
Timemark Editor - Web App Version
Chạy trên điện thoại, miễn phí 100%
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Timemark Editor - Free",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #1a1a2e;
    }
    .stButton>button {
        width: 100%;
        background-color: #0f3460;
        color: white;
        font-weight: bold;
    }
    h1 {
        color: #00d4ff;
        text-align: center;
    }
    .success-box {
        padding: 1rem;
        background-color: #00d4ff22;
        border-radius: 0.5rem;
        border-left: 4px solid #00d4ff;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("# 📝 TIMEMARK EDITOR")
st.markdown("### ✨ Miễn phí 100% - Chạy trên điện thoại")

# Info
with st.expander("ℹ️ Hướng dẫn sử dụng"):
    st.markdown("""
    1. **Upload ảnh** từ điện thoại
    2. **Điền thông tin** ngày giờ, địa chỉ
    3. **Chọn vị trí** text (4 góc)
    4. **Tải ảnh về** điện thoại
    
    💰 **Chi phí:** $0 - Hoàn toàn miễn phí!
    """)

st.markdown("---")

# Layout
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("### 📷 Upload ảnh")
    uploaded_file = st.file_uploader(
        "Chọn ảnh từ điện thoại",
        type=['png', 'jpg', 'jpeg'],
        help="Chọn ảnh cần thêm thông tin"
    )
    
    if uploaded_file:
        input_image = Image.open(uploaded_file)
        st.image(input_image, caption="Ảnh gốc", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ✏️ Thông tin")
    
    date_str = st.text_input("📅 Ngày (DD/MM/YYYY)", value="29/12/2025")
    time_str = st.text_input("🕐 Giờ (HH:MM:SS)", value="12:31:00")
    
    st.markdown("**📍 Địa chỉ:**")
    ward = st.text_input("Xã/Phường", value="X. Chu Đăng Ya")
    district = st.text_input("Huyện/Quận", value="H. Chu Păh")
    province = st.text_input("Tỉnh/TP", value="Gia Lai")
    country = st.text_input("Quốc gia", value="Việt Nam")
    
    font_size = st.slider("🔤 Cỡ chữ", 20, 100, 40)
    
    position = st.radio(
        "📍 Vị trí text",
        ["Trên trái", "Trên phải", "Dưới trái", "Dưới phải"],
        index=1,
        horizontal=True
    )
    
    position_map = {
        "Trên trái": "top-left",
        "Trên phải": "top-right",
        "Dưới trái": "bottom-left",
        "Dưới phải": "bottom-right"
    }

with col2:
    st.markdown("### 📸 Kết quả")
    
    if uploaded_file:
        if st.button("🎨 TẠO ẢNH", type="primary"):
            with st.spinner("⏳ Đang xử lý..."):
                try:
                    # Generate image
                    output = input_image.copy()
                    draw = ImageDraw.Draw(output)
                    
                    # Load font
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                    
                    # Format datetime
                    try:
                        day, month, year = date_str.split('/')
                        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                        month_name = month_names[int(month) - 1]
                        datetime_text = f"{int(day)} {month_name} {year} at {time_str}"
                    except:
                        datetime_text = f"{date_str} at {time_str}"
                    
                    # Prepare texts
                    texts = [t for t in [datetime_text, ward, district, province, country] if t]
                    
                    img_width, img_height = output.size
                    padding = 30
                    line_spacing = font_size + 10
                    
                    # Calculate position
                    pos = position_map[position]
                    if pos == "top-left":
                        x = padding
                        y = padding
                    elif pos == "top-right":
                        x = img_width - padding
                        y = padding
                    elif pos == "bottom-left":
                        x = padding
                        total_height = len(texts) * line_spacing
                        y = img_height - total_height - padding
                    else:  # bottom-right
                        x = img_width - padding
                        total_height = len(texts) * line_spacing
                        y = img_height - total_height - padding
                    
                    # Draw text
                    text_color = (255, 255, 255)
                    shadow_color = (0, 0, 0)
                    
                    for i, text in enumerate(texts):
                        current_y = y + (i * line_spacing)
                        
                        if 'right' in pos:
                            bbox = draw.textbbox((0, 0), text, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_x = x - text_width
                        else:
                            text_x = x
                        
                        draw.text((text_x+2, current_y+2), text, font=font, fill=shadow_color)
                        draw.text((text_x, current_y), text, font=font, fill=text_color)
                    
                    # Display result
                    st.image(output, caption="Ảnh đã chỉnh sửa", use_container_width=True)
                    
                    # Download button
                    buf = io.BytesIO()
                    output.save(buf, format='JPEG', quality=95)
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="💾 TẢI ẢNH VỀ ĐIỆN THOẠI",
                        data=byte_im,
                        file_name=f"timemark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                        mime="image/jpeg",
                        type="primary"
                    )
                    
                    st.success("✅ Tạo ảnh thành công! Click nút trên để tải về.")
                    
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
    else:
        st.info("👈 Upload ảnh bên trái để bắt đầu")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    💰 <b>Chi phí: $0</b> - Miễn phí 100%<br>
    📱 Hoạt động trên mọi thiết bị<br>
    🔒 Ảnh được xử lý trực tiếp, không lưu trữ
</div>
""", unsafe_allow_html=True)
