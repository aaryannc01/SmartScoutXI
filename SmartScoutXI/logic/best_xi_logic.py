import pandas as pd
from logic.tactics import style_score

def load_data(path):
    df = pd.read_excel(path)
    df['native'] = df['native'].str.upper().str.strip()
    df['tag'] = df['tag'].str.replace(' ', '_').str.title().str.strip()
    df['position'] = df['position'].str.upper().str.strip()
    df['role'] = df['role'].str.upper().str.strip()
    return df

def parse_formation(formation):
    formation = formation.strip().replace('–', '-').replace('—', '-').replace('−', '-')
    if '-' not in formation and len(formation) == 3 and formation.isdigit():
        formation = f"{formation[0]}-{formation[1]}-{formation[2]}"
    parts = formation.split('-')
    if len(parts) == 3 and all(p.strip().isdigit() for p in parts):
        return tuple(int(p.strip()) for p in parts)
    raise ValueError("Formation must be in 'DEF-MID-FWD' format like 4-3-3")

def pick_best_xi(df, style, formation, native_filter='ALL', tag_filter='ALL', clubs_filter='ALL'):
    df = df.copy()

    if native_filter != 'ALL':
        df = df[df['native'] == native_filter]

    if tag_filter != 'ALL':
        df = df[df['tag'] == tag_filter]

    if clubs_filter and len(clubs_filter) > 0:
        df = df[df['team'].isin(clubs_filter)]

    if df.empty:
        print("[DEBUG] No players available after applying filters.")
        return pd.DataFrame()

    def safe_score(row):
        try:
            return float(style_score(row, style=style))
        except Exception as e:
            print(f"[DEBUG] style_score error on {row.get('name')}: {e}")
            return 0.0

    df['style_score'] = df.apply(safe_score, axis=1)

    def_count, mid_count, fw_count = parse_formation(formation)

    gk = df[df['position'] == 'G'].sort_values(by='style_score', ascending=False).head(1)

    if def_count >= 4:
        fb = df[(df['position'] == 'D') & (df['role'] == 'FB')].sort_values(by='style_score', ascending=False).head(2)
        cb = df[(df['position'] == 'D') & (df['role'] == 'CB') & (~df['name'].isin(fb['name']))].sort_values(by='style_score', ascending=False).head(def_count - 2)
        defenders = pd.concat([fb, cb])
    else:
        defenders = df[(df['position'] == 'D') & (df['role'] == 'CB')].sort_values(by='style_score', ascending=False).head(def_count)

    # Midfield logic
    if style.lower() == 'attacking':
        mid_roles = ['AM', 'CM']
    elif style.lower() == 'defensive':
        mid_roles = ['DM', 'CM']
    elif style.lower() == 'possession':
        mid_roles = ['CM'] * mid_count
    elif style.lower() == 'counter':
        mid_roles = ['CM', 'DM', 'AM'][:mid_count]
    else:
        mid_roles = ['AM', 'CM', 'DM'][:mid_count]

    mids = []
    used_names = set()
    role_pool = mid_roles.copy()

    while len(mids) < mid_count and role_pool:
        for role in role_pool:
            if len(mids) >= mid_count:
                break
            candidate = df[(df['position'] == 'M') & (df['role'] == role) & (~df['name'].isin(used_names))]
            if not candidate.empty:
                best = candidate.sort_values(by='style_score', ascending=False).head(1)
                if not best.empty:
                    mids.append(best)
                    used_names.update(best['name'])

        if len(mids) < mid_count:
            role_pool = ['CM', 'DM', 'AM']  # fallback pool

            # Try to fill remaining mids from fallback roles
            candidate = df[(df['position'] == 'M') & (~df['name'].isin(used_names))]
            needed = mid_count - len(mids)
            fallback_mids = candidate.sort_values(by='style_score', ascending=False).head(needed)
            if not fallback_mids.empty:
                mids.append(fallback_mids)
                used_names.update(fallback_mids['name'])

            break  # Avoid infinite loop

    midfielders = pd.concat(mids) if mids else pd.DataFrame()

    # Forward selection
    if fw_count == 3:
        w = df[(df['position'] == 'F') & (df['role'] == 'W')].sort_values(by='style_score', ascending=False).head(2)
        st = df[(df['position'] == 'F') & (df['role'] == 'ST') & (~df['name'].isin(w['name']))].sort_values(by='style_score', ascending=False).head(1)
        forwards = pd.concat([w, st])
    else:
        forwards = df[(df['position'] == 'F') & (df['role'] == 'ST')].sort_values(by='style_score', ascending=False).head(fw_count)

    return pd.concat([gk, defenders, midfielders, forwards])


