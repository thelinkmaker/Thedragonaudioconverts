import os
import streamlit as st

MONETAG_META = '<meta name="monetag" content="d80d3c02aee02551207039c9200f3f6a">'

# Add ONE <script> line here per format you actually want live.
# Get each exact tag from that format's "Get tag" button in the Monetag dashboard —
# do NOT reuse the same data-zone for two different formats.
MONETAG_SCRIPTS = [
    '<script src="https://quge5.com/88/tag.min.js" data-zone="282833" async data-cfasync="false"></script>',
    # '<script src="..." data-zone="..." ...></script>',  # add more here
]

SW_CONTENT = '''self.options = {
    "domain": "3nbf4.com",
    "zoneId": 11835715
}
self.lary = ""
importScripts('https://3nbf4.com/act/files/service-worker.min.js?r=sw')
'''

def get_static_dir():
    st_dir = os.path.dirname(st.__file__)
    return os.path.join(st_dir, "static")

def inject_head_tags():
    static_dir = get_static_dir()
    index_path = os.path.join(static_dir, "index.html")

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    tags_block = "\n    ".join([MONETAG_META] + MONETAG_SCRIPTS)

    if MONETAG_META not in html:
        html = html.replace("<head>", f"<head>\n    {tags_block}", 1)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Monetag tags injected")
    else:
        print("ℹ️ Monetag tags already present")

def inject_service_worker():
    static_dir = get_static_dir()
    sw_path = os.path.join(static_dir, "sw.js")
    with open(sw_path, "w", encoding="utf-8") as f:
        f.write(SW_CONTENT)
    print("✅ sw.js placed at static root (Luminous / 3nbf4.com)")

if __name__ == "__main__":
    inject_head_tags()
    inject_service_worker()
