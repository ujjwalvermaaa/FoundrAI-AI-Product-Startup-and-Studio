# Unit Economics for Startups and SaaS Businesses

## Why Unit Economics Matter

Unit economics answer the fundamental question: "Do we make money on each customer?" A startup can grow fast and still be destroying value if its unit economics are negative. Investors care about unit economics because they predict whether the business can ever be profitable at scale.

The core test: Can you acquire a customer (CAC) for significantly less than the value they generate over their lifetime (LTV)?

## Customer Acquisition Cost (CAC)

**CAC** = Total sales and marketing spend in a period ÷ Number of new customers acquired in that period

Include all costs: salaries of sales and marketing teams, ad spend, agency fees, marketing tools, sponsorships, events, and a pro-rated share of overhead attributable to acquisition.

**Blended vs. Paid CAC**: Blended CAC includes all customers (organic + paid). Paid CAC includes only customers from paid channels. Paid CAC is always higher — if your blended CAC looks good but paid CAC is terrible, you're relying on organic that may not scale.

**CAC payback period** = CAC ÷ Monthly Gross Profit per Customer

This tells you how many months before a customer pays back their acquisition cost. For SaaS:
- < 12 months: excellent
- 12–18 months: acceptable for B2B
- > 24 months: capital-intensive, requires significant funding to scale

## Lifetime Value (LTV)

**LTV** = Average Revenue per Account (ARPA) × Gross Margin % ÷ Churn Rate

Or equivalently: Gross Profit per month × Average customer lifespan

**Example**: ARPA = $200/month, gross margin = 75%, monthly churn = 2%
- LTV = $200 × 0.75 ÷ 0.02 = $7,500

### LTV assumptions to watch
- LTV calculations assume steady-state churn — if churn is improving, LTV is understated
- Include expansion revenue (upsells, seat additions) in ARPA for net LTV
- Discount future cash flows for a more conservative estimate (use a 10-20% annual discount rate)

## LTV:CAC Ratio

The LTV:CAC ratio is the single most important unit economics metric for SaaS.

| LTV:CAC | Signal |
|---------|--------|
| < 1x    | Destroying value — stop scaling |
| 1x–3x   | Break even or marginal — investigate CAC breakdown |
| 3x–5x   | Healthy — scale with confidence |
| > 5x    | Consider investing more in growth (may be leaving money on the table) |

**Target**: 3:1 or better for venture-scale SaaS. Below 1:1 means you lose money on every customer.

Note: LTV:CAC in isolation is incomplete. A 3:1 ratio with a 36-month payback period is far more capital-intensive than 3:1 with a 6-month payback.

## Gross Margin and Contribution Margin

**Gross Margin** = (Revenue − Cost of Goods Sold) ÷ Revenue

For SaaS, COGS includes: hosting/infrastructure, third-party APIs charged per usage, customer support costs, and data costs. It excludes R&D, sales, and marketing.

Healthy SaaS gross margins: 70-85%. Below 60% signals infrastructure-heavy architecture or high human service costs.

**Contribution Margin** = Revenue − Variable Costs

Variable costs are those that scale directly with revenue: payment processing fees, per-transaction API costs, variable support costs. Contribution margin tells you how much each additional dollar of revenue contributes to covering fixed costs. A positive contribution margin means you should want more customers even before you're profitable.

## Churn Rate

**Monthly churn rate** = Customers lost in the month ÷ Customers at start of month

**Annual churn rate** ≈ 1 − (1 − monthly churn)^12

Churn benchmarks for SaaS:
- SMB-focused: 3-5% monthly (significant — a business with 5% monthly churn loses ~46% of its base per year)
- Mid-market: 1-2% monthly
- Enterprise: 0.5-1% monthly (annual contracts, higher switching costs)

### Net Revenue Retention (NRR)

NRR = (Starting MRR + Expansion MRR − Contraction MRR − Churned MRR) ÷ Starting MRR

NRR > 100% means existing customers are growing faster than churn. This is the holy grail — your revenue base grows even if you acquire zero new customers.

- NRR > 130%: world-class (Snowflake, Twilio territory)
- NRR > 110%: strong for enterprise SaaS
- NRR > 100%: healthy
- NRR < 100%: churn is a real problem

## MRR and ARR

**MRR (Monthly Recurring Revenue)** = Sum of all monthly subscription amounts

**ARR (Annual Recurring Revenue)** = MRR × 12

Track MRR components:
- **New MRR**: From new customers this month
- **Expansion MRR**: Upgrades and upsells from existing customers
- **Contraction MRR**: Downgrades
- **Churned MRR**: Lost to cancellations
- **Net New MRR** = New + Expansion − Contraction − Churned

ARR is a snapshot metric. It should not be confused with actual annual revenue recognized (which depends on timing of contracts and payments).

## Unit Economics for Different Business Models

### SaaS/Subscription
Primary metrics: CAC, LTV, churn, NRR, gross margin. The model improves with scale as COGS stays relatively fixed while revenue grows.

### Marketplace
Track: take rate, GMV, CAC for both supply and demand sides, liquidity (% of supply that transacts). Unit economics often harder in early stages due to chicken-and-egg problems.

### Transactional / Usage-Based
CAC still applies, but LTV is harder to model without consumption history. Use cohort revenue curves to project LTV over time.

## Red Flags in Unit Economics

- **Payback > 24 months** and no path to shortening it
- **NRR < 90%** — customers are shrinking or leaving faster than they grow
- **Gross margin declining** as you scale (suggests cost structure is broken)
- **CAC increasing** quarter-over-quarter while LTV stays flat (saturating easy channels)
- **Blended and paid CAC diverging** — organic is slowing, paid is scaling
