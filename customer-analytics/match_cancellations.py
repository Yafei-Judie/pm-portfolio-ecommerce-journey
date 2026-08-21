"""
Match each cancellation line (Invoice starting with 'C') back to the original
purchase line it reverses, by (Customer ID, StockCode, |Quantity|), picking the
nearest prior unused purchase. Standard "drop C-invoices only" cleaning misses
this: it removes the cancellation record but leaves the original order in the
"clean" data, which is wrong when the order never actually shipped.
"""
import pandas as pd
import pickle
from collections import defaultdict
from bisect import insort, bisect_left

df = pd.read_pickle("data/raw_combined.pkl")
df = df.dropna(subset=["Customer ID"]).copy()
df["Customer ID"] = df["Customer ID"].astype(int)

is_cancel = df.Invoice.astype(str).str.startswith("C")
cancels = df[is_cancel].copy()
positives = df[~is_cancel].copy()
print("cancel lines:", len(cancels), "positive lines:", len(positives))

# bucket positives by (customer, stockcode, qty) -> sorted list of (timestamp, index)
buckets = defaultdict(list)
for idx, cid, code, qty, dt in zip(positives.index, positives["Customer ID"], positives.StockCode,
                                     positives.Quantity, positives.InvoiceDate):
    key = (cid, code, qty)
    insort(buckets[key], (dt.value, idx))

matched_idx = []
unmatched = 0
for idx, cid, code, qty, dt in zip(cancels.index, cancels["Customer ID"], cancels.StockCode,
                                     cancels.Quantity.abs(), cancels.InvoiceDate):
    key = (cid, code, qty)
    lst = buckets.get(key)
    if not lst:
        unmatched += 1
        continue
    pos = bisect_left(lst, (dt.value, -1))
    if pos == 0:
        unmatched += 1
        continue
    # nearest prior purchase not yet used
    ts, orig_idx = lst.pop(pos - 1)
    matched_idx.append(orig_idx)

print("matched cancel->original pairs:", len(matched_idx), "unmatched cancels:", unmatched)
matched_set = set(matched_idx)
removed_revenue = positives.loc[matched_idx].eval("Quantity*Price").sum()
print("positive-side revenue removed by matching:", removed_revenue)
print("customer 16446 / stockcode 23843 order matched?:", any(
    positives.loc[i, "Customer ID"] == 16446 and positives.loc[i, "StockCode"] == "23843" for i in matched_idx
))

with open("data/matched_cancel_idx.pkl", "wb") as f:
    pickle.dump(matched_set, f)
print("saved", len(matched_set), "matched indices")
