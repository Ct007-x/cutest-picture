# Quantile forecaster for Polymarket's "Next CEO of NVIDIA?" event prices (standard library only, deterministic).
# For each market it builds the empirical distribution of h-minute price changes from the market's own recent
# history (recency weighted), blends it with a pooled, volatility-scaled distribution, and writes five quantiles
# for each of the next 240 minutes.
import json, math, os, glob

QS = [0.05, 0.25, 0.5, 0.75, 0.95]
H = 240
HGRID = [1, 2, 3, 5, 8, 12, 18, 27, 40, 60, 90, 130, 180, 240]

# tunable parameters
P = {
    "halflife": 400.0,   # minutes, recency weight of history windows
    "own_w": 0.3,        # weight of the market's own change distribution vs pooled
    "widen": 0.75,        # overall spread multiplier
    "floor_sig": 0.0006,  # minimum per-sqrt-minute sigma (price units)
}


def wquantiles(vals, wts, qs):
    idx = sorted(range(len(vals)), key=lambda i: vals[i])
    tot = sum(wts)
    out = []
    cum = 0.0
    k = 0
    cums = []
    for i in idx:
        cum += wts[i]
        cums.append(cum)
    for q in qs:
        target = q * tot
        while k < len(idx) - 1 and cums[k] < target:
            k += 1
        out.append(vals[idx[k]])
    return out


def deltas(prices, h, halflife):
    n = len(prices)
    if n <= h + 1:
        return None, None
    vals, wts = [], []
    lam = math.log(2) / halflife
    stride = max(1, h // 4)
    start = (n - 1 - h) % stride
    for i in range(start, n - h, stride):
        vals.append(prices[i + h] - prices[i])
        wts.append(math.exp(-lam * (n - 1 - (i + h))))
    return vals, wts


def recent_sigma(prices):
    n = len(prices)
    w = prices[max(0, n - 721):]
    if len(w) < 30:
        w = prices
    s = 0.0
    c = 0
    for a, b in zip(w, w[1:]):
        s += (b - a) ** 2
        c += 1
    if c == 0:
        return P["floor_sig"]
    return max(P["floor_sig"], math.sqrt(s / c))


def forecast_market(prices, pooled):
    x = prices[-1]
    sig = recent_sigma(prices)
    zs = [-1.644854, -0.67449, 0.0, 0.67449, 1.644854]
    grid = {}
    for h in HGRID:
        own, wts = deltas(prices, h, P["halflife"])
        # parametric fallback / pooled component: normalised pooled quantiles times sigma sqrt(h)
        pooled_q = [pooled[h][j] * sig * math.sqrt(h) for j in range(5)]
        if own is None or len(own) < 20:
            q = pooled_q
        else:
            oq = wquantiles(own, wts, QS)
            wo = P["own_w"]
            q = [wo * oq[j] + (1 - wo) * pooled_q[j] for j in range(5)]
        grid[h] = [v * P["widen"] for v in q]
    rows = []
    for h in range(1, H + 1):
        # interpolate between grid horizons
        lo = max(g for g in HGRID if g <= h)
        hi = min(g for g in HGRID if g >= h)
        if lo == hi:
            q = grid[lo]
        else:
            t = (h - lo) / (hi - lo)
            q = [grid[lo][j] * (1 - t) + grid[hi][j] * t for j in range(5)]
        row = [min(1.0, max(0.0, x + d)) for d in q]
        for j in range(1, 5):
            if row[j] < row[j - 1]:
                row[j] = row[j - 1]
        rows.append([round(v, 6) for v in row])
    return rows


def build_pooled(markets):
    """Pooled normalised h-step change quantiles: change / (sigma*sqrt(h)), across markets with enough history."""
    pooled = {}
    for h in HGRID:
        vals, wts = [], []
        for prices in markets:
            if len(prices) < h + 60:
                continue
            sig = recent_sigma(prices)
            d, w = deltas(prices, h, P["halflife"])
            if d is None:
                continue
            sc = sig * math.sqrt(h)
            vals.extend(v / sc for v in d)
            wts.extend(w)
        if len(vals) >= 50:
            pooled[h] = wquantiles(vals, wts, QS)
        else:
            pooled[h] = [z * 1.0 for z in (-1.644854, -0.67449, 0.0, 0.67449, 1.644854)]
    return pooled


def forecast_case(case):
    series = [m["prices"] for m in case["markets"]]
    pooled = build_pooled(series)
    return {"forecasts": [{"id": m["id"], "q": forecast_market(m["prices"], pooled)} for m in case["markets"]]}


def main():
    indir = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    for path in sorted(glob.glob(os.path.join(indir, "*.in"))):
        with open(path, encoding="utf-8") as f:
            case = json.load(f)
        res = forecast_case(case)
        name = os.path.basename(path)[:-3] + ".out"
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as f:
            json.dump(res, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
