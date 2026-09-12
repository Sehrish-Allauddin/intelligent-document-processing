import streamlit as st


def render_sidebar():

    st.sidebar.title("📂 Navigation")

    page = st.sidebar.radio(

        "Select Module",

        [

            "🏠 Dashboard",

            "📄 Resume",

            "🧾 Invoice",

            "🧾 Receipt",

            "📋 Form",

            "📊 Analytics",

            "🗄 Database"

        ]

    )

    st.sidebar.markdown("---")

    st.sidebar.info(

        "Intelligent Document Processing\n\nVersion 1.0"

    )

    return page