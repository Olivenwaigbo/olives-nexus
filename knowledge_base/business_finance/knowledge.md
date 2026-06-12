# Business & Finance Knowledge Base

## Domain: Business & Finance

## 1. Core Metrics & KPIs

### Revenue Metrics
- **Total Revenue**: Sum of all income. Chart: Line (trend), Bar (by category)
- **Revenue by Region**: x=region y=revenue chart=bar orientation=h
- **Revenue by Product**: x=product y=revenue chart=bar orientation=h
- **MRR**: Monthly Recurring Revenue. Chart: line x=month y=revenue

### Profit Metrics
- **Gross Profit**: Revenue minus cost. Chart: bar or kpi
- **Gross Margin %**: (profit/revenue)*100. Chart: kpi or line
- **Net Profit Margin**: chart=kpi or line x=month y=profit

### Cost & Sales
- **CAC** Customer Acquisition Cost: chart=kpi value_column=cac aggregation=mean
- **Churn Rate**: chart=line x=month y=churn_rate
- **Win Rate**: chart=gauge or kpi
- **Sales Funnel**: chart=funnel stages=[Lead,Prospect,Qualified,Won]

## 2. Chart Type Mapping

| User Says | chart_type | x_column | y_column | notes |
|---|---|---|---|---|
| revenue over time | line | month | revenue | |
| revenue by region | bar | region | revenue | orientation=h if many regions |
| compare products | bar | product | revenue | orientation=h |
| expense breakdown | pie | category | cost | |
| profit trend | line | month | profit | |
| budget vs actual | bar | category | budget | barmode=group add actual |
| sales funnel | funnel | stage | count | |
| market share | pie | product | revenue | |
| KPI overview | kpi | | revenue | aggregation=sum |

## 3. Dashboard Templates

### Revenue Overview
kpi_cards: [revenue/sum/$, profit/sum/$, cac/mean/$, gross_margin/mean/%]
charts: [line(month,revenue), bar(region,revenue orientation=h), pie(product,cost)]

### Sales Dashboard
kpi_cards: [revenue/sum, win_rate/mean/%, cac/mean/$]
charts: [funnel(stage,count), line(month,revenue), bar(product,revenue orientation=h)]

## 4. Column Aliases
revenue = revenue, sales, income, total_revenue, amount
profit = profit, net_income, earnings, margin
cost = cost, expense, cogs, expenditure
month = month, date, period, week, quarter, year
region = region, country, territory, location, geo
product = product, product_name, item, sku, category
customer = customer, client, account

## 5. Examples

Prompt: "show me revenue by region"
→ {chart_type: bar, x_column: region, y_column: revenue, orientation: h, title: Revenue by Region}

Prompt: "monthly profit trend"
→ {chart_type: line, x_column: month, y_column: profit, title: Monthly Profit Trend}

Prompt: "give me a financial overview"
→ kpi_cards=[revenue sum $, profit sum $, cac mean $] charts=[line(month revenue), bar(region revenue), pie(product cost)]
