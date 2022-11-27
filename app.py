import streamlit as st
from Page import Page
from urllib.parse import urlparse
from validators import url as is_url
from matplotlib import pyplot as plt
import pandas as pd

st.set_page_config(page_title="Page Analyzer")
st.title("Page Analyzer")

# Get any query parameters, and set the input URL if present
query_params = st.experimental_get_query_params()
param_url: str = None
for key, value in query_params.items():
    if "url" in key:
        param_url = value[0]

input_url = st.text_input(
    "Enter the URL of a page to analyze",
    value=param_url if param_url else ""
)

# Validate the URL
if input_url and is_url(input_url):
    # Set the URL as a query parameter
    st.experimental_set_query_params(url=input_url)

    # Parse the URL
    parsed_url = urlparse(input_url)

    # Extract the properties of the parsed URL
    domain = parsed_url.hostname
    path = parsed_url.path
    protocol = parsed_url.scheme

    page = Page(input_url)

    st.markdown(f"#### [Visit Page]({input_url})")

    # Display the page's metadata
    st.markdown("## Page Metadata")
    metadata = page.get_metadata()
    st.markdown(f"""
    - Title Tag: `{metadata.get("title_tag")}`
    - Meta Description: `{metadata.get("meta_description")}`
    - H1: `{metadata.get("h1")}`
    """)

    # Display the page's h2s
    st.markdown("## Page Headings")
    heading_types = st.multiselect(
        "Select heading levels to include",
        options=["h1", "h2", "h3", "h4", "h5", "h6"],
        default=["h2"]
    )

    headings_by_level = page.get_headings(heading_types)
    # Display a bullet list of the page's h2s
    num_expanders = 0
    for level in sorted(list(headings_by_level.keys())):
        num_expanders += 1

        with st.expander(f"{level.upper()}s", expanded=num_expanders == 1):
            st.markdown("\n".join(list(map(
                lambda heading: f"- {heading}",
                headings_by_level[level]
            ))))

    st.markdown("## Schema Markup")
    # Display the page's schema markup
    schema_tags = page.get_schema_tags()

    for tag in schema_tags:
        tag_id = tag.get("id")
        schema_obj = page.get_schema_object_from_tag(tag)
        with st.expander(f"{schema_obj.get('@type')} (tag id: {tag_id})"):
            st.json(schema_obj)

    st.markdown("## Word Cloud")
    # Display a word cloud of the page's text
    wordcloud = page.get_wordcloud()
    fig = plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(fig)

    st.markdown("## Entities")
    # Get a the list of the H2s on the page
    h2s = headings_by_level.get("h2")

    # Create a list of entities by their salience
    concatenated_paragraphs = page.get_concatenated_paragraphs()
    entities = page.get_entities(concatenated_paragraphs)
    entity_freqs = {}
    for entity in entities:
        entity = entity.text.strip()
        if entity in entity_freqs:
            entity_freqs[entity] += 1
        else:
            entity_freqs[entity] = 1

    # Display the entities in a table
    st.markdown("### Entities by Frequency")
    df = pd.DataFrame.from_dict(
        entity_freqs,
        orient="index",
        columns=["Frequency"]
    ).sort_values(by="Frequency", ascending=False)
    st.dataframe(df)

elif input_url and not is_url(input_url):
    st.warning("Please enter a valid URL")
