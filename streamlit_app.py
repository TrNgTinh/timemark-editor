"""
Timemark Editor - Web App Version
Chạy trên điện thoại, miễn phí 100%
Version 2.1 - Custom font support
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="Timemark Editor - Free",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Đẹp hơn
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #0f3460 0%, #16537e 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.75rem;
        border-radius: 0.5rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,212,255,0.3);
    }
    h1 {
        color: #00d4ff;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 0;
    }
    h3 {
        color: #00d4ff;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .info-box {
        background: rgba(0, 212, 255, 0.1);
        border-left: 4px solid #00d4ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background: rgba(0, 255, 100, 0.1);
        border-left: 4px solid #00ff64;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stDownloadButton>button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        font-size: 1.1rem;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to download font from URL
@st.cache_resource
def download_font_from_url(url, filename):
    """Download font file from URL and cache it"""
    import urllib.request
    try:
        # Download to temp location
        urllib.request.urlretrieve(url, filename)
        return True
    except Exception as e:
        st.warning(f"⚠️ Không thể tải font từ URL: {str(e)}")
        return False

# Helper function to load font
@st.cache_resource
def load_font(size):
    """Load custom font with fallback and size compensation"""
    
    # Try to download font from Google Fonts if not exists locally
    font_url = "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Bold.ttf"
    local_font_file = "downloaded_font.ttf"
    
    # Download font if not exists
    if not os.path.exists(local_font_file) and not os.path.exists("arial.ttf"):
        download_font_from_url(font_url, local_font_file)
    
    font_paths = [
        "arial.ttf",  # Custom font in root directory
        local_font_file,  # Downloaded font
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Alternative Linux
        "C:/Windows/Fonts/arial.ttf",  # Windows (local)
    ]
    
    # Try to load custom fonts
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size), False
        except Exception as e:
            continue
    
    # If all fail, use default font with size compensation
    # Default font is much smaller, so we need to scale up
    try:
        # Try to create a larger default font
        return ImageFont.load_default(), True  # Return flag indicating default font
    except:
        return ImageFont.load_default(), True

# Helper function to generate image
def generate_image_with_position(input_image, date_str, time_str, ward, district, province, country, font_size, position):
    """Generate image with text at specified position"""
    output = input_image.copy()
    draw = ImageDraw.Draw(output)
    
    # Load font
    font, is_default = load_font(font_size)
    
    # If using default font, compensate for smaller size
    if is_default:
        # Default font is about 3x smaller, so multiply spacing
        actual_font_size = font_size * 3
        line_spacing_multiplier = 3
    else:
        actual_font_size = font_size
        line_spacing_multiplier = 1
    
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
    line_spacing = (actual_font_size + 10) * line_spacing_multiplier
    
    # Calculate position
    if position == "top-left":
        x = padding
        y = padding
    elif position == "top-right":
        x = img_width - padding
        y = padding
    elif position == "bottom-left":
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
        
        if 'right' in position:
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                # If default font, multiply width
                if is_default:
                    text_width = text_width * line_spacing_multiplier
            except:
                # Fallback calculation
                text_width = len(text) * (actual_font_size // 2)
            text_x = x - text_width
        else:
            text_x = x
        
        # If using default font, draw text multiple times to make it bolder and larger
        if is_default:
            # Draw multiple times with slight offsets to simulate larger size
            for dx in range(line_spacing_multiplier):
                for dy in range(line_spacing_multiplier):
                    # Shadow
                    draw.text((text_x+2+dx, current_y+2+dy), text, font=font, fill=shadow_color)
            for dx in range(line_spacing_multiplier):
                for dy in range(line_spacing_multiplier):
                    # Main text
                    draw.text((text_x+dx, current_y+dy), text, font=font, fill=text_color)
        else:
            # Normal rendering for custom fonts
            # Shadow
            draw.text((text_x+2, current_y+2), text, font=font, fill=shadow_color)
            # Main text
            draw.text((text_x, current_y), text, font=font, fill=text_color)
    
    return output

# Title
st.markdown("# 📝 TIMEMARK EDITOR")
st.markdown("<p class='subtitle'>✨ Miễn phí 100% - Chạy trên mọi thiết bị</p>", unsafe_allow_html=True)

# Info box
st.markdown("""
<div class='info-box'>
    <b>🎯 Hướng dẫn nhanh:</b><br>
    1️⃣ Upload ảnh từ điện thoại<br>
    2️⃣ Điền thông tin ngày giờ, địa chỉ<br>
    3️⃣ Chọn vị trí text hoặc xuất 4 góc<br>
    4️⃣ Tải ảnh về điện thoại<br>
    💰 <b>Chi phí: $0</b> - Hoàn toàn miễn phí!
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Layout
col1, col2 = st.columns([1, 1.3])

