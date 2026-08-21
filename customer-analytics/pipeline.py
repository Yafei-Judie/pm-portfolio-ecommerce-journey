"""
Full run to nail down exact numbers before assembling the final notebook.
Not part of the shipped repo — exploratory driver script.
"""
import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, recall_score, roc_curve
from sklearn.preprocessing import StandardScaler
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data

pd.set_option("display.width", 140)

df = pd.read_pickle("data/raw_combined.pkl")

with open("data/matched_cancel_idx.pkl", "rb") as f:
    matched_cancel_idx = pickle.load(f)

# --- cleaning ---
raw_n = len(df)
d = df.dropna(subset=["Customer ID"]).copy()
null_cid_dropped = raw_n - len(d)
d = d[~d.Invoice.astype(str).str.startswith("C")]
# also drop the ORIGINAL order line for any purchase later matched to a cancellation
# (customer/stockcode/quantity/nearest-prior-date match — see match_cancellations.py).
# Dropping only C-prefixed invoices, the standard approach for this dataset, leaves
# the original order sitting in "clean" data even when it never shipped. Caught this
# because it was the single line inflating one CLV segment 6x: an 80,995-unit order
# (customer 16446, stockcode 23843) placed and cancelled 12 minutes later.
cancel_matched_n = len(set(d.index) & matched_cancel_idx)
d = d[~d.index.isin(matched_cancel_idx)]
non_product = d.StockCode.astype(str).isin(["POST", "DOT", "M", "m", "D", "S", "ADJUST", "AMAZONFEE",
                                              "CRUK", "PADS", "B", "GIFT"])
d = d[~non_product]
d = d[(d.Quantity > 0) & (d.Price > 0)]
d["Revenue"] = d.Quantity * d.Price
d["Customer ID"] = d["Customer ID"].astype(int)

print("raw rows:", raw_n)
print("dropped for null Customer ID:", null_cid_dropped, f"({null_cid_dropped/raw_n:.4f})")
print("dropped as matched-cancellation originals:", cancel_matched_n)
print("clean rows:", len(d), "unique customers:", d["Customer ID"].nunique())
print("date range:", d.InvoiceDate.min(), d.InvoiceDate.max())

# --- churn label: cutoff date, 90-day forward outcome window ---
max_date = d.InvoiceDate.max()
outcome_window_days = 90
cutoff = max_date - pd.Timedelta(days=outcome_window_days)
print("\ncutoff:", cutoff, "outcome window end:", max_date)

obs = d[d.InvoiceDate <= cutoff].copy()
out = d[d.InvoiceDate > cutoff].copy()

# only customers with >=1 purchase in observation window are eligible for a label
eligible_customers = obs["Customer ID"].unique()
print("customers eligible (purchased before cutoff):", len(eligible_customers))

purchased_in_outcome = set(out["Customer ID"].unique())
churn_label = pd.Series(
    {cid: 0 if cid in purchased_in_outcome else 1 for cid in eligible_customers}
)
print("churn rate in label:", churn_label.mean(), "n churned:", churn_label.sum(), "of", len(churn_label))

# --- RFM / features from observation window ONLY ---
snapshot_date = cutoff + pd.Timedelta(days=1)
grp = obs.groupby("Customer ID")
rfm = grp.agg(
    last_purchase=("InvoiceDate", "max"),
    first_purchase=("InvoiceDate", "min"),
    frequency=("Invoice", "nunique"),
    monetary=("Revenue", "sum"),
    avg_order_value=("Revenue", lambda s: s.sum() / obs.loc[s.index, "Invoice"].nunique()),
    n_countries=("Country", "nunique"),
).reset_index()
rfm["recency_days"] = (snapshot_date - rfm.last_purchase).dt.days
rfm["tenure_days"] = (rfm.last_purchase - rfm.first_purchase).dt.days
rfm["avg_days_between_orders"] = np.where(
    rfm.frequency > 1, rfm.tenure_days / (rfm.frequency - 1), np.nan
)
rfm["churn"] = rfm["Customer ID"].map(churn_label)

print("\nrfm shape:", rfm.shape)
print(rfm[["frequency", "monetary", "recency_days", "tenure_days"]].describe())

