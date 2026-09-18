import os
import streamlit as st

MONETAG_META = '<meta name="monetag" content="d80d3c02aee02551207039c9200f3f6a">'
MONETAG_SCRIPT = '<script src="https://quge5.com/88/tag.min.js" data-zone="282833" async data-cfasync="false"></script>'

SW_CONTENT = '''self.options = {
    "domain": "5gvci.com",
    "zoneId": 11835663
}
self.lary = ""
importScripts('https://5gvci.com/act/files/service-worker.min.js?r=sw')
'''

def get_static_dir():
    st_dir = os.path.dirname(st.__file__)
    return os.path.join(st_dir, "static")

def inject_head_tags():
    static_dir = get_static_dir()
    index_path = os.path.join(static_dir, "index.html")

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    if "monetag" not in html:
        html = html.replace("<head>", f"<head>\n    {MONETAG_META}\n    {MONETAG_SCRIPT}", 1)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Monetag meta + script injected")
    else:
        print("ℹ️ Monetag tags already present")

def inject_service_worker():
    static_dir = get_static_dir()
    sw_path = os.path.join(static_dir, "sw.js")
    with open(sw_path, "w", encoding="utf-8") as f:
        f.write(SW_CONTENT)
    print("✅ sw.js placed at static root")

if __name__ == "__main__":
    inject_head_tags()
    inject_service_worker()
