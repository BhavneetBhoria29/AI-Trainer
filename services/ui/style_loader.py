import os
import streamlit as st
import base64
import streamlit.components.v1 as components


def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:     
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def inject_local_font(font_path,font_name):
    if not os.path.exists(font_path):
        return
    

    with open(font_path, "rb") as f:
        encoded=base64.b64encode(f.read()).decode()

    ext=os.path.splitext(font_path)[1].lstrip(".")
    fmt={"otf":"opentype","ttf":"truetype"}.get(ext,ext)
    mime={"otf":"font/otf"}.get(ext,f"font/{ext}")


    st.markdown(f"""
                
        <style>
            @font-face {{
                font-family: '{font_name}';
                src: url("data:{mime};base64,{encoded}") format("{fmt}");
                font-weight: 100 900;
                font-style: normal;
            }}
        </style>
    """, unsafe_allow_html=True)


def inject_webrtc_styles():
    font_path = os.path.join(os.getcwd(), "static", "AdobeClean.otf")

    if not os.path.exists(font_path):
        return

    with open(font_path, "rb") as font_file:
        encoded_font = base64.b64encode(font_file.read()).decode()

    components.html(
        f"""
        <script>
        (function patchWebRTCStyles() {{
            function injectIntoIframe(iframe) {{
                try {{
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    if (!doc || !doc.head) {{
                        return;
                    }}

                    if (doc.head.querySelector("#webrtc-custom-styles")) return;

                    const style = document.createElement("style");
                    style.id = "webrtc-custom-styles";
                    style.textContent = `
                        @font-face {{
                            font-family: 'Adobe Clean';
                            src: url("data:font/otf;base64,{encoded_font}") format("opentype");
                            font-weight: 100 900;
                            font-style: normal;
                        }}
                        .MuiButtonBase-root,
                        .MuiButton-root,
                        .MuiButton-contained,
                        .MuiButton-text {{
                            border-radius: 0px !important;
                            font-family: 'Adobe Clean', sans-serif !important;
                        }}
                    `;
                    doc.head.appendChild(style);
                }} catch (e) {{
                    console.error("Failed to inject styles into iframe:", e);
                }}
            }}

            function findAndPatch() {{
                const parentDoc = window.parent.document;
                const iframes = parentDoc.querySelectorAll("iframe");
                iframes.forEach(iframe => {{
                    if (iframe.src && iframe.src.includes('webrtc')) {{
                        if (!iframe.contentDocument || !iframe.contentDocument.head) {{
                            iframe.addEventListener("load", () => injectIntoIframe(iframe));
                        }} else {{
                            injectIntoIframe(iframe);
                        }}
                    }}
                }});
            }}

            findAndPatch();
        }})();
        </script>
        """,
        height=0
    )