# quantile RFM segments (on obs-window data, standard R/F/M scoring 1-4, higher=better)
rfm["R_score"] = pd.qcut(rfm.recency_days.rank(method="first"), 4, labels=[4, 3, 2, 1]).astype(int)
rfm["F_score"] = pd.qcut(rfm.frequency.rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["M_score"] = pd.qcut(rfm.monetary.rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["RFM_sum"] = rfm.R_score + rfm.F_score + rfm.M_score


def segment(row):
    if row.RFM_sum >= 10:
        return "Champions"
    elif row.R_score >= 3 and row.RFM_sum >= 7:
        return "Loyal"
    elif row.R_score <= 2 and row.RFM_sum >= 7:
        return "At Risk (high value)"
    elif row.R_score >= 3 and row.RFM_sum < 7:
        return "Recent, low value"
    else:
        return "Lost / Low value"


rfm["segment"] = rfm.apply(segment, axis=1)
print("\nsegment sizes:")
print(rfm.segment.value_counts())
print("\nsegment revenue share:")
seg_rev = rfm.groupby("segment").monetary.sum().sort_values(ascending=False)
print(seg_rev)
print((seg_rev / seg_rev.sum()).round(4))
print("\nchurn rate by segment:")
print(rfm.groupby("segment").churn.mean().sort_values(ascending=False))

# --- churn model ---
feat_cols = ["recency_days", "frequency", "monetary", "avg_order_value", "tenure_days", "n_countries"]
model_df = rfm.dropna(subset=feat_cols).copy()
X = model_df[feat_cols]
y = model_df["churn"]
print("\nmodel_df rows (non-null features):", len(model_df), "churn rate:", y.mean())

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

logit = LogisticRegression(max_iter=1000, random_state=42)
logit.fit(X_train_s, y_train)
logit_proba = logit.predict_proba(X_test_s)[:, 1]
logit_pred = logit.predict(X_test_s)
print("\nLogistic Regression:")
print("AUC:", roc_auc_score(y_test, logit_proba))
print("precision:", precision_score(y_test, logit_pred), "recall:", recall_score(y_test, logit_pred))
print("coefficients:", dict(zip(feat_cols, logit.coef_[0])))

rf = RandomForestClassifier(n_estimators=300, max_depth=6, min_samples_leaf=20, random_state=42, class_weight="balanced")
rf.fit(X_train, y_train)
rf_proba = rf.predict_proba(X_test)[:, 1]
rf_pred = rf.predict(X_test)
print("\nRandom Forest:")
print("AUC:", roc_auc_score(y_test, rf_proba))
print("precision:", precision_score(y_test, rf_pred), "recall:", recall_score(y_test, rf_pred))
print("feature importances:", dict(zip(feat_cols, rf.feature_importances_)))

# --- CLV via lifetimes (BG/NBD + Gamma-Gamma), fit on FULL clean history ---
summary = summary_data_from_transaction_data(
    d, "Customer ID", "InvoiceDate", monetary_value_col="Revenue", observation_period_end=max_date
)
print("\nlifetimes summary shape:", summary.shape)
repeat = summary[summary.frequency > 0]
print("customers usable for gamma-gamma (frequency>0):", len(repeat))

bgf = BetaGeoFitter(penalizer_coef=0.01)
bgf.fit(summary["frequency"], summary["recency"], summary["T"])
print("\nBG/NBD fitted, params:", bgf.params_)

ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(repeat["frequency"], repeat["monetary_value"])
print("Gamma-Gamma fitted, params:", ggf.params_)

clv = ggf.customer_lifetime_value(
    bgf, repeat["frequency"], repeat["recency"], repeat["T"], repeat["monetary_value"],
    time=12, freq="D", discount_rate=0.01
)
print("\nCLV (12-month) stats:")
print(clv.describe())

clv_df = clv.rename("clv_12m").to_frame().merge(
    rfm[["Customer ID", "segment", "churn"]], left_index=True, right_on="Customer ID", how="left"
)
print("\nCLV by segment (mean, median):")
print(clv_df.groupby("segment").clv_12m.agg(["mean", "median", "count"]).sort_values("mean", ascending=False))

# save everything needed for the notebook / charts
rfm.to_pickle("data/rfm.pkl")
model_df.to_pickle("data/model_df.pkl")
clv_df.to_pickle("data/clv_df.pkl")
summary.to_pickle("data/lifetimes_summary.pkl")
import pickle
with open("data/models.pkl", "wb") as f:
    pickle.dump({"logit": logit, "rf": rf, "scaler": scaler, "feat_cols": feat_cols,
                 "X_test": X_test, "y_test": y_test, "logit_proba": logit_proba, "rf_proba": rf_proba}, f)
print("\nsaved all intermediate artifacts.")
