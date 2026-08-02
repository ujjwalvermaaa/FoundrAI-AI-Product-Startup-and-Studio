# Product Roadmap Guide: From MVP to Scale

## What Is a Product Roadmap?

A product roadmap is a strategic communication tool that conveys the direction of the product over time. It is NOT a feature list, a project plan, or a commitment. A good roadmap answers: "What problem are we solving, for whom, and in what order?"

Roadmaps serve different audiences:
- **Engineering**: Sequence of work to plan capacity and technical decisions
- **Sales/CS**: Near-term capabilities to communicate to prospects and customers
- **Investors**: Evidence of a coherent vision and execution ability
- **Leadership**: Strategic alignment and tradeoff visibility

## Roadmap Frameworks

### Now / Next / Later

The simplest and most effective framework for early-stage teams:

- **Now**: What you're building in the current sprint or quarter (concrete, scoped)
- **Next**: What you're planning for the next quarter (directional, may shift)
- **Later**: What you might build eventually (aspirational, lowest confidence)

Benefits: Forces honest prioritization, avoids fake precision on distant quarters, easy to update as learning happens.

### Opportunity Scoring (Kano-influenced)

Score each potential feature or initiative on:
1. **Importance**: How important is this to customers? (1-10, from survey or interview data)
2. **Satisfaction**: How satisfied are customers with current solutions? (1-10)
3. **Opportunity score** = Importance + (Importance − Satisfaction), capped at 10

Features with high importance and low satisfaction (large unmet needs) score highest. This method surfaces opportunities that customers care about but aren't being served by existing solutions.

## Feature Prioritization Methods

### RICE Scoring

**RICE** = (Reach × Impact × Confidence) ÷ Effort

- **Reach**: How many users will this affect per quarter? Use data (DAUs, segment size)
- **Impact**: Expected impact on goal per user: massive (3), high (2), medium (1), low (0.5), minimal (0.25)
- **Confidence**: How confident are you in the estimates? 100% = proven, 80% = high, 50% = medium
- **Effort**: Person-months to implement

Use RICE when comparing features across different types (acquisition vs. retention vs. engagement). The output is a ranked list, not an absolute truth — use it to structure debate, not end it.

**Example**:
- Feature A: 500 users × 2 impact × 80% confidence ÷ 1 month = 800
- Feature B: 50 users × 3 impact × 60% confidence ÷ 0.5 months = 180

Feature A scores higher despite lower per-user impact due to reach and effort efficiency.

### MoSCoW Prioritization

Categorize features for a given release or milestone:
- **Must have**: Non-negotiable. Without these, the release fails its goal.
- **Should have**: Important but not critical. Include if capacity allows.
- **Could have**: Nice-to-have. Drop first when things slip.
- **Won't have**: Explicitly out of scope for this release. Communicate clearly.

MoSCoW is fast and works well for sprint planning or release scoping. Weakness: it doesn't account for effort, so "must haves" can balloon scope if not monitored.

### Impact vs. Effort Matrix

Quick visual framework for small team triage:
- **High impact, low effort**: Do immediately (quick wins)
- **High impact, high effort**: Plan carefully (major projects)
- **Low impact, low effort**: Do if there's slack capacity
- **Low impact, high effort**: Avoid

## Product Phases: MVP to Scale

### Phase 1: Hypothesis MVP (0-100 users)

**Goal**: Validate that the core problem is real and your solution works.

**What to build**: One job-to-be-done, end-to-end. No admin dashboard, no billing integration, no integrations. Manual processes for everything non-core.

**Success metrics**:
- Activation rate (% who complete the primary action)
- 3-day retention
- Qualitative NPS / "very disappointed" score

**What NOT to build**: Performance optimization, self-serve onboarding, role-based permissions, analytics dashboards, API integrations.

### Phase 2: Retention MVP (100-1,000 users)

**Goal**: Prove that users come back and get ongoing value.

**What to build**: Onboarding flows, core habit loops, notifications/reminders, basic analytics for your team.

**Success metrics**:
- Day-7 and day-30 retention cohorts
- Feature adoption rates
- Support ticket volume per user (should decrease over time)

### Phase 3: Growth MVP (1,000-10,000 users)

**Goal**: Build the acquisition and expansion machinery.

**What to build**: Self-serve signup, referral/viral mechanisms, integrations with adjacent tools, billing and subscription management, in-product upsell flows.

**Success metrics**:
- CAC by channel
- Viral coefficient (k-factor)
- Expansion MRR / NRR

### Phase 4: Scale (10,000+ users)

**Goal**: Operationalize growth and expand market.

**What to build**: Enterprise features (SSO, audit logs, admin controls, SLAs), platform APIs, partner integrations, advanced analytics, performance at scale.

**Success metrics**:
- NRR > 110%
- Gross margin approaching 80%+
- Sales cycle length decreasing

## How to Write User Stories

**Format**: As a [persona], I want to [action], so that [outcome/benefit].

**Rules**:
- One user story = one action toward one outcome
- The "so that" clause is mandatory — it captures the why and prevents over-building
- Stories should be testable: you can verify whether a story is complete

**Example**:
"As a founder building an investor pitch, I want to see a one-page financial summary with key metrics, so that I can share it without manual formatting."

**Acceptance criteria**: Each story needs clear done conditions. Use "Given/When/Then" format:
- Given [context]
- When [action]
- Then [expected result]

**Story sizing**: Break stories down until each can be completed in 1-3 days. If a story takes longer, split it. Large stories introduce planning uncertainty and reduce visibility.

## Metrics Per Phase

| Phase | Primary Metric | Supporting Metrics |
|-------|---------------|-------------------|
| Hypothesis MVP | Activation rate | Qualitative NPS, core action completion |
| Retention MVP | D30 retention | DAU/MAU ratio, feature adoption |
| Growth MVP | CAC, k-factor | Conversion rate, time-to-activate |
| Scale | NRR, ARR growth | Gross margin, LTV:CAC |

## Roadmap Communication Tips

- **Date ranges, not dates**: "Q3" instead of "August 15" — reduces commitment anxiety and allows room for learning
- **Outcomes over features**: "Users can complete onboarding unassisted" vs. "Build onboarding wizard"
- **Mark confidence levels**: Explicit "high / medium / low" confidence signals to stakeholders what's committed vs. directional
- **Review cadence**: Revisit the roadmap at the end of every sprint or at minimum monthly — a roadmap that isn't updated is a liability
