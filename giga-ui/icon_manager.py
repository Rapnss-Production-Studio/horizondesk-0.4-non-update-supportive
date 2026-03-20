
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os
from pathlib import Path
import math

ICONS_DIR = Path(__file__).parent / 'icons'
ICONS_DIR.mkdir(exist_ok=True)

def adjust_color(color, factor):
    r, g, b = color
    return (
        max(0, min(255, int(r * factor))),
        max(0, min(255, int(g * factor))),
        max(0, min(255, int(b * factor)))
    )

def draw_smooth_curve(draw, points, fill, width=0):
    if len(points) < 2: return
    draw.polygon(points, fill=fill)

def create_gradient_image(size, color1, color2, direction='vertical'):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    for y in range(size[1]):
        ratio = y / size[1] if direction == 'vertical' else 0
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        a = int(color1[3] + (color2[3] - color1[3]) * ratio) if len(color1) > 3 else 255
        for x in range(size[0]):
            img.putpixel((x, y), (r, g, b, a))
    return img

def create_folder_icon(primary_color=None):
    """
    Create premium curved folder icon - 512x512
    Smooth curves, gradient, professional look
    """
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Palette
    base = primary_color or (139, 92, 246) # Violet default
    
    back_color = adjust_color(base, 0.7)
    front_top = base
    front_bottom = adjust_color(base, 0.85)
    tab_color = adjust_color(base, 0.9)
    highlight = (255, 255, 255)
    
    # ===== BACK FOLDER LAYER =====
    back_points = [
        (0, 100), (0, 480), (20, 500), (40, 512), (472, 512), 
        (492, 500), (512, 480), (512, 100), (280, 100), 
        (240, 60), (200, 40), (40, 40), (20, 50), (0, 70),
    ]
    draw.polygon(back_points, fill=(*back_color, 200))
    
    # ===== TAB (top left) =====
    draw.rounded_rectangle([0, 30, 220, 110], radius=40, fill=(*tab_color, 240))
    
    # ===== FRONT FOLDER (main body) =====
    front_gradient = create_gradient_image((size, size - 80), (*front_top, 255), (*front_bottom, 255))
    
    front_mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(front_mask)
    mask_draw.rounded_rectangle([0, 80, 512, 512], radius=50, fill=255)
    
    img.paste(front_gradient, (0, 80), front_mask.crop((0, 80, 512, 512)))
    draw = ImageDraw.Draw(img)
    
    # ===== GLOSSY HIGHLIGHT (top) =====
    highlight_mask = Image.new('L', (size, 80), 0)
    h_draw = ImageDraw.Draw(highlight_mask)
    h_draw.rounded_rectangle([0, 0, 512, 80], radius=50, fill=255)
    
    highlight_layer = Image.new('RGBA', (size, 80), (*highlight, 60))
    img.paste(Image.alpha_composite(Image.new('RGBA', (size, 80), (0, 0, 0, 0)), highlight_layer), (0, 80), highlight_mask)
    draw = ImageDraw.Draw(img)
    
    # ===== INNER CONTENT PREVIEW =====
    content_y = 180
    content_spacing = 60
    for i in range(5):
        alpha = 100 - i * 15
        width_reduction = i * 30
        draw.rounded_rectangle(
            [50, content_y + i * content_spacing, 462 - width_reduction, content_y + i * content_spacing + 28],
            radius=14,
            fill=(255, 255, 255, alpha)
        )
    
    # ===== SUBTLE GLOW EFFECT =====
    glow = img.filter(ImageFilter.GaussianBlur(3))
    enhancer = ImageEnhance.Brightness(glow)
    glow = enhancer.enhance(1.2)
    
    # ===== SAVE =====
    ico_path = ICONS_DIR / 'folder.ico'
    sizes_list = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256), (512, 512)]
    icons = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes_list]
    icons[0].save(ico_path, format='ICO', sizes=sizes_list, append_images=icons[1:])
    
    png_path = ICONS_DIR / 'folder_512.png'
    img.save(png_path, format='PNG')
    return ico_path

