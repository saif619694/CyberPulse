import streamlit as st
import pandas as pd
import plotly.express as px
import html
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from app.frontend.utils.formatters import format_amount, format_date, get_round_color

def clean_html_text(text: str) -> str:
    """Clean and truncate HTML text efficiently"""
    if not text:
        return ""
    
    processed_text = str(text)
    for _ in range(3):
        processed_text = html.unescape(processed_text)
    
    soup = BeautifulSoup(processed_text, 'html.parser')
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    
    plain_text = soup.get_text()
    lines = (line.strip() for line in plain_text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    cleaned_text = ' '.join(chunk for chunk in chunks if chunk)
    cleaned_text = cleaned_text.strip()
    
    if len(cleaned_text) > 200:
        cleaned_text = cleaned_text[:197] + '...'
    return cleaned_text

def display_funding_card(company: Dict[str, Any]):
    """Display optimized funding card with enhanced styling"""
    
    company_name = clean_html_text(str(company.get('company_name', 'Unknown Company')))
    
    raw_round_data = company.get('round')
    round_name_raw_for_logic = "Unknown" if not raw_round_data else str(raw_round_data)
    round_name_display = clean_html_text(round_name_raw_for_logic)
    
    date_str = format_date(company.get('date', ''))
    company_type = clean_html_text(str(company.get('company_type', 'Unknown')))
    description = clean_html_text(str(company.get('description', '')))

    raw_source = company.get('source')
    source_display_text = clean_html_text(str(raw_source)) if raw_source else "ReturnonSecurity"

    amount_display = format_amount(company.get('amount', 0))

    investors_raw = company.get('investors', [])
    MAX_LINK_INVESTORS = 3
    linked_investors_data = []

    if isinstance(investors_raw, list):
        for inv_data in investors_raw[:MAX_LINK_INVESTORS]:
            investor_name = ''
            investor_url = ''
            if isinstance(inv_data, dict):
                investor_name = clean_html_text(str(inv_data.get('name', '')))
                investor_url_raw = str(inv_data.get('url', ''))
                if investor_url_raw and (investor_url_raw.startswith('http://') or investor_url_raw.startswith('https://')):
                    investor_url = investor_url_raw
            elif isinstance(inv_data, str):
                investor_name = clean_html_text(inv_data)
            if investor_name:
                linked_investors_data.append({'name': investor_name, 'url': investor_url})

    num_total_investors = len(investors_raw) if isinstance(investors_raw, list) else 0
    more_investors_count = num_total_investors - len(linked_investors_data)

    company_url = str(company.get('company_url', ''))
    story_link = str(company.get('story_link', ''))
    if not (company_url.startswith('http://') or company_url.startswith('https://')): 
        company_url = ''
    if not (story_link.startswith('http://') or story_link.startswith('https://')): 
        story_link = ''
    
    round_color_key = round_name_raw_for_logic if round_name_display and round_name_display.lower() != 'unknown' else "Unknown"
    round_color = get_round_color(round_color_key)

    try:
        card_container = st.container(border=True)
    except TypeError:
        card_container = st.container()

    with card_container:
        header_col1, header_col2 = st.columns([0.7, 0.3])
        with header_col1:
            st.subheader(company_name)
            
            if round_name_display and round_name_display.lower() != 'unknown':
                badge_html = f"""<span style="display: inline-block; padding: 0.2rem 0.5rem;
                                            background-color: {round_color}20; border: 1px solid {round_color}40;
                                            color: {round_color}; border-radius: 6px; font-size: 0.86rem;
                                            font-weight: 500; margin-top: -5px; margin-bottom: 10px;">
                                   {html.escape(round_name_display)}
                               </span>"""
                st.markdown(badge_html, unsafe_allow_html=True)
            else:
                st.markdown("<div style='height: 1px; margin-top: -5px; margin-bottom: 10px; visibility: hidden;'></div>", unsafe_allow_html=True)

        with header_col2:
            amount_font_size = "1.4rem" if amount_display != "Undisclosed" else "1.19rem"
            amount_color = "#10b981" if amount_display != "Undisclosed" else "gold"
            
            st.markdown(f"<div style='text-align: right;'>"
                        f"<p style='font-size: {amount_font_size}; font-weight: bold; color: {amount_color}; margin-bottom: -2px; line-height:1.2;'>{html.escape(amount_display)}</p>"
                        f"<p style='font-size: 0.75rem; color: #6b7280; margin-top: 0px;'>{html.escape(date_str)}</p>"
                        f"</div>", unsafe_allow_html=True)
        
        description_text = description if description else " "
        st.markdown(f"<p style='color: #9ca3af; font-size: 0.875rem; line-height: 1.6; min-height: 3.2em; max-height: 3.2em; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; margin-bottom: 0.75rem;'>{description_text}</p>", unsafe_allow_html=True)

        type_tag_html = f"""<span style='background-color: #262626; color: #a3a3a3; 
                                        padding: 0.25rem 0.5rem; border-radius: 4px; 
                                        border: 1px solid #4B5563;'>
                               Type: {html.escape(company_type if company_type else 'N/A')}
                           </span>"""
        st.markdown(f"<div style='display: flex; gap: 0.5rem; margin-bottom: 0.75rem; flex-wrap: wrap; font-size: 0.75rem; min-height: 1.8em;'>{type_tag_html}</div>", unsafe_allow_html=True)

        if num_total_investors > 0:
            investor_links_html = []
            link_style = "text-decoration: none; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.75rem; margin-right: 0.3rem; margin-bottom: 0.3rem; display: inline-block;"
            
            for inv in linked_investors_data:
                if inv['url']:
                    style = f"{link_style} color: #90cdf4; background-color: #2d3748; border: 1px solid #4a5568;"
                    investor_links_html.append(f"<a href='{html.escape(inv['url'])}' target='_blank' rel='noopener noreferrer' style='{style}'>{html.escape(inv['name'])}</a>")
                else:
                    style = f"{link_style} color: #a0aec0; background-color: #384252; border: 1px solid #4a5568; cursor: default;"
                    investor_links_html.append(f"<span style='{style}'>{html.escape(inv['name'])}</span>")
            
            investor_content = "".join(investor_links_html)
            if more_investors_count > 0:
                investor_content += f"<span style='font-size: 0.75rem; color: #a3a3a3; margin-left: 0.3rem; display: inline-block; vertical-align: middle; margin-bottom: 0.3rem;'>+{more_investors_count} more</span>"
            
            st.markdown(f"""
            <div style="margin-bottom: 0.5rem; min-height: 2.8em;">
                <strong style='font-size:0.8rem; color: #8a8a8a; margin-bottom: 0.25rem; display: block;'>Investors:</strong>
                <div style='line-height: 1.5;'>{investor_content}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='margin-bottom: 0.5rem; min-height: 2.8em;'> </div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='margin-bottom:1rem; min-height: 1.5em;'>
            <span style='font-size:0.75rem; color: #6b7280;'>Source: {html.escape(source_display_text)}</span>
        </div>""", unsafe_allow_html=True)
        
        button_cols = st.columns(2)
        button_style = ("text-decoration: none; display: block; width: 100%; text-align: center; "
                       "padding: 0.35rem 0.75rem; font-size: 0.875rem; border-radius: 0.375rem; "
                       "font-weight: 500; line-height: 1.25; ")

        enabled_style = f"{button_style}color: #FAFAFA; background-color: #31333F; border: 1px solid #31333F; cursor: pointer;"
        disabled_style = f"{button_style}color: rgba(250, 250, 250, 0.5); background-color: rgba(49, 51, 63, 0.4); border: 1px solid rgba(49, 51, 63, 0.4); cursor: not-allowed;"

        with button_cols[0]:
            if company_url:
                st.markdown(f'<a href="{html.escape(company_url)}" target="_blank" rel="noopener noreferrer" style="{enabled_style}">🔗 Website</a>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span style="{disabled_style}">🔗 Website</span>', unsafe_allow_html=True)

        with button_cols[1]:
            if story_link:
                st.markdown(f'<a href="{html.escape(story_link)}" target="_blank" rel="noopener noreferrer" style="{enabled_style}">📰 Story</a>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span style="{disabled_style}">📰 Story</span>', unsafe_allow_html=True)

def display_funding_cards(companies: List[Dict[str, Any]]):
    """Display funding cards in optimized grid layout"""
    if not companies:
        st.info("No funding data found. Try adjusting your search criteria.")
        return
    
    num_columns = 3 
    for i in range(0, len(companies), num_columns):
        cols = st.columns(num_columns)
        for j in range(num_columns):
            if i + j < len(companies):
                with cols[j]:
                    display_funding_card(companies[i + j])

def display_no_data_message():
    """Display professional no data message"""
    st.markdown("""
    <div style="background-color: #111111; border: 1px solid #333333; border-radius: 12px; 
                 padding: 3rem 2rem; text-align: center; margin: 2rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🤷‍♂️</div>
        <h3 style="color: #e0e0e0; font-size: 1.3rem; margin-bottom: 0.5rem;">No Funding Data Found</h3>
        <p style="color: #9e9e9e; font-size: 0.9rem;">Try adjusting your search criteria or check back later.</p>
    </div>
    """, unsafe_allow_html=True)

def display_funding_data(companies: List[Dict[str, Any]], view_mode: str = "cards"):
    """Display funding data in specified view mode"""
    if not companies and view_mode != "chart":
        display_no_data_message()
        return

    if view_mode == "cards":
        st.markdown("""
            <style>
            a[style*="cursor: pointer;"]:hover {
                filter: brightness(1.2);
            }
            div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] h3 {
                margin-bottom: 0.25rem !important; 
            }
            </style>
            """, unsafe_allow_html=True)
        display_funding_cards(companies)
    elif view_mode == "table":
        if not companies: 
            display_no_data_message()
            return
        display_table_view(companies)
    elif view_mode == "chart":
        display_chart_view(companies) 

def display_table_view(companies: List[Dict[str, Any]]):
    """Display optimized table view"""
    st.markdown("<h3 style='color: #8b5cf6; font-size: 1.5rem; margin-bottom: 1rem;'>📊 Funding Table</h3>", unsafe_allow_html=True)
    
    table_data = [{
        "Company": clean_html_text(str(c.get('company_name', 'Unknown'))),
        "Round": clean_html_text(str(c.get('round', 'Unknown'))),
        "Amount": format_amount(c.get('amount', 0)),
        "Type": clean_html_text(str(c.get('company_type', 'Unknown'))),
        "Date": format_date(c.get('date', '')),
        "Investors": len(c.get('investors', []) if isinstance(c.get('investors'), list) else []),
        "Source": clean_html_text(str(c.get('source', ''))) if c.get('source') and clean_html_text(str(c.get('source', ''))) else "ReturnonSecurity"
    } for c in companies]
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True, column_config={
        "Company": st.column_config.TextColumn("🏢 Company", width="large"),
        "Round": st.column_config.TextColumn("💼 Round"),
        "Amount": st.column_config.TextColumn("💰 Amount"),
        "Type": st.column_config.TextColumn("🏷️ Type", width="small"),
        "Date": st.column_config.TextColumn("📅 Date"),
        "Investors": st.column_config.NumberColumn("👥 Investors", width="small"),
        "Source": st.column_config.TextColumn("🌐 Source")
    }) 
    
    try:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download CSV", data=csv, file_name="funding_data.csv", mime="text/csv", use_container_width=True)
    except Exception as e: 
        st.error(f"Could not generate CSV: {e}")

