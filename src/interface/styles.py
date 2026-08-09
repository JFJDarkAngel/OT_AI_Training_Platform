import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #F7F9FC;
            --surface: #FFFFFF;
            --surface-soft: #F4F7FA;
            --border: #E2E8F0;
            --text: #172033;
            --muted: #6B778C;
            --accent: #2563EB;
            --accent-soft: #EFF6FF;
            --success: #168A52;
            --warning: #B7791F;
            --danger: #D64545;
        }

        html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", Arial, sans-serif;
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 1.35rem;
            padding-bottom: 2.5rem;
        }

        .app-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 1rem;
            margin-bottom: 1.25rem;
            border-bottom: 1px solid var(--border);
        }

        .brand-wrap {
            display: flex;
            align-items: center;
            gap: .85rem;
        }

        .brand-icon {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: grid;
            place-items: center;
            background: var(--accent-soft);
            border: 1px solid #D9E7FF;
            font-size: 1.2rem;
        }

        .brand-title {
            margin: 0;
            color: var(--text);
            font-size: 1.12rem;
            font-weight: 750;
        }

        .brand-subtitle {
            color: var(--muted);
            font-size: .82rem;
            margin-top: .1rem;
        }

        .page-title {
            font-size: 2rem;
            font-weight: 760;
            margin: .15rem 0 .25rem 0;
            color: var(--text);
            letter-spacing: -.025em;
        }

        .page-subtitle {
            color: var(--muted);
            font-size: .95rem;
            margin-bottom: 1.3rem;
        }

        .metric-card,
        .panel-card {
            border: 1px solid var(--border);
            background: var(--surface);
            border-radius: 15px;
            box-shadow: 0 3px 12px rgba(23, 32, 51, .045);
        }

        .metric-card {
            padding: 1.05rem 1.15rem;
            min-height: 118px;
        }

        .metric-label {
            color: var(--muted);
            font-size: .82rem;
            font-weight: 550;
            margin-bottom: .55rem;
        }

        .metric-value {
            color: var(--text);
            font-size: 1.75rem;
            font-weight: 760;
            line-height: 1;
            margin-bottom: .6rem;
        }

        .metric-note {
            color: var(--muted);
            font-size: .78rem;
        }

        .panel-card {
            padding: 1.15rem 1.2rem;
            margin-bottom: 1rem;
        }

        .section-title {
            color: var(--text);
            font-size: 1rem;
            font-weight: 720;
            margin-bottom: .2rem;
        }

        .section-note {
            color: var(--muted);
            font-size: .82rem;
            margin-bottom: .9rem;
        }

        .scenario-row {
            display: grid;
            grid-template-columns: 1.1fr 2.4fr .9fr .8fr .9fr;
            gap: .75rem;
            align-items: center;
            padding: .82rem .2rem;
            border-top: 1px solid #EDF1F5;
        }

        .scenario-row.header {
            border-top: 0;
            color: var(--muted);
            font-size: .74rem;
            text-transform: uppercase;
            letter-spacing: .04em;
            padding-top: .1rem;
            padding-bottom: .55rem;
        }

        .scenario-cell {
            color: var(--text);
            font-size: .84rem;
            overflow-wrap: anywhere;
        }

        .scenario-cell.muted {
            color: var(--muted);
        }

        .badge {
            display: inline-block;
            padding: .28rem .55rem;
            border-radius: 999px;
            font-size: .73rem;
            font-weight: 650;
            border: 1px solid var(--border);
            background: var(--surface-soft);
        }

        .badge-evaluated {
            color: #117A48;
            background: #ECFDF3;
            border-color: #BDECCF;
        }

        .badge-draft {
            color: #996515;
            background: #FFF8E7;
            border-color: #F3DCA6;
        }

        .severity-critical { color: #C92A2A; font-weight: 650; }
        .severity-high { color: #D65A18; font-weight: 650; }
        .severity-medium { color: #A56B00; font-weight: 650; }
        .severity-low { color: #168A52; font-weight: 650; }
        .severity-unknown { color: var(--muted); }

        div[data-testid="stButton"] > button {
            width: 100%;
            border-radius: 9px;
            min-height: 42px;
            font-weight: 650;
            border: 1px solid #D7DEE8;
            background: #FFFFFF;
            color: #263348;
            box-shadow: none;
        }

        div[data-testid="stButton"] > button:hover {
            border-color: #AFC8F5;
            color: var(--accent);
            background: #F8FBFF;
        }

        div[data-testid="stButton"] > button[kind="primary"] {
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }

        div[data-testid="stButton"] > button[kind="primary"]:hover {
            background: #1D4ED8;
            color: white;
            border-color: #1D4ED8;
        }

        div[data-testid="stAlert"] {
            border-radius: 10px;
        }

        .empty-state {
            color: var(--muted);
            font-size: .88rem;
            padding: 1rem 0 .3rem 0;
        }

        @media (max-width: 900px) {
            .scenario-row {
                grid-template-columns: 1fr;
                gap: .25rem;
                padding: .9rem 0;
            }

            .scenario-row.header {
                display: none;
            }
        }

        /* HMI training visualization */
        .training-banner {
            display: flex;
            align-items: center;
            gap: .65rem;
            padding: .85rem 1rem;
            margin-bottom: 1.2rem;
            background: #FFF8E7;
            border: 1px solid #F3DCA6;
            border-radius: 11px;
            color: #7B5B17;
            font-size: .82rem;
        }
        
        .training-banner strong {
            color: #6E4F0C;
        }
        
        .hmi-main-card {
            min-height: 120px;
            padding: 1.05rem 1.15rem;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            box-shadow: 0 3px 12px rgba(23,32,51,.045);
        }
        
        .hmi-card-label,
        .hmi-tile-label {
            color: #6B778C;
            font-size: .77rem;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: .035em;
        }
        
        .hmi-card-value {
            display: flex;
            align-items: center;
            gap: .45rem;
            color: #172033;
            font-size: 1.25rem;
            font-weight: 760;
            margin: .55rem 0 .35rem 0;
        }
        
        .hmi-card-sub,
        .hmi-tile-detail {
            color: #8792A3;
            font-size: .75rem;
        }
        
        .hmi-status-tile {
            min-height: 135px;
            padding: 1rem;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 13px;
            box-shadow: 0 3px 12px rgba(23,32,51,.04);
        }
        
        .hmi-tile-top {
            display: flex;
            align-items: center;
            gap: .42rem;
        }
        
        .hmi-tile-value {
            color: #172033;
            font-size: 1.3rem;
            font-weight: 760;
            margin: .75rem 0 .35rem 0;
        }
        
        .hmi-status-dot {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            display: inline-block;
            flex: 0 0 auto;
        }
        
        .hmi-good {
            background: #22A06B;
            box-shadow: 0 0 0 4px rgba(34,160,107,.10);
        }
        
        .hmi-warning {
            background: #E0A11B;
            box-shadow: 0 0 0 4px rgba(224,161,27,.10);
        }
        
        .hmi-bad {
            background: #D84A4A;
            box-shadow: 0 0 0 4px rgba(216,74,74,.10);
        }
        
        .hmi-neutral {
            background: #8995A6;
            box-shadow: 0 0 0 4px rgba(137,149,166,.10);
        }
        
        .hmi-process-panel {
            padding: 1.15rem 1.2rem 1.25rem;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 15px;
            box-shadow: 0 3px 12px rgba(23,32,51,.045);
        }
        
        .hmi-panel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .hmi-panel-title {
            color: #172033;
            font-size: 1rem;
            font-weight: 740;
        }
        
        .hmi-panel-sub {
            color: #7A8799;
            font-size: .78rem;
            margin-top: .15rem;
        }
        
        .hmi-mode-pill {
            padding: .3rem .6rem;
            border-radius: 999px;
            background: #F4F7FA;
            border: 1px solid #E2E8F0;
            color: #536174;
            font-size: .72rem;
            font-weight: 700;
        }
        
        .hmi-process-line {
            display: grid;
            grid-template-columns: 1fr .55fr 1fr .55fr 1fr .55fr 1fr;
            align-items: center;
            gap: .4rem;
            padding: 1.2rem .5rem;
            background: #F8FAFC;
            border: 1px solid #EDF1F5;
            border-radius: 12px;
        }
        
        .hmi-node {
            text-align: center;
        }
        
        .hmi-node-box {
            width: 74px;
            height: 58px;
            margin: 0 auto;
            display: grid;
            place-items: center;
            border-radius: 8px;
            background: #FFFFFF;
            border: 2px solid #9CB9E8;
            color: #1E4F9A;
            font-weight: 800;
            font-size: .8rem;
        }
        
        .hmi-node-caption {
            margin-top: .45rem;
            color: #6B778C;
            font-size: .68rem;
            min-height: 2em;
        }
        
        .hmi-connector {
            height: 2px;
            background: linear-gradient(90deg, #A8B7CA, #6E96CC);
            position: relative;
        }
        
        .hmi-connector:after {
            content: "";
            position: absolute;
            right: -1px;
            top: -3px;
            width: 7px;
            height: 7px;
            border-top: 2px solid #6E96CC;
            border-right: 2px solid #6E96CC;
            transform: rotate(45deg);
        }
        
        .hmi-process-note {
            margin-top: 1rem;
            color: #7A8799;
            font-size: .76rem;
            line-height: 1.5;
        }
        
        .hmi-key-row {
            display: flex;
            align-items: center;
            gap: .55rem;
            padding: .5rem 0;
            color: #5E6C7E;
            font-size: .78rem;
            border-bottom: 1px solid #EDF1F5;
        }
        
        .hmi-key-row:last-child {
            border-bottom: 0;
        }
        
        @media (max-width: 900px) {
            .training-banner {
                align-items: flex-start;
                flex-direction: column;
            }
        
            .hmi-process-line {
                grid-template-columns: 1fr;
            }
        
            .hmi-connector {
                width: 2px;
                height: 26px;
                margin: 0 auto;
                background: #8EA6C3;
            }
        
            .hmi-connector:after {
                display: none;
            }
        }

        /* Stakeholder response additions */
        .summary-line {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding: .56rem 0;
            border-bottom: 1px solid #EDF1F5;
            color: #6B778C;
            font-size: .8rem;
        }
        .summary-line:last-child { border-bottom: 0; }
        .summary-line strong {
            color: #253146;
            font-weight: 700;
            text-align: right;
        }

        /* Evaluation page additions */
        .evaluation-ready-card{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:1rem 1.15rem;margin-bottom:1rem;background:#F8FFFB;border:1px solid #CDEAD8;border-radius:13px}
        .evaluation-ready-title{color:#176B44;font-size:.95rem;font-weight:750}
        .evaluation-ready-sub{color:#6B778C;font-size:.78rem;margin-top:.15rem}
        .evaluation-ready-count{color:#176B44;font-size:.8rem;font-weight:750;padding:.3rem .6rem;border-radius:999px;background:#ECFDF3}
        .evaluation-role-card{min-height:115px;padding:1rem;background:#FFF;border:1px solid #E2E8F0;border-radius:13px;text-align:center}
        .evaluation-role-check{width:28px;height:28px;margin:0 auto .6rem;border-radius:999px;display:grid;place-items:center;background:#ECFDF3;color:#168A52;font-weight:800}
        .evaluation-role-name{color:#172033;font-size:.85rem;font-weight:720}
        .evaluation-role-status{color:#7A8799;font-size:.72rem;margin-top:.2rem}
        .evaluation-process-row{display:flex;align-items:center;gap:.65rem;padding:.65rem 0;border-bottom:1px solid #EDF1F5;color:#536174;font-size:.82rem}
        .evaluation-process-row:last-child{border-bottom:0}
        .evaluation-process-row span{width:24px;height:24px;flex:0 0 auto;border-radius:999px;display:grid;place-items:center;background:#EFF6FF;color:#2563EB;font-size:.7rem;font-weight:800}
        .evaluation-score-card{min-height:125px;padding:1rem;background:#FFF;border:1px solid #E2E8F0;border-radius:13px;text-align:center}
        .evaluation-score-card.overall{background:#F8FBFF;border-color:#BFD6FF}
        .evaluation-score-label{color:#6B778C;font-size:.76rem;font-weight:650}
        .evaluation-score-value{color:#172033;font-size:1.75rem;font-weight:800;line-height:1;margin-top:.6rem}
        .evaluation-score-unit{color:#8A96A8;font-size:.7rem;margin-top:.3rem}

        /* Final Results page */
        .results-overall-card,
        .results-info-card,
        .stakeholder-result-card {
            background:#FFFFFF;
            border:1px solid #E2E8F0;
            border-radius:14px;
            box-shadow:0 3px 12px rgba(23,32,51,.045);
        }
        .results-overall-card {
            min-height:200px;
            padding:1.15rem;
            text-align:center;
        }
        .results-info-card {
            min-height:200px;
            padding:1.15rem;
        }
        .results-card-label {
            color:#6B778C;
            font-size:.76rem;
            font-weight:700;
            text-transform:uppercase;
            letter-spacing:.04em;
        }
        .results-overall-score {
            color:#172033;
            font-size:3rem;
            font-weight:820;
            line-height:1;
            margin-top:1rem;
        }
        .results-score-unit {
            color:#8A96A8;
            font-size:.75rem;
            margin:.2rem 0 .7rem;
        }
        .results-score-band {
            display:inline-block;
            padding:.28rem .6rem;
            border-radius:999px;
            font-size:.7rem;
            font-weight:750;
        }
        .score-good { background:#ECFDF3; color:#168A52; }
        .score-warning { background:#FFF8E7; color:#9A6812; }
        .score-bad { background:#FFF0F0; color:#C83D3D; }
        .results-scenario-title {
            color:#172033;
            font-size:1.05rem;
            font-weight:760;
            margin-top:.8rem;
        }
        .results-scenario-id {
            color:#7A8799;
            font-size:.76rem;
            margin-top:.15rem;
        }
        .results-mini-grid {
            display:grid;
            grid-template-columns:1fr 1fr;
            gap:.65rem;
            margin-top:1rem;
        }
        .results-mini-grid div {
            padding:.65rem;
            background:#F8FAFC;
            border:1px solid #EDF1F5;
            border-radius:9px;
        }
        .results-mini-grid span,
        .results-mini-grid strong {
            display:block;
        }
        .results-mini-grid span {
            color:#8A96A8;
            font-size:.68rem;
        }
        .results-mini-grid strong {
            color:#253146;
            font-size:.8rem;
            margin-top:.15rem;
        }
        .results-report-title {
            color:#172033;
            font-size:1rem;
            font-weight:760;
            margin-top:.8rem;
        }
        .results-report-note {
            color:#6B778C;
            font-size:.78rem;
            line-height:1.5;
            margin-top:.45rem;
        }
        .stakeholder-result-card {
            min-height:140px;
            padding:1rem;
            text-align:center;
        }
        .stakeholder-result-name {
            color:#536174;
            font-size:.8rem;
            font-weight:700;
        }
        .stakeholder-result-score {
            color:#172033;
            font-size:1.75rem;
            font-weight:800;
            margin:.65rem 0 .55rem;
        }
        .stakeholder-result-score span {
            color:#8A96A8;
            font-size:.7rem;
            font-weight:600;
        }
        .results-copy {
            color:#4F5D70;
            font-size:.88rem;
            line-height:1.65;
        }
        .results-divider {
            height:1px;
            background:#EDF1F5;
            margin:1rem 0;
        }
        .results-snapshot-row {
            display:flex;
            justify-content:space-between;
            gap:1rem;
            padding:.6rem 0;
            border-bottom:1px solid #EDF1F5;
            color:#6B778C;
            font-size:.8rem;
        }
        .results-snapshot-row:last-child { border-bottom:0; }
        .results-snapshot-row strong {
            color:#253146;
            text-align:right;
        }
        .recommendation-row {
            display:grid;
            grid-template-columns:110px 1fr;
            gap:1rem;
            align-items:start;
            padding:.9rem 1rem;
            margin-bottom:.65rem;
            background:#FFFFFF;
            border:1px solid #E2E8F0;
            border-radius:11px;
        }
        .recommendation-priority {
            display:inline-block;
            width:max-content;
            padding:.25rem .5rem;
            border-radius:999px;
            background:#EFF6FF;
            color:#2563EB;
            font-size:.7rem;
            font-weight:750;
        }
        .recommendation-text {
            color:#3E4A5C;
            font-size:.84rem;
            line-height:1.55;
        }
        @media (max-width:900px) {
            .recommendation-row { grid-template-columns:1fr; }
            .results-mini-grid { grid-template-columns:1fr; }
        }

        /* Scenario History */
        .history-card {
            background:#FFFFFF;
            border:1px solid #E2E8F0;
            border-radius:14px;
            padding:1.05rem 1.15rem;
            box-shadow:0 3px 12px rgba(23,32,51,.04);
        }
        .history-card-top {
            display:flex;
            align-items:flex-start;
            justify-content:space-between;
            gap:1rem;
        }
        .history-title {
            color:#172033;
            font-size:.95rem;
            font-weight:760;
        }
        .history-id {
            color:#7A8799;
            font-size:.74rem;
            margin-top:.15rem;
        }
        .history-pill {
            display:inline-block;
            padding:.27rem .55rem;
            border-radius:999px;
            background:#F4F7FA;
            border:1px solid #E2E8F0;
            color:#536174;
            font-size:.7rem;
            font-weight:700;
        }
        .history-meta-grid {
            display:grid;
            grid-template-columns:repeat(4, 1fr);
            gap:.65rem;
            margin-top:1rem;
        }
        .history-meta-grid div {
            padding:.65rem .7rem;
            background:#F8FAFC;
            border:1px solid #EDF1F5;
            border-radius:9px;
        }
        .history-meta-grid span,
        .history-meta-grid strong {
            display:block;
        }
        .history-meta-grid span {
            color:#8A96A8;
            font-size:.67rem;
        }
        .history-meta-grid strong {
            color:#253146;
            font-size:.77rem;
            margin-top:.16rem;
        }
        @media (max-width:900px) {
            .history-meta-grid {
                grid-template-columns:1fr 1fr;
            }
        }

        /* =========================
           Final Interface Polish
           Safe global additions only
           ========================= */
        
        /* Typography and page rhythm */
        .stApp {
            background: #F7F9FC;
        }
        
        .block-container {
            max-width: 1440px;
            padding-top: 1.2rem;
            padding-bottom: 2.5rem;
        }
        
        .page-title {
            margin-top: .15rem;
            margin-bottom: .2rem;
        }
        
        .page-subtitle {
            max-width: 920px;
            line-height: 1.55;
        }
        
        /* Stronger card consistency */
        .metric-card,
        .panel-card,
        .hmi-main-card,
        .hmi-status-tile,
        .evaluation-role-card,
        .evaluation-score-card,
        .results-overall-card,
        .results-info-card,
        .stakeholder-result-card,
        .history-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 14px rgba(23, 32, 51, .045);
        }
        
        .metric-card:hover,
        .history-card:hover {
            border-color: #D3DDEA;
        }
        
        /* Form controls */
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        div[data-baseweb="select"] > div {
            border-radius: 10px !important;
            border-color: #DCE3EB !important;
            background: #FFFFFF !important;
        }
        
        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="textarea"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within {
            border-color: #8BB4F7 !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, .08) !important;
        }
        
        input:disabled {
            color: #7A8799 !important;
            -webkit-text-fill-color: #7A8799 !important;
        }
        
        /* Labels */
        label[data-testid="stWidgetLabel"] p {
            color: #263348;
            font-weight: 650;
        }
        
        /* Buttons */
        div[data-testid="stButton"] > button,
        div[data-testid="stDownloadButton"] > button {
            min-height: 42px;
            border-radius: 9px;
            font-weight: 700;
            transition:
                border-color .15s ease,
                background .15s ease,
                color .15s ease,
                transform .08s ease;
        }
        
        div[data-testid="stButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover {
            transform: translateY(-1px);
        }
        
        div[data-testid="stButton"] > button:active,
        div[data-testid="stDownloadButton"] > button:active {
            transform: translateY(0);
        }
        
        /* Primary CTA remains visually dominant */
        div[data-testid="stButton"] > button[kind="primary"],
        div[data-testid="stDownloadButton"] > button[kind="primary"] {
            background: #2563EB;
            border-color: #2563EB;
            color: #FFFFFF;
        }
        
        div[data-testid="stButton"] > button[kind="primary"]:hover,
        div[data-testid="stDownloadButton"] > button[kind="primary"]:hover {
            background: #1D4ED8;
            border-color: #1D4ED8;
            color: #FFFFFF;
        }
        
        /* Disabled controls */
        div[data-testid="stButton"] > button:disabled {
            opacity: .55;
            cursor: not-allowed;
            transform: none !important;
        }
        
        /* Alerts */
        div[data-testid="stAlert"] {
            border-radius: 11px;
            border-width: 1px;
        }
        
        /* Progress */
        div[data-testid="stProgress"] > div > div > div {
            border-radius: 999px;
        }
        
        /* Expanders */
        details[data-testid="stExpander"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 11px;
            overflow: hidden;
        }
        
        details[data-testid="stExpander"] summary {
            color: #263348;
            font-weight: 650;
        }
        
        /* Native Streamlit metrics used in Scenario History */
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 13px;
            padding: .9rem 1rem;
            box-shadow: 0 3px 12px rgba(23, 32, 51, .035);
        }
        
        div[data-testid="stMetricLabel"] {
            color: #6B778C;
        }
        
        div[data-testid="stMetricValue"] {
            color: #172033;
        }
        
        /* Search/filter spacing */
        div[data-testid="stTextInput"],
        div[data-testid="stSelectbox"],
        div[data-testid="stTextArea"] {
            margin-bottom: .15rem;
        }
        
        /* Scenario History CTA spacing */
        .history-card + div[data-testid="stHorizontalBlock"] {
            margin-top: .35rem;
            margin-bottom: .9rem;
        }
        
        /* HMI status clarity */
        .hmi-status-tile {
            transition: transform .12s ease, border-color .12s ease;
        }
        
        .hmi-status-tile:hover {
            transform: translateY(-1px);
            border-color: #D3DDEA;
        }
        
        .hmi-status-dot {
            width: 10px;
            height: 10px;
        }
        
        /* Results hierarchy */
        .results-overall-score,
        .evaluation-score-value,
        .stakeholder-result-score {
            letter-spacing: -.03em;
        }
        
        .recommendation-row {
            transition: border-color .12s ease, transform .12s ease;
        }
        
        .recommendation-row:hover {
            border-color: #CDD9E8;
            transform: translateY(-1px);
        }
        
        /* Better readability for long scenario text */
        .results-copy,
        .results-report-note,
        .section-note,
        .hmi-card-sub,
        .hmi-tile-detail,
        .history-id {
            line-height: 1.5;
        }
        
        /* Consistent section spacing */
        .section-title {
            margin-top: .15rem;
        }
        
        .section-note {
            margin-bottom: .85rem;
        }
        
        /* Hide Streamlit chrome while preserving layout */
        #MainMenu,
        footer {
            visibility: hidden;
        }
        
        /* Keyboard accessibility */
        button:focus-visible,
        input:focus-visible,
        textarea:focus-visible {
            outline: 3px solid rgba(37, 99, 235, .18) !important;
            outline-offset: 2px !important;
        }
        
        /* Mobile cleanup */
        @media (max-width: 900px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        
            .app-header {
                margin-bottom: 1rem;
            }
        
            .page-title {
                font-size: 1.65rem;
            }
        
            .history-card-top,
            .evaluation-ready-card {
                align-items: flex-start;
                flex-direction: column;
            }
        
            .results-overall-card,
            .results-info-card {
                min-height: auto;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