def create_file_icon(primary_color=None):
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    base = primary_color or (167, 139, 250)
    main_top = base
    main_bottom = adjust_color(base, 0.8)
    
    gradient = create_gradient_image((size, size), (*main_top, 255), (*main_bottom, 255))
    
    body_mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(body_mask)
    mask_draw.rounded_rectangle([0, 0, 512, 512], radius=50, fill=255)
    
    img.paste(gradient, (0, 0), body_mask)
    draw = ImageDraw.Draw(img)
    
    fold_size = 120
    fold_points = [(size - fold_size, 0), (size, fold_size), (size - fold_size, fold_size)]
    draw.polygon(fold_points, fill=(255, 255, 255, 140))
    
    draw.arc([size - fold_size - 20, -20, size + 20, fold_size + 20], start=90, end=180, fill=(255, 255, 255, 80), width=4)
    
    line_y = 160
    for i in range(6):
        alpha = 180 - i * 25
        width = 400 - i * 40
        draw.rounded_rectangle(
            [56, line_y + i * 55, 56 + width, line_y + i * 55 + 26],
            radius=13,
            fill=(255, 255, 255, alpha)
        )
    
    ico_path = ICONS_DIR / 'file.ico'
    sizes_list = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256), (512, 512)]
    icons = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes_list]
    icons[0].save(ico_path, format='ICO', sizes=sizes_list, append_images=icons[1:])
    return ico_path

def apply_folder_icon(folder_path, icon_path):
    import ctypes
    folder_path = Path(folder_path)
    icon_path = Path(icon_path).absolute()
    if not folder_path.is_dir(): return False
    
    desktop_ini = folder_path / "desktop.ini"
    content = f"[.ShellClassInfo]\nIconResource={icon_path},0\n"
    
    try:
        if desktop_ini.exists():
            os.system(f'attrib -h -s "{desktop_ini}" 2>nul')
            desktop_ini.unlink()
        
        os.system(f'attrib +s "{folder_path}"')
        with open(desktop_ini, 'w') as f:
            f.write(content)
        os.system(f'attrib +h +s "{desktop_ini}"')
        ctypes.windll.shell32.SHChangeNotify(0x8000000, 0x1000, None, None)
        return True
    except: return False

def apply_to_all_desktop_folders():
    desktop = Path.home() / "Desktop"
    ico_path = ICONS_DIR / "folder.ico"
    import ctypes
    for item in desktop.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            apply_folder_icon(item, ico_path)
    ctypes.windll.shell32.SHChangeNotify(0x8000000, 0x1000, None, None)

def restore_default_icons():
    import ctypes
    desktop = Path.home() / "Desktop"
    for folder in desktop.iterdir():
        if folder.is_dir():
            ini = folder / "desktop.ini"
            if ini.exists():
                try:
                    os.system(f'attrib -h -s "{ini}" 2>nul')
                    ini.unlink()
                    os.system(f'attrib -s "{folder}"')
                except: pass
    ctypes.windll.shell32.SHChangeNotify(0x8000000, 0x1000, None, None)

def generate_themed_icons(color):
    create_folder_icon(color)
    create_file_icon(color)
    print(f"✓ Themed icons generated for color: {color}")


# ═══════════════════════════════════════════════════════
#   ICON DESIGN STUDIO — Template Functions
# ═══════════════════════════════════════════════════════

TEMPLATES = ['gradient', 'flat', 'neon', 'pastel', 'metallic', 'glass']

def create_icon_from_template(template_name, primary_color=None):
    """Create a folder icon using the specified template style"""
    fn = {
        'gradient': create_folder_icon,
        'flat': _create_flat_icon,
        'neon': _create_neon_icon,
        'pastel': _create_pastel_icon,
        'metallic': _create_metallic_icon,
        'glass': _create_glass_icon,
    }.get(template_name, create_folder_icon)
    return fn(primary_color)


def _create_flat_icon(primary_color=None):
    """Flat minimal folder icon — solid color, no gradient"""
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    base = primary_color or (99, 102, 241)

    # Simple rounded rectangle body
    draw.rounded_rectangle([0, 80, 512, 512], radius=40, fill=(*base, 255))
    # Tab
    draw.rounded_rectangle([0, 30, 200, 110], radius=30, fill=(*base, 255))
    # White content lines
    for i in range(4):
        alpha = 200 - i * 30
        draw.rounded_rectangle(
            [50, 180 + i * 70, 420 - i * 30, 210 + i * 70],
            radius=10, fill=(255, 255, 255, alpha)
        )

    return _save_icon(img, 'flat_folder')


def _create_neon_icon(primary_color=None):
    """Neon glow folder icon — dark body with glowing edges"""
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    base = primary_color or (0, 255, 136)

    dark = (20, 20, 30)
    # Dark body
    draw.rounded_rectangle([0, 80, 512, 512], radius=45, fill=(*dark, 240))
    draw.rounded_rectangle([0, 30, 210, 110], radius=30, fill=(*dark, 240))

    # Neon border
    draw.rounded_rectangle([0, 80, 512, 512], radius=45, outline=(*base, 255), width=4)
    draw.rounded_rectangle([0, 30, 210, 110], radius=30, outline=(*base, 255), width=3)

    # Glow lines inside
    for i in range(3):
        draw.rounded_rectangle(
            [60, 200 + i * 80, 400, 230 + i * 80],
            radius=8, fill=(*base, 60 + i * 20)
        )

    # Blur for glow effect
    glow = img.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(glow, img)

    return _save_icon(img, 'neon_folder')


