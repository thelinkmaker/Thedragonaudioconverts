import os
import streamlit as st

def inject_meta_tag():
    meta_tag = '<meta name="monetag" content="d80d3c02aee02551207039c9200f3f6a">'
    st_dir = os.path.dirname(st.__file__)
    index_path = os.path.join(st_dir, "static", "index.html")

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    if "monetag" not in html:
        html = html.replace("<head>", f"<head>\n    {meta_tag}", 1)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Monetag meta tag injected.")
    else:
        print("ℹ️ Monetag tag already present.")

if __name__ == "__main__":
    inject_meta_tag()
