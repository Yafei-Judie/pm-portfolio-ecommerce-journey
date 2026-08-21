import os
import pickle
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score

# Same Morandi palette convention as analysis/make_charts.py in this repo.
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#ffffff"

ORDINAL_BLUE = ["#70afea", "#5b99d3", "#4583bc", "#2b6aa1"]
CAT_BLUE = "#4583bc"
DIVERGING_RED = ["#914337", "#cb7867"]
DIVERGING_GRAY = "#c5bcb1"
DIVERGING_BLUE = ["#70afea", "#4583bc"]
BLUE_DARK = "#12568b"

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]
plt.rcParams["text.color"] = INK_PRIMARY
plt.rcParams["axes.edgecolor"] = BASELINE
plt.rcParams["axes.labelcolor"] = INK_SECONDARY
plt.rcParams["xtick.color"] = INK_MUTED
plt.rcParams["ytick.color"] = INK_MUTED

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")
os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def style_ax(ax, hide_spines=("top", "right", "left")):
    for s in hide_spines:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(length=0)
    ax.set_facecolor(SURFACE)


d = pd.read_pickle(os.path.join(DATA, "clean_full.pkl"))
rfm = pd.read_pickle(os.path.join(DATA, "rfm.pkl"))
clv_df = pd.read_pickle(os.path.join(DATA, "clv_df.pkl"))
merged = pd.read_pickle(os.path.join(DATA, "merged_quadrant.pkl"))
with open(os.path.join(DATA, "models.pkl"), "rb") as f:
    m = pickle.load(f)

SEG_ORDER = ["Champions", "Loyal", "At Risk (high value)", "Recent, low value", "Lost / Low value"]
SEG_COLORS = {
    "Champions": ORDINAL_BLUE[3],
    "Loyal": ORDINAL_BLUE[2],
    "At Risk (high value)": DIVERGING_RED[1],
    "Recent, low value": DIVERGING_GRAY,
    "Lost / Low value": DIVERGING_RED[0],
}

# 1. Monthly revenue trend
monthly = d.set_index("InvoiceDate").resample("MS").Revenue.sum()
fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
fig.patch.set_facecolor(SURFACE)
ax.plot(monthly.index, monthly.values, color=CAT_BLUE, linewidth=2)
ax.fill_between(monthly.index, monthly.values, color=CAT_BLUE, alpha=0.08)
ax.scatter([monthly.index[-1]], [monthly.values[-1]], color=DIVERGING_RED[0], zorder=5, s=30)
ax.annotate("partial month\n(data ends Dec 9)", xy=(monthly.index[-1], monthly.values[-1]),
            xytext=(-90, 15), textcoords="offset points", fontsize=9, color=INK_MUTED)
style_ax(ax)
ax.set_title("Monthly revenue, cleaned transaction data (Dec 2009 - Dec 2011)", fontsize=12, color=INK_PRIMARY, loc="left")
ax.set_ylabel("Revenue (GBP)")
ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.8)
ax.set_axisbelow(True)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "01_monthly_revenue.png"))
plt.close()

# 2. RFM segment sizes + revenue share (two panels)
seg_counts = rfm.segment.value_counts().reindex(SEG_ORDER)
seg_rev = rfm.groupby("segment").monetary.sum().reindex(SEG_ORDER)
fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=150)
fig.patch.set_facecolor(SURFACE)
colors = [SEG_COLORS[s] for s in SEG_ORDER]
axes[0].barh(SEG_ORDER, seg_counts.values, color=colors)
style_ax(axes[0])
axes[0].set_title("Customers per segment", fontsize=11, loc="left")
axes[0].invert_yaxis()
axes[0].xaxis.grid(True, color=GRIDLINE, linewidth=0.8)
axes[0].set_axisbelow(True)
for i, v in enumerate(seg_counts.values):
    axes[0].text(v + 20, i, f"{v:,}", va="center", fontsize=9, color=INK_SECONDARY)

axes[1].barh(SEG_ORDER, seg_rev.values, color=colors)
style_ax(axes[1])
axes[1].set_title("Revenue per segment (observation window)", fontsize=11, loc="left")
axes[1].invert_yaxis()
axes[1].xaxis.grid(True, color=GRIDLINE, linewidth=0.8)
axes[1].set_axisbelow(True)
share = (seg_rev / seg_rev.sum() * 100)
for i, (v, s) in enumerate(zip(seg_rev.values, share.values)):
    axes[1].text(v + 60000, i, f"{s:.0f}%", va="center", fontsize=9, color=INK_SECONDARY)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "02_rfm_segments.png"))
plt.close()

# 3. Churn rate by segment
churn_by_seg = rfm.groupby("segment").churn.mean().reindex(SEG_ORDER)
fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
fig.patch.set_facecolor(SURFACE)
bars = ax.bar(SEG_ORDER, churn_by_seg.values * 100, color=[SEG_COLORS[s] for s in SEG_ORDER])
style_ax(ax)
ax.set_title("90-day forward churn rate by RFM segment", fontsize=12, loc="left")
ax.set_ylabel("Churn rate (%)")
ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.8)
ax.set_axisbelow(True)
for b, v in zip(bars, churn_by_seg.values):
    ax.text(b.get_x() + b.get_width() / 2, v * 100 + 1.5, f"{v*100:.0f}%", ha="center", fontsize=9, color=INK_SECONDARY)
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "03_churn_by_segment.png"))
plt.close()