with col1:
    st.markdown("### 📷 Upload ảnh")
    uploaded_file = st.file_uploader(
        "Chọn ảnh từ điện thoại",
        type=['png', 'jpg', 'jpeg'],
        help="Chọn ảnh cần thêm thông tin",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        input_image = Image.open(uploaded_file)
        st.image(input_image, caption="✅ Ảnh gốc", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ✏️ Thông tin")
    
    col_date, col_time = st.columns(2)
    with col_date:
        date_str = st.text_input("📅 Ngày", value="29/12/2025", placeholder="DD/MM/YYYY")
    with col_time:
        time_str = st.text_input("🕐 Giờ", value="12:31:00", placeholder="HH:MM:SS")
    
    st.markdown("**📍 Địa chỉ:**")
    ward = st.text_input("🏘️ Xã/Phường", value="X. Chu Đăng Ya")
    district = st.text_input("🏙️ Huyện/Quận", value="H. Chu Păh")
    province = st.text_input("🌆 Tỉnh/TP", value="Gia Lai")
    country = st.text_input("🌏 Quốc gia", value="Việt Nam")
    
    font_size = st.slider("🔤 Cỡ chữ", 20, 100, 40, help="Kéo để điều chỉnh kích thước chữ")
    
    st.markdown("**📍 Vị trí text:**")
    position = st.radio(
        "Chọn vị trí",
        ["↖ Trên trái", "↗ Trên phải", "↙ Dưới trái", "↘ Dưới phải"],
        index=1,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    position_map = {
        "↖ Trên trái": "top-left",
        "↗ Trên phải": "top-right",
        "↙ Dưới trái": "bottom-left",
        "↘ Dưới phải": "bottom-right"
    }

with col2:
    st.markdown("### 📸 Kết quả")
    
    if uploaded_file:
        # Two buttons side by side
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            generate_single = st.button("🎨 TẠO 1 ẢNH", type="primary", use_container_width=True)
        
        with btn_col2:
            generate_all = st.button("📸 XUẤT 4 GÓC", type="secondary", use_container_width=True)
        
        # Generate single image
        if generate_single:
            with st.spinner("⏳ Đang xử lý..."):
                try:
                    pos = position_map[position]
                    output = generate_image_with_position(
                        input_image, date_str, time_str, ward, district, 
                        province, country, font_size, pos
                    )
                    
                    # Display result
                    st.image(output, caption="✅ Ảnh đã chỉnh sửa", use_container_width=True)
                    
                    # Download button
                    buf = io.BytesIO()
                    output.save(buf, format='JPEG', quality=95)
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="💾 TẢI ẢNH VỀ ĐIỆN THOẠI",
                        data=byte_im,
                        file_name=f"timemark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                        mime="image/jpeg",
                        use_container_width=True
                    )
                    
                    st.markdown("""
                    <div class='success-box'>
                        ✅ <b>Tạo ảnh thành công!</b><br>
                        Click nút trên để tải về điện thoại
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
        
        # Generate 4 corners
        elif generate_all:
            with st.spinner("⏳ Đang tạo 4 ảnh ở 4 góc..."):
                try:
                    positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
                    position_names = ["↖ Trên trái", "↗ Trên phải", "↙ Dưới trái", "↘ Dưới phải"]
                    
                    # Create ZIP file
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for pos, pos_name in zip(positions, position_names):
                            output = generate_image_with_position(
                                input_image, date_str, time_str, ward, district,
                                province, country, font_size, pos
                            )
                            
                            # Save to buffer
                            img_buffer = io.BytesIO()
                            output.save(img_buffer, format='JPEG', quality=95)
                            img_buffer.seek(0)
                            
                            # Add to ZIP
                            filename = f"timemark_{pos.replace('-', '_')}.jpg"
                            zip_file.writestr(filename, img_buffer.getvalue())
                    
                    zip_buffer.seek(0)
                    
                    # Show preview of first image
                    output_preview = generate_image_with_position(
                        input_image, date_str, time_str, ward, district,
                        province, country, font_size, "top-right"
                    )
                    st.image(output_preview, caption="✅ Preview (Trên phải)", use_container_width=True)
                    
                    # Download ZIP button
                    st.download_button(
                        label="📦 TẢI 4 ẢNH (ZIP) VỀ ĐIỆN THOẠI",
                        data=zip_buffer.getvalue(),
                        file_name=f"timemark_4corners_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                    
                    st.markdown("""
                    <div class='success-box'>
                        ✅ <b>Đã tạo 4 ảnh thành công!</b><br>
                        📦 File ZIP chứa 4 ảnh ở 4 góc khác nhau<br>
                        💰 Chi phí: $0 (Miễn phí!)
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.info("💡 **Mẹo:** Sau khi tải về, giải nén file ZIP để lấy 4 ảnh")
                    
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
        
        else:
            st.info("👆 Click nút phía trên để tạo ảnh")
    else:
        st.info("👈 Upload ảnh bên trái để bắt đầu")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 2rem 0;'>
    <h4 style='color: #00d4ff;'>💰 Hoàn toàn miễn phí</h4>
    📱 Hoạt động trên mọi thiết bị (PC, điện thoại, tablet)<br>
    🔒 Ảnh được xử lý trực tiếp trên server, không lưu trữ<br>
    ⚡ Nhanh - Đơn giản - Miễn phí<br><br>
    <small>Made with ❤️ using Streamlit</small>
</div>
""", unsafe_allow_html=True)
