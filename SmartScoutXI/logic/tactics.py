import pandas as pd

def style_score(row, style='attack'):
    def safe(val):
        return 0 if pd.isna(val) else val

    pos = row['position'].strip().upper()

    g = safe(row.get('goals'))
    gc = safe(row.get('goal_conversion_%'))
    so = safe(row.get('shots_on_target'))
    sof = safe(row.get('shots_off_target'))
    a = safe(row.get('assists'))
    d = safe(row.get('successful_dribbles'))
    t = safe(row.get('tackles'))
    ip = safe(row.get('interceptions'))
    bcc = safe(row.get('big_chances_created'))
    pa = safe(row.get('accurate_passes_%'))
    tp = safe(row.get('total_passes'))
    sv = safe(row.get('saves'))
    cs = safe(row.get('cleansheets'))

    score = 0

    if style == 'Attack':
        if pos == 'F':
            score = g*5 + so*6 + sof*2 + a*1 + gc*3
        elif pos == 'M':
            score = a*10 + g*2 + t*2 + bcc*7 + ip*2
        elif pos == 'D':
            score = t*4 + g*20 + ip*2 + so*5 + pa*4
        elif pos == 'G':
            score = sv*4 + cs*2 + pa*2

    elif style == 'Defensive':
        if pos == 'F':
            score = g*4 + ip*2 + gc*4 + so*6
        elif pos == 'M':
            score = t*2 + tp*3 + ip*2
        elif pos == 'D':
            score = t*4 + ip*3 + pa*2 + tp*0.5
        elif pos == 'G':
            score = sv*4 + cs*3

    elif style == 'Possession':
        if pos == 'F':
            score = g*4 + tp*3 + so*2 + a*3 + bcc*2
        elif pos == 'M':
            score = bcc*9 + ip*1 + tp*4 + pa*5
        elif pos == 'D':
            score = t*2 + tp*4 + pa*2
        elif pos == 'G':
            score = sv*2 + cs*4

    elif style == 'Counter':
        if pos == 'F':
            score = g*5 + d*10 + bcc*3 + a*2 + so*5 + gc*4
        elif pos == 'M':
            score = tp*3 + t*2 + d*10 + ip*3 + pa*4 + bcc*4
        elif pos == 'D':
            score = t*4 + ip*3 + pa*2 + tp*0.5 + g*8
        elif pos == 'G':
            score = sv*2 + cs*5

    elif style == 'Balanced':
      all_styles = ['Attack', 'Defensive', 'Possession', 'Counter']
      score = sum([float(style_score(row, s)) for s in all_styles]) / len(all_styles)


    return float(score)