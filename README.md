# ⚽ SmartScoutXI

**SmartScoutXI** is a tactical football scouting and player recommendation system designed to help analysts, scouts, and enthusiasts identify players best suited to specific game styles and team needs. This tool combines data-driven logic, user filters, and custom scoring formulas to offer smart, personalized suggestions.

---

## 🔍 Features

- Recommends players tailored to five playstyles:
  - Attacking
  - Defensive
  - Possession
  - Counter
  - Balanced (average of all styles)
- Filters by:
  - Position (F, M, D, G)
  - Role (ST, Winger, CM, AM, DM, CB, FB, GK)
  - Nationality, Club, and Player Tags
- Tactical scoring formulas based on role-specific weights
- Ranks and displays top recommended players with backups

---

## ⚙️ Tech Stack

- **Python** – backend logic and scoring engine  
- **pandas** – data filtering and tactical score computation  
- **Streamlit** – interactive frontend  
- **Excel** – used for:
  - Player data collection
  - Performance metrics aggregation
  - Data cleaning and role labeling

---

## 🧠 How It Works

1. User selects a game style and position preferences.
2. The system applies custom tactical formulas (based on the style) to rank players.
3. Players are filtered based on selected role and additional criteria.
4. Top candidates are shown with backups for each role, making it easy to scout or build a team.

---

SmartScoutXI offers a simple, effective interface for football scouting. It’s built for users who love the game, understand tactical nuances, and want to blend data with football intelligence.
