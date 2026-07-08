"""Data Quality page."""

from __future__ import annotations

import streamlit as st

from src.services.summary_service import PipelineResult


def render(pipeline: PipelineResult) -> None:
    st.markdown("### Data Quality")
    st.caption("Validation results and data integrity checks for the loaded inventory dataset.")

    validation = pipeline.validation

    if validation.is_valid:
        st.success("Dataset passed required validation checks.")
    else:
        st.error("Dataset failed one or more required validation checks.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Errors")
        if validation.errors:
            for err in validation.errors:
                st.error(err)
        else:
            st.info("No validation errors.")

    with col2:
        st.markdown("#### Warnings")
        if validation.warnings:
            for warn in validation.warnings:
                st.warning(warn)
        else:
            st.info("No validation warnings.")

    st.markdown("#### Dataset Profile")
    st.metric("Total Rows", f"{len(pipeline.normalized_df):,}")
    st.metric("Unique SKUs", f"{pipeline.normalized_df['sku'].nunique():,}")
    st.metric("Unique Locations", f"{pipeline.normalized_df['location'].nunique():,}")

    with st.expander("Column Summary"):
        st.dataframe(pipeline.normalized_df.describe(include="all").T, use_container_width=True)

    with st.expander("Sample Records"):
        st.dataframe(pipeline.normalized_df.head(20), use_container_width=True, hide_index=True)
