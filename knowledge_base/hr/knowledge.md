# HR Knowledge Base

## Domain: HR (Human Resources)

## 1. Core Metrics & KPIs

### Workforce
- **Headcount**: Total employees. chart=bar x=department y=headcount
- **Headcount by Department**: chart=bar x=department y=headcount orientation=h
- **Remote vs Onsite**: chart=pie names=work_type values=count

### Recruitment
- **Time to Hire**: chart=kpi or line x=month y=time_to_hire aggregation=mean
- **Cost per Hire**: chart=kpi value_column=cost_per_hire aggregation=mean prefix=$
- **Offer Acceptance Rate**: chart=kpi suffix=%
- **Hiring Funnel**: chart=funnel stages=[Applied,Screened,Interviewed,Offered,Hired]
- **Source of Hire**: chart=pie names=source values=count

### Retention & Attrition
- **Turnover Rate**: chart=line x=month y=turnover_rate or chart=kpi suffix=%
- **Attrition by Department**: chart=bar x=department y=turnover_rate orientation=h
- **Retention Rate**: chart=kpi or gauge suffix=%

### Performance
- **Performance Rating Distribution**: chart=bar x=rating y=count
- **Goal Completion Rate**: chart=kpi or gauge suffix=%
- **Training Completion**: chart=kpi suffix=%

### Compensation
- **Avg Salary by Department**: chart=bar x=department y=avg_salary orientation=h
- **Pay Equity**: chart=bar x=gender y=avg_salary barmode=group

### Engagement
- **Engagement Score**: chart=gauge or kpi value_column=engagement_score aggregation=mean
- **Absenteeism Rate**: chart=line x=month y=absenteeism_rate

## 2. Chart Type Mapping

| User Says | chart_type | x_column | y_column | notes |
|---|---|---|---|---|
| headcount by department | bar | department | headcount | orientation=h |
| turnover trend | line | month | turnover_rate | |
| hiring funnel | funnel | stage | count | |
| salary by department | bar | department | avg_salary | orientation=h |
| performance ratings | bar | rating | count | |
| source of hire | pie | source | count | |
| engagement score | gauge | | engagement_score | aggregation=mean |
| attrition by team | bar | department | turnover_rate | orientation=h |
| remote vs onsite | pie | work_type | count | |
| tenure distribution | histogram | tenure | | |

## 3. Dashboard Templates

### HR Overview
kpi_cards: [headcount/count, turnover_rate/mean/%, engagement_score/mean, open_roles/sum]
charts: [bar(department,headcount orientation=h), line(month,hires), pie(department,headcount)]

### Recruitment Dashboard
kpi_cards: [open_roles/sum, hires/sum, time_to_hire/mean]
charts: [funnel(stage,count), pie(source,count), line(month,hires)]

### Retention Dashboard
kpi_cards: [turnover_rate/mean/%, headcount/count]
charts: [bar(department,turnover_rate orientation=h), line(month,turnover_rate)]

## 4. Column Aliases
department = department, team, division, business_unit, group
headcount = headcount, employees, count, staff_count, employee_count
turnover = turnover_rate, attrition_rate, churn_rate
salary = salary, compensation, base_pay, annual_pay, avg_salary
engagement = engagement_score, score, satisfaction
hires = hires, new_hires, hired_count

## 5. Examples

Prompt: "show headcount by department"
→ {chart_type: bar, x_column: department, y_column: headcount, orientation: h, title: Headcount by Department}

Prompt: "HR turnover analysis"
→ kpi_cards=[turnover_rate mean %, headcount count] charts=[bar(department,turnover_rate orientation=h), line(month,turnover_rate)]

Prompt: "hiring funnel"
→ {chart_type: funnel, x_column: stage, y_column: count, title: Hiring Funnel}
