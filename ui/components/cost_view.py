import streamlit as st
import pandas as pd


def render_cost_view(state: dict):
    st.subheader("💰 Token Usage & Estimated Cost Estimator")
    
    token_entries = state.get("token_usage", [])
    if not token_entries:
        st.info("No token usage tracked yet.")
        return

    df = pd.DataFrame(token_entries)
    
    total_prompt = df["prompt_tokens"].sum() if "prompt_tokens" in df.columns else 0
    total_completion = df["completion_tokens"].sum() if "completion_tokens" in df.columns else 0
    total_tokens = total_prompt + total_completion
    total_cost = df["cost_usd"].sum() if "cost_usd" in df.columns else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Prompt Tokens", f"{total_prompt:,}")
    c2.metric("Total Completion Tokens", f"{total_completion:,}")
    c3.metric("Total Combined Tokens", f"{total_tokens:,}")
    c4.metric("Estimated Total Cost (USD)", f"${total_cost:.5f}")

    st.divider()
    st.markdown("#### Token Breakdown per Specialist Agent")
    st.dataframe(df, use_container_width=True)

    api_calls = int(df["api_used"].sum()) if "api_used" in df.columns else 0
    fallback_calls = int((df["provider"] == "heuristic_fallback").sum()) if "provider" in df.columns else 0
    st.caption(f"Groq API-backed reviews: {api_calls}. Local fallback reviews: {fallback_calls}.")
