"""Backward-compatible entry point for `streamlit run app.py`.

The canonical entry file is streamlit_app.py (renamed to avoid Vercel Python detection).
This shim is excluded from Vercel deploys via .vercelignore.
"""

from streamlit_app import main

if __name__ == "__main__":
    main()
