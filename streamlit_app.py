#!/usr/bin/env python3
"""
GrokOSINT Streamlit Web UI
Run: streamlit run streamlit_app.py
"""

import asyncio
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from grok_osint.modules.email_osint import EmailOSINT
from grok_osint.modules.phone_osint import PhoneOSINT
from grok_osint.core.reporter import Reporter
from grok_osint import __version__

st.set_page_config(
    page_title="GrokOSINT",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"## 🛡️ GrokOSINT v{__version__}")
    st.markdown("**Ethical OSINT Tool**")
    st.markdown("---")
    st.markdown("### ⚠️ Ethical Warning")
    st.warning(
        "Only use on accounts/numbers you own or have **explicit authorization** for.\n\n"
        "Stalking, doxxing, harassment = **ILLEGAL**."
    )
    st.markdown("---")
    st.markdown("### Options")
    export_pdf = st.checkbox("Generate PDF Report", value=True)
    deep_scan = st.checkbox("Deep Scan (Holehe/Ignorant if installed)", value=True)
    region = st.selectbox("Phone Default Region", ["BD", "IN", "US", "GB", "PK", "NP"], index=0)
    st.markdown("---")
    st.markdown("GitHub: [sayan9168/GrokOSINT](https://github.com/sayan9168/GrokOSINT)")

st.markdown('<p class="main-header">🛡️ GrokOSINT</p>', unsafe_allow_html=True)
st.markdown("**Advanced Ethical Email + Phone OSINT** — Public data only")

tab1, tab2, tab3 = st.tabs(["📧 Email OSINT", "📱 Phone OSINT", "🔗 Full Scan"])

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

with tab1:
    st.subheader("Email Intelligence")
    email_input = st.text_input("Email Address", placeholder="someone@gmail.com", key="email")
    if st.button("🔍 Analyze Email", key="btn_email", type="primary"):
        if not email_input or "@" not in email_input:
            st.error("Please enter a valid email address")
        else:
            with st.spinner("Running advanced Email OSINT..."):
                osint = EmailOSINT(deep=deep_scan)
                result = run_async(osint.run_async(email_input))

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Valid", "Yes ✓" if result.validation.is_valid else "No")
            c2.metric("Gmail", "Yes" if result.validation.is_gmail else "No")
            c3.metric("Has MX", "Yes" if result.has_mx else "No")
            c4.metric("Disposable", "Yes ⚠" if result.validation.is_disposable else "No")

            if result.gravatar.get("has_gravatar"):
                st.success("Gravatar profile found!")
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    if result.gravatar.get("avatar_url"):
                        st.image(result.gravatar["avatar_url"], width=120)
                with col_b:
                    profile = result.gravatar.get("profile", {})
                    if profile.get("display_name"):
                        st.write(f"**Name:** {profile['display_name']}")
                    if profile.get("location"):
                        st.write(f"**Location:** {profile['location']}")
                    if result.gravatar.get("profile_url"):
                        st.markdown(f"[View Gravatar]({result.gravatar['profile_url']})")

            if result.username_guesses:
                st.markdown("#### 👤 Username Guesses")
                st.code(" | ".join(result.username_guesses))

            if result.account_checks:
                st.markdown("#### 🔎 Account Existence")
                for a in result.account_checks:
                    if a.get("found"):
                        st.success(f"**{a['name']}** — FOUND {a.get('details', '')}")
                    else:
                        st.info(f"**{a['name']}** — not found")

            if getattr(result, "holehe_results", None):
                st.markdown("#### 🕵️ Holehe Results")
                for h in result.holehe_results:
                    st.write(f"- {h}")

            if result.paste_hits:
                st.markdown("#### 📋 Public Paste Mentions")
                for p in result.paste_hits:
                    st.write(f"- [{p.get('source')}]({p.get('url')}) — {p.get('date')}")

            if result.social_profiles:
                st.markdown("#### 🔗 Quick Links")
                cols = st.columns(3)
                for i, s in enumerate(result.social_profiles):
                    cols[i % 3].markdown(f"[{s['platform']}]({s['url']})")

            if result.dorks:
                with st.expander("🔍 Google Dorks"):
                    for d in result.dorks:
                        st.code(d["query"], language=None)
                        st.caption(d["name"])

            if result.notes:
                st.markdown("#### Notes")
                for n in result.notes:
                    st.write(f"• {n}")

            reporter = Reporter("reports")
            data = reporter.to_dict(email_result=result)
            reporter.save_json(data, "email_web")
            reporter.save_markdown(data, "email_web")
            if export_pdf:
                reporter.save_pdf(data, "email_web")
                st.success("Reports saved in `reports/` (JSON, MD, PDF)")