# 4. ROC curves
fpr_l, tpr_l, _ = roc_curve(m["y_test"], m["logit_proba"])
fpr_r, tpr_r, _ = roc_curve(m["y_test"], m["rf_proba"])
auc_l = roc_auc_score(m["y_test"], m["logit_proba"])
auc_r = roc_auc_score(m["y_test"], m["rf_proba"])
fig, ax = plt.subplots(figsize=(7, 6), dpi=150)
fig.patch.set_facecolor(SURFACE)
ax.plot(fpr_l, tpr_l, color=ORDINAL_BLUE[1], linewidth=2, label=f"Logistic regression (AUC {auc_l:.3f})")
ax.plot(fpr_r, tpr_r, color=BLUE_DARK, linewidth=2, label=f"Random forest (AUC {auc_r:.3f})")
ax.plot([0, 1], [0, 1], color=BASELINE, linestyle="--", linewidth=1)
style_ax(ax, hide_spines=("top", "right"))
ax.set_xlabel("False positive rate")
ax.set_ylabel("True positive rate")
ax.set_title("Churn model performance, held-out test set", fontsize=12, loc="left")
ax.legend(frameon=False, loc="lower right", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "04_roc_curve.png"))
plt.close()

# 5. Feature importance (random forest)
rf = m["rf"]
feat_cols = m["feat_cols"]
imp = pd.Series(rf.feature_importances_, index=feat_cols).sort_values()
label_map = {
    "recency_days": "Days since last order",
    "frequency": "Order count",
    "monetary": "Total spend",
    "tenure_days": "Customer tenure (days)",
    "avg_order_value": "Avg order value",
    "n_countries": "Countries ordered from",
}
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
fig.patch.set_facecolor(SURFACE)
ax.barh([label_map[i] for i in imp.index], imp.values, color=CAT_BLUE)
style_ax(ax)
ax.set_title("What predicts churn: random forest feature importance", fontsize=12, loc="left")
ax.xaxis.grid(True, color=GRIDLINE, linewidth=0.8)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "05_feature_importance.png"))
plt.close()

# 6. CLV distribution by segment (log-scale box/strip since heavily right-skewed)
fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
fig.patch.set_facecolor(SURFACE)
order = [s for s in SEG_ORDER if s in clv_df.segment.unique()]
data_by_seg = [clv_df[clv_df.segment == s].clv_12m.clip(lower=1) for s in order]
bp = ax.boxplot(data_by_seg, vert=False, showfliers=False, patch_artist=True,
                 medianprops=dict(color=INK_PRIMARY, linewidth=1.5))
for patch, seg in zip(bp["boxes"], order):
    patch.set_facecolor(SEG_COLORS[seg])
    patch.set_alpha(0.75)
    patch.set_edgecolor(BASELINE)
ax.set_yticklabels(order)
ax.set_xscale("log")
style_ax(ax)
ax.set_title("Predicted 12-month CLV by RFM segment (log scale, outliers trimmed for readability)", fontsize=11, loc="left")
ax.set_xlabel("Predicted 12-month CLV (GBP, log scale)")
ax.xaxis.grid(True, color=GRIDLINE, linewidth=0.8)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "06_clv_by_segment.png"))
plt.close()

# 7. Churn-risk x CLV quadrant
risk_med = merged.churn_prob.median()
clv_med = merged.clv_12m.median()
quad_colors = {
    "Save first (high risk, high value)": DIVERGING_RED[0],
    "Protect, low effort (low risk, high value)": ORDINAL_BLUE[3],
    "Low priority (high risk, low value)": DIVERGING_GRAY,
    "Deprioritize (low risk, low value)": GRIDLINE,
}
fig, ax = plt.subplots(figsize=(9, 7), dpi=150)
fig.patch.set_facecolor(SURFACE)
for q, sub in merged.groupby("quadrant"):
    ax.scatter(sub.churn_prob, sub.clv_12m.clip(lower=1), s=14, alpha=0.55,
               color=quad_colors[q], label=q, linewidths=0)
ax.axvline(risk_med, color=BASELINE, linestyle="--", linewidth=1)
ax.axhline(clv_med, color=BASELINE, linestyle="--", linewidth=1)
ax.set_yscale("log")
style_ax(ax, hide_spines=("top", "right"))
ax.set_xlabel("Predicted churn probability")
ax.set_ylabel("Predicted 12-month CLV (GBP, log scale)")
ax.set_title("Who to prioritize: churn risk vs. predicted value", fontsize=12, loc="left")
ax.legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(1.01, 1))
plt.tight_layout()
plt.savefig(os.path.join(OUT, "07_risk_value_quadrant.png"))
plt.close()

print("charts written to", OUT)
print(sorted(os.listdir(OUT)))