def _create_pastel_icon(primary_color=None):
    """Soft pastel folder icon — light, airy colors"""
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    base = primary_color or (167, 139, 250)

    pastel = (
        min(255, base[0] + 60),
        min(255, base[1] + 60),
        min(255, base[2] + 60)
    )
    pastel_light = (
        min(255, base[0] + 90),
        min(255, base[1] + 90),
        min(255, base[2] + 90)
    )

    draw.rounded_rectangle([0, 80, 512, 512], radius=50, fill=(*pastel, 220))
    draw.rounded_rectangle([0, 30, 220, 110], radius=35, fill=(*pastel_light, 220))

    # Soft white highlights
    draw.rounded_rectangle([20, 100, 492, 160], radius=20, fill=(255, 255, 255, 80))
    for i in range(4):
        draw.rounded_rectangle(
            [60, 200 + i * 65, 380, 228 + i * 65],
            radius=12, fill=(255, 255, 255, 120 - i * 20)
        )

    return _save_icon(img, 'pastel_folder')


def _create_metallic_icon(primary_color=None):
    """Metallic folder icon — shiny gradient with reflections"""
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    base = primary_color or (120, 120, 140)

    dark = adjust_color(base, 0.5)
    light = adjust_color(base, 1.4)
    mid = base

    # Gradient body via strips
    for y in range(80, 512):
        ratio = (y - 80) / 432
        r = int(light[0] + (dark[0] - light[0]) * ratio)
        g = int(light[1] + (dark[1] - light[1]) * ratio)
        b = int(light[2] + (dark[2] - light[2]) * ratio)
        draw.line([(0, y), (512, y)], fill=(r, g, b, 250))

    # Mask to rounded rect
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 80, 512, 512], radius=40, fill=255)
    mask_draw.rounded_rectangle([0, 30, 200, 110], radius=25, fill=255)

    result = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    result.paste(img, mask=mask)

    draw2 = ImageDraw.Draw(result)
    # Highlight streak
    draw2.rounded_rectangle([30, 100, 482, 140], radius=15, fill=(255, 255, 255, 60))
    # Content lines
    for i in range(3):
        draw2.rounded_rectangle(
            [60, 220 + i * 80, 420, 250 + i * 80],
            radius=10, fill=(255, 255, 255, 80)
        )

    return _save_icon(result, 'metallic_folder')


def _create_glass_icon(primary_color=None):
    """Glassmorphism folder icon — frosted glass look"""
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    base = primary_color or (99, 102, 241)

    # Semi-transparent body
    draw.rounded_rectangle([0, 80, 512, 512], radius=50, fill=(*base, 100))
    draw.rounded_rectangle([0, 30, 220, 110], radius=35, fill=(*base, 120))

    # White border
    draw.rounded_rectangle([0, 80, 512, 512], radius=50, outline=(255, 255, 255, 80), width=2)

    # Inner glass highlight
    draw.rounded_rectangle([10, 90, 502, 200], radius=40, fill=(255, 255, 255, 50))

    # Content lines behind the glass
    for i in range(5):
        draw.rounded_rectangle(
            [50, 220 + i * 55, 460 - i * 30, 248 + i * 55],
            radius=12, fill=(255, 255, 255, 60 + i * 10)
        )

    # Blur for frosted effect
    blurred = img.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(blurred, img)

    return _save_icon(img, 'glass_folder')


def _save_icon(img, name):
    """Save PIL image as .ico and .png"""
    ico_path = ICONS_DIR / f'{name}.ico'
    png_path = ICONS_DIR / f'{name}_512.png'
    sizes_list = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes_list]
    icons[0].save(ico_path, format='ICO', sizes=sizes_list, append_images=icons[1:])
    img.save(png_path, format='PNG')
    return ico_path


def get_template_preview(template_name, primary_color=None, size=128):
    """Generate a preview image for a template at given size"""
    ico = create_icon_from_template(template_name, primary_color)
    # Return the full-size PNG path for preview
    png_name = ico.stem + '_512.png'
    png_path = ICONS_DIR / png_name
    if not png_path.exists():
        png_path = ICONS_DIR / 'folder_512.png'
    return png_path


if __name__ == '__main__':
    generate_themed_icons(None)