with tab2:
    st.subheader("Phone Intelligence")
    phone_input = st.text_input("Phone Number", placeholder="+8801712345678", key="phone")
    if st.button("🔍 Analyze Phone", key="btn_phone", type="primary"):
        if not phone_input:
            st.error("Please enter a phone number")
        else:
            with st.spinner("Running advanced Phone OSINT..."):
                osint = PhoneOSINT(default_region=region, deep=deep_scan)
                result = run_async(osint.run_async(phone_input, region=region))

            v = result.validation
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Valid", "Yes ✓" if v.is_valid else ("Possible" if v.is_possible else "No"))
            c2.metric("Country", v.country_name or "-")
            c3.metric("Carrier", v.carrier_name or "Unknown")
            c4.metric("Type", v.number_type or "-")

            st.markdown("#### Formats")
            st.json(result.formats)

            if result.possible_apps:
                st.markdown("#### 📲 Possible Linked Apps")
                st.write(", ".join(result.possible_apps))

            if getattr(result, "ignorant_results", None):
                st.markdown("#### 🕵️ Ignorant Results")
                for r in result.ignorant_results:
                    st.write(f"- {r}")

            if result.social_links:
                st.markdown("#### 🔗 Quick Links")
                cols = st.columns(3)
                for i, s in enumerate(result.social_links):
                    cols[i % 3].markdown(f"[{s['name']}]({s['url']})")

            if result.dorks:
                with st.expander("🔍 Google Dorks"):
                    for d in result.dorks:
                        st.code(d["query"], language=None)

            if result.notes:
                st.markdown("#### Notes")
                for n in result.notes:
                    st.write(f"• {n}")

            reporter = Reporter("reports")
            data = reporter.to_dict(phone_result=result)
            reporter.save_json(data, "phone_web")
            reporter.save_markdown(data, "phone_web")
            if export_pdf:
                reporter.save_pdf(data, "phone_web")
                st.success("Reports saved in `reports/`")

with tab3:
    st.subheader("Full Combined Scan")
    col1, col2 = st.columns(2)
    with col1:
        full_email = st.text_input("Email", placeholder="someone@gmail.com", key="full_email")
    with col2:
        full_phone = st.text_input("Phone", placeholder="+8801712345678", key="full_phone")

    if st.button("🚀 Run Full Scan", type="primary"):
        if not full_email and not full_phone:
            st.error("Provide at least one of email or phone")
        else:
            email_result = None
            phone_result = None

            if full_email:
                with st.spinner("Email module..."):
                    eosint = EmailOSINT(deep=deep_scan)
                    email_result = run_async(eosint.run_async(full_email))
                    st.success(f"Email done: {full_email}")

            if full_phone:
                with st.spinner("Phone module..."):
                    posint = PhoneOSINT(default_region=region, deep=deep_scan)
                    phone_result = run_async(posint.run_async(full_phone, region=region))
                    st.success(f"Phone done: {full_phone}")

            reporter = Reporter("reports")
            data = reporter.to_dict(email_result=email_result, phone_result=phone_result)
            reporter.save_json(data, "full_web")
            reporter.save_markdown(data, "full_web")
            if export_pdf:
                reporter.save_pdf(data, "full_web")
                st.success("Full report generated (JSON + Markdown + PDF)")
                st.balloons()

st.markdown("---")
st.caption("GrokOSINT • Public data only • Use ethically • https://github.com/sayan9168/GrokOSINT")
