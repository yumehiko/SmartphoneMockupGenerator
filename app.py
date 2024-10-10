import streamlit as st
from PIL import Image, ImageOps
import io
import zipfile
from typing import Tuple, List

# 定数の定義
MOCKUP_IMAGE_PATH = 'assets/mockup.png'
MOCKUP_SIZE = (864, 1728)
SCREEN_SIZE = (750, 1624)
SCREEN_COORDS = (57, 51)  # 左上原点としての座標 (x, y)

def load_mockup_image(path: str) -> Image.Image:
    """Load the mockup image."""
    try:
        return Image.open(path)
    except FileNotFoundError:
        st.error(f"Mockup image not found at {path}")
        raise

def resize_and_crop(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
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

def create_mockup(app_screen: Image.Image, mockup_image: Image.Image, screen_size: Tuple[int, int], screen_coords: Tuple[int, int], mockup_size: Tuple[int, int]) -> Image.Image:
    """Create a mockup by combining the app screen with the mockup image."""
    app_screen_resized = resize_and_crop(app_screen, screen_size)
    result_mockup = Image.new('RGBA', mockup_size, (255, 255, 255, 0))
    result_mockup.paste(app_screen_resized, screen_coords)
    result_mockup.paste(mockup_image, (0, 0), mockup_image)
    return result_mockup

def create_zip_from_mockups(uploaded_files: List[io.BytesIO], mockup_image: Image.Image, screen_size: Tuple[int, int], screen_coords: Tuple[int, int], mockup_size: Tuple[int, int]) -> io.BytesIO:
    """Create a ZIP file containing all the mockups."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for uploaded_file in uploaded_files:
            try:
                app_screen = Image.open(uploaded_file)
                result_mockup = create_mockup(app_screen, mockup_image, screen_size, screen_coords, mockup_size)
                buf = io.BytesIO()
                result_mockup.save(buf, format="PNG")
                zip_file.writestr(f"mockup_{uploaded_file.name}.png", buf.getvalue())
            except Exception as e:
                st.error(f"Error processing file {uploaded_file.name}: {e}")
    zip_buffer.seek(0)
    return zip_buffer

def main() -> None:
    # Mockup用スマートフォン画像の読み込み
    mockup_image = load_mockup_image(MOCKUP_IMAGE_PATH)

    # Streamlitアプリ
    st.title('Mockup Generator')

    # ファイルアップロード
    uploaded_files = st.file_uploader("アプリ画面画像をドラッグアンドドロップしてください", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        if len(uploaded_files) == 1:
            # 1つのファイルのみの場合、そのまま画像を返す
            uploaded_file = uploaded_files[0]
            try:
                app_screen = Image.open(uploaded_file)
                result_mockup = create_mockup(app_screen, mockup_image, SCREEN_SIZE, SCREEN_COORDS, MOCKUP_SIZE)
                buf = io.BytesIO()
                result_mockup.save(buf, format="PNG")
                buf.seek(0)
                st.download_button(
                    label="💾 ダウンロード",
                    data=buf,
                    file_name=f"mockup_{uploaded_file.name}.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"Error processing file {uploaded_file.name}: {e}")
        else:
            # 複数のファイルの場合、ZIPファイルを返す
            zip_buffer = create_zip_from_mockups(uploaded_files, mockup_image, SCREEN_SIZE, SCREEN_COORDS, MOCKUP_SIZE)
            st.download_button(
                label="💾 ZIPでダウンロード",
                data=zip_buffer,
                file_name="mockups.zip",
                mime="application/zip"
            )

if __name__ == "__main__":
    main()