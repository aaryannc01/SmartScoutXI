from logic.tactics import style_score

def recommend_players(df, positions, style, tag='ALL', native='ALL', clubs='ALL', roles=[]):

        df = df.copy()
        df.columns = df.columns.str.strip().str.lower()

        df['team_cleaned'] = df['team'].astype(str).str.strip().str.lower()
        df['tag'] = df['tag'].astype(str).str.replace('_', '').str.title()
        df['native'] = df['native'].astype(str).str.strip().str.upper()

        # Tag filter
        tag = tag.replace('_', '').title()
        if tag != 'All':
            df = df[df['tag'] == tag]

        # Native filter
        native = native.strip().upper()
        print(f"🧾 Filtering native: '{native}'")
        if native != 'ALL':
            df = df[df['native'] == native]

        # Club filter
        if isinstance(clubs, list) and len(clubs) > 0:
           club_list = [club.strip().lower() for club in clubs]
           df = df[df['team_cleaned'].isin(club_list)]

        stat_cols = [
        'goals', 'assists', 'successful dribbles', 'tackles', 
        'accurate passes %', 'goal conversion %', 'shots on target',
        'shots off target', 'interceptions', 'big chances created', 'total passes', 'saves', 'cleansheet'
    ]

        recommendations = {}
        position_role_map = {
        'G': ['GK'],
        'D': ['CB', 'FB'],
        'M': ['CM', 'DM', 'AM'],
        'F': ['ST', 'W']
     }

        for pos in positions:
            pos_players = df[df['position'] == pos.upper()].copy()

            if roles and pos.upper() in position_role_map:
               valid_roles = position_role_map[pos.upper()]
               roles = [r.upper().strip() for r in roles if r.upper().strip() in valid_roles]
               if roles:
                  pos_players = pos_players[pos_players['role'].isin(roles)]

            if pos_players.empty:
               recommendations[pos.upper()] = pd.DataFrame(columns=['name', 'team', 'native'])
               continue

            pos_players['style_score'] = pos_players.apply(lambda row: style_score(row, style), axis=1)
            pos_players = pos_players.sort_values(by='style_score', ascending=False)

            display_cols = ['role', 'name', 'team', 'native'] + [col for col in stat_cols if col in pos_players.columns]
            recommendations[pos.upper()] = pos_players[display_cols].reset_index(drop=True)

        return recommendations