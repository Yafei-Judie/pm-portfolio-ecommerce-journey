import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Chart chrome tokens (light mode, from the dataviz skill's validated reference palette)
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#ffffff"

# Ordinal blue ramp (funnel stages) light->dark, step 250/350/450/550
ORDINAL_BLUE = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab"]
CAT_BLUE = "#2a78d6"
DIVERGING_RED = ["#d03b3b", "#e88f8f"]  # critical-ish red, lighter red
DIVERGING_GRAY = "#c3c2b7"
DIVERGING_BLUE = ["#9ec5f4", "#2a78d6"]  # light blue, blue

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]
plt.rcParams["text.color"] = INK_PRIMARY
plt.rcParams["axes.edgecolor"] = BASELINE
plt.rcParams["axes.labelcolor"] = INK_SECONDARY
plt.rcParams["xtick.color"] = INK_MUTED
plt.rcParams["ytick.color"] = INK_MUTED

# Numbers below are copy-pasted from analysis/findings.md, which is itself sourced
# from real query output (sql/01-07). Re-run the queries first if you want to
# regenerate findings.md and this script from scratch instead of trusting these
# hardcoded values.
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")
os.makedirs(OUT, exist_ok=True)


def style_ax(ax, hide_spines=("top", "right", "left")):
    for s in hide_spines:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(length=0)
    ax.set_facecolor(SURFACE)


# 1. GA4 acquisition funnel: grouped bars, ordinal blue ramp
fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
fig.patch.set_facecolor(SURFACE)
months = ["2020-11", "2020-12", "2021-01"]
stages = ["Viewed item", "Added to cart", "Began checkout", "Purchased"]
data = {
    "2020-11": [21440, 2060, 4219, 1532],
    "2020-12": [22906, 7113, 3859, 1975],
    "2021-01": [19629, 3832, 1924, 1069],
}
x = range(len(months))
bar_w = 0.2
for i, stage in enumerate(stages):
    vals = [data[m][i] for m in months]
    xs = [xi + (i - 1.5) * bar_w for xi in x]
    ax.bar(xs, vals, width=bar_w, color=ORDINAL_BLUE[i], label=stage)
ax.set_xticks(list(x))
ax.set_xticklabels(months)
ax.set_ylabel("Distinct users")
ax.set_title("GA4 acquisition funnel by month", color=INK_PRIMARY, fontsize=13, loc="left", pad=14)
ax.yaxis.grid(True, color=GRIDLINE, linewidth=1)
ax.set_axisbelow(True)
style_ax(ax)
ax.legend(frameon=False, loc="upper right", fontsize=9, labelcolor=INK_SECONDARY)
fig.tight_layout()
fig.savefig(f"{OUT}/ga4_funnel.png", facecolor=SURFACE)
plt.close(fig)

# 2. GA4 channel revenue: horizontal bar, single hue, sorted descending
fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
fig.patch.set_facecolor(SURFACE)
channels = [
    "google / organic", "(direct) / (none)", "(data deleted)", "shop.googlemerchandisestore.com / referral",
    "<Other> / referral", "<Other> / <Other>", "google / cpc", "<Other> / organic", "<Other> / (data deleted)",
]
revenue = [95775, 79650, 50064, 46521, 37000, 35470, 9056, 8232, 397]
order = sorted(range(len(revenue)), key=lambda i: revenue[i])
channels = [channels[i] for i in order]
revenue = [revenue[i] for i in order]
ax.barh(channels, revenue, color=CAT_BLUE, height=0.6)
ax.set_xlabel("Revenue (USD)")
ax.set_title("GA4 revenue by acquisition channel (3-month total)", color=INK_PRIMARY, fontsize=13, loc="left", pad=14)
ax.xaxis.grid(True, color=GRIDLINE, linewidth=1)
ax.set_axisbelow(True)
style_ax(ax, hide_spines=("top", "right"))
for i, v in enumerate(revenue):
    ax.text(v + 1200, i, f"${v:,.0f}", va="center", fontsize=9, color=INK_SECONDARY)
fig.tight_layout()
fig.savefig(f"{OUT}/ga4_channel_revenue.png", facecolor=SURFACE)
plt.close(fig)

# 3. Olist % late by state: horizontal bar, single hue, sorted descending, top 12 worst
fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
fig.patch.set_facecolor(SURFACE)
states = ["AL", "MA", "SE", "PI", "CE", "RR", "BA", "RJ", "PA", "ES", "PB", "TO",
          "MS", "PE", "RN", "SC", "GO", "RS", "MT", "DF", "MG", "SP", "PR", "AC", "AP", "RO", "AM"]
pct_late = [21.4, 17.4, 15.2, 13.9, 13.8, 12.2, 12.2, 12.1, 11.2, 10.7, 10.4, 9.9,
            9.7, 9.6, 9.3, 8.2, 6.5, 6.1, 6.0, 5.7, 4.6, 4.5, 4.0, 3.8, 3.0, 2.9, 2.8]
pairs = sorted(zip(states, pct_late), key=lambda p: p[1])
states_sorted = [p[0] for p in pairs]
pct_sorted = [p[1] for p in pairs]
colors = [CAT_BLUE if s != "SP" else "#1c5cab" for s in states_sorted]
ax.barh(states_sorted, pct_sorted, color=colors, height=0.65)
ax.set_xlabel("% of delivered orders that arrived late")
ax.set_title("Delivery lateness by state, all 27 states with 30+ orders", color=INK_PRIMARY, fontsize=13, loc="left", pad=14)
ax.xaxis.grid(True, color=GRIDLINE, linewidth=1)
ax.set_axisbelow(True)
style_ax(ax, hide_spines=("top", "right"))
sp_i = states_sorted.index("SP")
ax.text(pct_sorted[sp_i] + 0.3, sp_i, "SP = 42% of all order volume", va="center", fontsize=8, color=INK_MUTED, style="italic")
fig.tight_layout()
fig.savefig(f"{OUT}/olist_late_by_state.png", facecolor=SURFACE)
plt.close(fig)

