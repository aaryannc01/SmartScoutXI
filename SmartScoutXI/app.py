import streamlit as st
import pandas as pd

from logic.best_xi_logic import suggest_best_xi
from logic.scout_recommend import recommend_players

# Load data
df = pd.read_excel(r"C:\Users\Aaryan\OneDrive\Documents\SmartScoutXI\data\isl24-25allplayers.xlsx")
df.columns = df.columns.str.strip().str.lower()

# Streamlit App Title
st.title("⚽ Smart Scout XI")

# App mode selection
mode = st.sidebar.radio("Select Feature", ["📋 Scout Recommendation", "🏆 Best XI Selector"])

if mode == "📋 Scout Recommendation":
    st.header("📋 Scout Recommendation")

    style = st.selectbox("🎯 Choose Game Style", ["Attack", "Defensive", "Possession", "Counter", "Balanced"])
    tag = st.selectbox("🏷️ Player Tag", ["ALL", "Young_Talent", "Experienced", "Veteran"])
    native = st.selectbox("🌍 Nationality", ["ALL", "INDIA", "FOREIGN"])

    all_teams = sorted(df['team'].dropna().unique().tolist())
    clubs = st.multiselect("Select Clubs (leave empty for ALL)", options=all_teams)
    clubs_filter = [] if not clubs else clubs

    positions = st.multiselect("🧱 Desired Positions", ["G", "D", "M", "F"])
    position_role_map = {
    'G': ['GK'],
    'D': ['CB', 'FB'],
    'M': ['CM', 'DM', 'AM'],
    'F': ['ST', 'W']
    }

    # Get allowed roles
    allowed_roles = set()
    for pos in positions:
        allowed_roles.update(position_role_map.get(pos, []))

    roles = []
    if positions:
       roles = st.multiselect("Select Roles (Optional)", sorted(allowed_roles))


    if st.button("🔍 Recommend Players"):
        results = recommend_players(df, positions, style, tag, native, clubs_filter, roles)
        for pos, players in results.items():
            st.subheader(f"🔹 {pos} ({len(players)} players)")
            st.dataframe(players)

elif mode == "🏆 Best XI Selector":
    st.header("🏆 Best XI Selector")

    style = st.selectbox("🎯 Choose Game Style", ["Attack", "Defensive", "Possession", "Counter", "Balanced"])
    formation = st.selectbox("📐 Formation", ["4-3-3", "4-4-2", "3-5-2"])
    tag = st.selectbox("🏷️ Player Tag", ["ALL", "Young_Talent", "Experienced", "Veteran"])
    native = st.selectbox("🌍 Nationality", ["ALL", "INDIA", "FOREIGN"])

    all_teams = sorted(df['team'].dropna().unique().tolist())
    clubs = st.multiselect("Select Clubs (leave empty for ALL)", options=all_teams)

    # 👇🏽 Ensure it's always defined before button click
    clubs_filter = 'ALL' if not clubs else ','.join(clubs)

    if st.button("🏁 Generate Best XI"):
        print("Formation received in app.py:", formation)
        result = suggest_best_xi(df, style, formation, tag, native, clubs)
        if result:
            st.subheader("✅ Best XI")
            st.dataframe(result['best_xi'])

            for pos, backup in result['backup_players'].items():
                st.subheader(f"🔁 Backup for {pos}")
                st.dataframe(backup)
        else:
            st.error("❌ No players found matching your criteria.")