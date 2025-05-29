import streamlit as st
import pandas as pd
from scraper import scrape_headlines, save_to_csv

st.set_page_config(page_title="Web Scraper", layout="centered")

st.title("📰 News Headline Scraper")
st.write("Scrapes latest headlines from [Hacker News](https://news.ycombinator.com)")

if st.button("Scrape Headlines"):
    try:
        with st.spinner("Scraping..."):
            headlines = scrape_headlines()
        st.success(f"Scraped {len(headlines)} headlines!")

        # Convert data to a DataFrame for display
        df = pd.DataFrame(headlines, columns=["Title", "Link"])

        # Display results in a table with clickable links
        def make_clickable(link):
            return f'<a href="{link}" target="_blank">Link</a>'

        df["Link"] = df["Link"].apply(make_clickable)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

        # Save to CSV
        filename = save_to_csv(headlines)
        with open(filename, 'rb') as f:
            st.download_button("📥 Download CSV", f, file_name=filename, mime='text/csv')

    except Exception as e:
        st.error(f"An error occurred: {e}")