def display_chart_view(companies: List[Dict[str, Any]]):
    """Display optimized chart analytics"""
    st.markdown("<h3 style='color: #8b5cf6; font-size: 1.5rem; margin-bottom: 1rem;'>📈 Funding Analytics</h3>", unsafe_allow_html=True)
    if not companies: 
        st.info("No data available to display charts.")
        return

    df_data = [{
        'company_name': clean_html_text(str(c.get('company_name', ''))),
        'round': clean_html_text(str(c.get('round', 'Unknown'))),
        'company_type': clean_html_text(str(c.get('company_type', 'Unknown'))),
        'source': clean_html_text(str(c.get('source', ''))) if c.get('source') and clean_html_text(str(c.get('source', ''))) else "ReturnonSecurity",
        'amount': c.get('amount', 0), 
        'date': c.get('date')
    } for c in companies]
    
    df = pd.DataFrame(df_data)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    df['company_type'] = df['company_type'].fillna('Unknown')
    df['round'] = df['round'].replace('', 'Unknown')

    tab1, tab2, tab3, tab4 = st.tabs(["💰 By Round", "📊 Distribution", "📅 Timeline", "🏢 By Type"])
    with tab1: display_funding_by_round_chart(df.copy())
    with tab2: display_amount_distribution_chart(df.copy())
    with tab3: display_funding_timeline_chart(df.copy())
    with tab4: display_funding_by_type_chart(df.copy())