def get_backups(df, best_xi, style, pos_code, def_count=0, fw_count=0):
    df = df.copy()
    df['style_score'] = df.apply(lambda row: style_score(row, style=style), axis=1)
    df = df[~df['name'].isin(best_xi['name'])]

    if pos_code == 'G':
        return df[df['position'] == 'G'].sort_values(by='style_score', ascending=False).head(3)

    elif pos_code == 'D':
        if def_count >= 4:
            fb = df[(df['position'] == 'D') & (df['role'] == 'FB')].sort_values(by='style_score', ascending=False).head(2)
            cb = df[(df['position'] == 'D') & (df['role'] == 'CB') & (~df['name'].isin(fb['name']))].sort_values(by='style_score', ascending=False).head(1)
            return pd.concat([fb, cb])
        else:
            return df[(df['position'] == 'D') & (df['role'] == 'CB')].sort_values(by='style_score', ascending=False).head(3)

    elif pos_code == 'M':
        return df[df['position'] == 'M'].sort_values(by='style_score', ascending=False).head(3)

    elif pos_code == 'F':
        if fw_count == 3:
            w = df[(df['position'] == 'F') & (df['role'] == 'W')].sort_values(by='style_score', ascending=False).head(2)
            st = df[(df['position'] == 'F') & (df['role'] == 'ST') & (~df['name'].isin(w['name']))].sort_values(by='style_score', ascending=False).head(1)
            return pd.concat([w, st])
        else:
            return df[(df['position'] == 'F') & (df['role'] == 'ST')].sort_values(by='style_score', ascending=False).head(3)

    return pd.DataFrame()

def suggest_best_xi(df, style, formation, tag='ALL', native='ALL', clubs='ALL'):
    def_count, mid_count, fw_count = parse_formation(formation)
    best_xi = pick_best_xi(df, style, formation, tag_filter=tag, native_filter=native, clubs_filter=clubs)


    backups = {}
    for pos_code, label in zip(['G', 'D', 'M', 'F'], ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']):
        backups[label] = get_backups(df, best_xi, style, pos_code, def_count=def_count, fw_count=fw_count)

    display_columns = [
        'role', 'name', 'team', 'native', 'goals', 'assists', 'shots on target',
        'goal conversion%', 'total passes', 'accurate passes%',
        'big chances created', 'tackles', 'interceptions',
        'cleansheet', 'saves'
    ]
    display_columns = [col for col in display_columns if col in df.columns]

    best_xi_display = best_xi[display_columns]

    formatted_backups = {}
    for pos, df_pos in backups.items():
        if not df_pos.empty:
            formatted_backups[pos] = df_pos[display_columns]
        else:
            formatted_backups[pos] = pd.DataFrame(columns=display_columns)

    position_order = ['G', 'D', 'M', 'F']
    best_xi['position_order'] = best_xi['position'].map(lambda x: position_order.index(x) if x in position_order else 4)
    best_xi = best_xi.sort_values(by='position_order').drop(columns=['position_order'])


    return {
        'best_xi': best_xi_display,
        'backup_players': formatted_backups
    }