# 4. Olist delay vs review score: diverging red -> gray -> blue, the money chart
fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
fig.patch.set_facecolor(SURFACE)
buckets = ["7+ days late", "1-7 days late", "On the\nestimated day", "Early\n(1-7 days)", "Early\n(8+ days)"]
scores = [1.70, 2.71, 4.10, 4.22, 4.32]
colors = [DIVERGING_RED[0], DIVERGING_RED[1], DIVERGING_GRAY, DIVERGING_BLUE[0], DIVERGING_BLUE[1]]
bars = ax.bar(buckets, scores, color=colors, width=0.6)
ax.set_ylabel("Average review score (1-5)")
ax.set_ylim(0, 5)
ax.set_title("Delivery timing vs. average review score", color=INK_PRIMARY, fontsize=13, loc="left", pad=14)
ax.axhline(y=scores[2], color=BASELINE, linewidth=1, linestyle="--", zorder=0)
ax.yaxis.grid(True, color=GRIDLINE, linewidth=1)
ax.set_axisbelow(True)
style_ax(ax)
for bar, v in zip(bars, scores):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 0.08, f"{v:.2f}", ha="center", fontsize=10, color=INK_PRIMARY, fontweight="bold")
fig.tight_layout()
fig.savefig(f"{OUT}/olist_delay_vs_review.png", facecolor=SURFACE)
plt.close(fig)

# 5. Distance vs lateness: does physical distance explain delay better than state alone?
fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
fig.patch.set_facecolor(SURFACE)
buckets = ["Under 50km\n(same metro)", "50-300km", "300-800km", "800-1500km", "1500km+"]
pct_late_by_dist = [4.4, 5.0, 7.0, 7.5, 11.7]
bars = ax.bar(buckets, pct_late_by_dist, color=ORDINAL_BLUE + [ "#1c5cab"], width=0.6)
ax.set_ylabel("% of delivered orders that arrived late")
ax.set_title("Delivery lateness vs. seller-customer distance", color=INK_PRIMARY, fontsize=13, loc="left", pad=14)
ax.yaxis.grid(True, color=GRIDLINE, linewidth=1)
ax.set_axisbelow(True)
style_ax(ax)
for bar, v in zip(bars, pct_late_by_dist):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 0.25, f"{v}%", ha="center", fontsize=10, color=INK_PRIMARY, fontweight="bold")
ax.set_ylim(0, 13)
fig.tight_layout()
fig.savefig(f"{OUT}/olist_distance_vs_delay.png", facecolor=SURFACE)
plt.close(fig)

# 6. Repeat purchase rate by first-order delivery experience
fig, ax = plt.subplots(figsize=(7, 5), dpi=150)
fig.patch.set_facecolor(SURFACE)
groups = ["First order\non-time/early", "First order\nwas late"]
pct_repeat = [3.03, 2.55]
ns = [86993, 6357]
colors = [CAT_BLUE, DIVERGING_RED[0]]
bars = ax.bar(groups, pct_repeat, color=colors, width=0.5)
ax.set_ylabel("% who became a repeat customer")
ax.set_title("Repeat-purchase rate by first-order delivery experience", color=INK_PRIMARY, fontsize=13, loc="left", pad=14)
ax.yaxis.grid(True, color=GRIDLINE, linewidth=1)
ax.set_axisbelow(True)
style_ax(ax)
for bar, v, n in zip(bars, pct_repeat, ns):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 0.05, f"{v}%", ha="center", fontsize=11, color=INK_PRIMARY, fontweight="bold")
    ax.text(bar.get_x() + bar.get_width() / 2, v / 2, f"n={n:,}", ha="center", fontsize=8, color="#ffffff")
ax.set_ylim(0, 3.6)
fig.tight_layout()
fig.savefig(f"{OUT}/olist_repeat_purchase.png", facecolor=SURFACE)
plt.close(fig)

# 7. Freight cost as % of price by category
fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
fig.patch.set_facecolor(SURFACE)
categories = ["food_drink", "electronics", "furniture_living_room", "kitchen_dining_laundry_garden_furniture",
              "drinks", "office_furniture", "food", "furniture_decor", "housewares", "books_technical",
              "telephony", "luggage_accessories", "fashion_shoes", "costruction_tools_garden", "fashion_bags_accessories"]
freight_pct = [29.7, 29.1, 26.1, 25.9, 25.6, 25.0, 24.7, 23.7, 23.1, 22.4, 22.0, 21.7, 20.9, 20.7, 20.6]
pairs = sorted(zip(categories, freight_pct), key=lambda p: p[1])
cats_sorted = [p[0] for p in pairs]
pct_sorted = [p[1] for p in pairs]
ax.barh(cats_sorted, pct_sorted, color=CAT_BLUE, height=0.65)
ax.set_xlabel("Freight cost as % of item price")
ax.set_title("Freight economics: highest freight-to-price categories (200+ items)", color=INK_PRIMARY, fontsize=13, loc="left", pad=14)
ax.xaxis.grid(True, color=GRIDLINE, linewidth=1)
ax.set_axisbelow(True)
style_ax(ax, hide_spines=("top", "right"))
for i, v in enumerate(pct_sorted):
    ax.text(v + 0.3, i, f"{v}%", va="center", fontsize=9, color=INK_SECONDARY)
fig.tight_layout()
fig.savefig(f"{OUT}/olist_freight_economics.png", facecolor=SURFACE)
plt.close(fig)

print("done")