def display_funding_by_round_chart(df: pd.DataFrame):
    """Display funding by round chart"""
    if df.empty or 'round' not in df.columns or 'amount' not in df.columns:
        st.caption("Insufficient data for 'Funding by Round' chart.")
        return
    
    df_agg = df.groupby('round', as_index=False).agg(Total_Amount=('amount', 'sum'))
    df_agg = df_agg[df_agg['Total_Amount'] > 0].sort_values('Total_Amount', ascending=False)
    
    if df_agg.empty: 
        st.caption("No disclosed funding amounts by round.")
        return
    
    fig = px.bar(df_agg, x='round', y='Total_Amount', title='Total Funding by Round', 
                 color='Total_Amount', color_continuous_scale=px.colors.sequential.Viridis)
    fig.update_layout(plot_bgcolor='#0E1117', paper_bgcolor='#0E1117', font_color='#FAFAFA', title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

def display_amount_distribution_chart(df: pd.DataFrame):
    """Display amount distribution chart"""
    if df.empty or 'amount' not in df.columns: 
        st.caption("No data for 'Amount Distribution'.")
        return
    
    df_filtered = df[df['amount'] > 1000] 
    if df_filtered.empty: 
        st.caption("No significant funding amounts for distribution.")
        return
    
    fig = px.histogram(df_filtered, x='amount', nbins=30, title='Funding Amount Distribution (> $1K)', 
                      color_discrete_sequence=['#636EFA'])
    fig.update_layout(plot_bgcolor='#0E1117', paper_bgcolor='#0E1117', font_color='#FAFAFA', title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

def display_funding_timeline_chart(df: pd.DataFrame):
    """Display funding timeline chart"""
    if df.empty or 'date' not in df.columns or 'amount' not in df.columns:
        st.caption("Insufficient data for 'Funding Timeline'.")
        return
    
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    
    if df.empty: 
        st.caption("No valid dates for timeline.")
        return
    
    df['month_year'] = df['date'].dt.to_period('M').astype(str)
    df_agg = df.groupby('month_year', as_index=False).agg(Total_Amount=('amount', 'sum')).sort_values('month_year')
    
    if df_agg.empty: 
        st.caption("No data for timeline after processing.")
        return
    
    fig = px.line(df_agg, x='month_year', y='Total_Amount', title='Funding Timeline (Monthly)', 
                  markers=True, color_discrete_sequence=['#00CC96'])
    fig.update_layout(plot_bgcolor='#0E1117', paper_bgcolor='#0E1117', font_color='#FAFAFA', title_x=0.5, xaxis_title='Month')
    st.plotly_chart(fig, use_container_width=True)

def display_funding_by_type_chart(df: pd.DataFrame):
    """Display funding by type chart"""
    if df.empty or 'company_type' not in df.columns:
        st.caption("No data for 'Funding by Type'.")
        return
    
    df_agg = df.groupby('company_type', as_index=False).agg(Company_Count=('company_name', 'nunique')) 
    df_agg = df_agg[df_agg['Company_Count'] > 0].sort_values('Company_Count', ascending=False)
    
    if df_agg.empty: 
        st.caption("No company counts by type available.")
        return
    
    fig = px.pie(df_agg, values='Company_Count', names='company_type', title='Companies by Type', 
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(plot_bgcolor='#0E1117', paper_bgcolor='#0E1117', font_color='#FAFAFA', title_x=0.5, legend_title_text='Company Type')
    st.plotly_chart(fig, use_container_width=True)

def display_pagination_info(current_page: int, total_pages: int, items_per_page: int, total_items: int):
    """Display pagination information"""
    start_item = (current_page - 1) * items_per_page + 1
    end_item = min(current_page * items_per_page, total_items)
    st.markdown(f"<p style='text-align: center; color: #9CA3AF; font-size:0.9rem;'>Showing {start_item}-{end_item} of {total_items:,} results</p>", unsafe_allow_html=True)