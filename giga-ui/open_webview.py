"""
Horizon Webview Launcher — Opens HTML apps in pywebview
Usage: python open_webview.py <html_path> <window_title> [width] [height]
"""
import sys
import os

def main():
    if len(sys.argv) < 3:
        print("Usage: python open_webview.py <html_path> <title> [width] [height]")
        sys.exit(1)

    html_path = sys.argv[1]
    title = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 800
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 560

    if not os.path.exists(html_path):
        print(f"File not found: {html_path}")
        sys.exit(1)

    import webview
    webview.create_window(
        title,
        url=html_path,
        width=width,
        height=height,
        resizable=True,
        min_size=(500, 400)
    )
    webview.start()

if __name__ == '__main__':
    main()
