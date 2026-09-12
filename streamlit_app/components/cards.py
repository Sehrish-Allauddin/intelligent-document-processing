import streamlit as st


def stat_card(title, value):

    st.metric(

        label=title,

        value=value

    )