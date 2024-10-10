import streamlit as st
from PIL import Image, ImageOps
import io
import zipfile

def load_mockup_image(path):
    """Load the mockup image."""
    return Image.open(path)

def resize_and_crop(image, target_size):
    """Resize and crop the image to fit the target size while maintaining aspect ratio."""
    # Resize the image to be larger than the target size while maintaining aspect ratio
    image_ratio = image.width / image.height
    target_ratio = target_size[0] / target_size[1]

    if image_ratio > target_ratio:
        # Image is wider than target, fit by height
        new_height = target_size[1]
        new_width = int(new_height * image_ratio)
    else:
        # Image is taller than target, fit by width
        new_width = target_size[0]
        new_height = int(new_width / image_ratio)

    image = image.resize((new_width, new_height), Image.LANCZOS)

    # Crop the image to the target size
    left = (new_width - target_size[0]) / 2
    top = (new_height - target_size[1]) / 2
    right = (new_width + target_size[0]) / 2
    bottom = (new_height + target_size[1]) / 2
    return image.crop((left, top, right, bottom))

def create_mockup(app_screen, mockup_image, screen_size, screen_coords, mockup_size):
    """Create a mockup by combining the app screen with the mockup image."""
    app_screen_resized = resize_and_crop(app_screen, screen_size)
    result_mockup = Image.new('RGBA', mockup_size, (255, 255, 255, 0))
    result_mockup.paste(app_screen_resized, screen_coords)
    result_mockup.paste(mockup_image, (0, 0), mockup_image)
    return result_mockup

def create_zip_from_mockups(uploaded_files, mockup_image, screen_size, screen_coords, mockup_size):
    """Create a ZIP file containing all the mockups."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for uploaded_file in uploaded_files:
            app_screen = Image.open(uploaded_file)
            result_mockup = create_mockup(app_screen, mockup_image, screen_size, screen_coords, mockup_size)
            buf = io.BytesIO()
            result_mockup.save(buf, format="PNG")
            zip_file.writestr(f"mockup_{uploaded_file.name}.png", buf.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

def main():
    # Mockup用スマートフォン画像の読み込み
    mockup_image_path = 'assets/mockup.png'
    mockup_image = load_mockup_image(mockup_image_path)

    # モックアップ画像および画面の設定
    mockup_size = (864, 1728)
    screen_size = (750, 1624)
    screen_coords = (57, 51)  # 左上原点としての座標 (x, y)

    # Streamlitアプリ
    st.title('Mockup Generator')

    uploaded_files = st.file_uploader("アプリ画面画像をドラッグアンドドロップしてください", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        zip_buffer = create_zip_from_mockups(uploaded_files, mockup_image, screen_size, screen_coords, mockup_size)
        st.download_button(
            label="Download All Mockups as ZIP",
            data=zip_buffer,
            file_name="mockups.zip",
            mime="application/zip"
        )

if __name__ == "__main__":
    main()