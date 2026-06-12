# Project Management Knowledge Base

## Domain: Project Management

## 1. Core Metrics & KPIs

### Schedule
- **Completion %**: chart=kpi or gauge value_column=completion aggregation=mean suffix=%
- **Tasks by Status**: chart=pie names=status values=count
- **Overdue Tasks**: chart=kpi value_column=overdue aggregation=count
- **Sprint Velocity**: chart=bar x=week y=velocity or chart=line x=week y=velocity
- **Days Until Deadline**: chart=kpi

### Budget
- **Budget Utilization**: chart=kpi or gauge suffix=%
- **Budget vs Actual**: chart=bar x=task y=budget barmode=group (add actual)
- **Budget Burn Rate**: chart=line x=week y=spent

### Tasks & Workload
- **Tasks by Assignee**: chart=bar x=assignee y=count orientation=h
- **Tasks by Priority**: chart=pie names=priority values=count or chart=bar x=priority y=count
- **Story Points per Person**: chart=bar x=assignee y=story_points orientation=h
- **Task Status Breakdown**: chart=pie names=status values=count
- **Backlog size**: chart=kpi value_column=story_points aggregation=sum

### Timeline
- **Gantt chart**: chart=gantt x_column=task color_column=status
- **Milestone progress**: chart=bar x=milestone y=completion

### Risk & Issues
- **Open Issues**: chart=kpi value_column=issues aggregation=count
- **Issues by Priority**: chart=pie names=priority values=count
- **Risk by Severity**: chart=bar x=severity y=count

## 2. Chart Type Mapping

| User Says | chart_type | x_column | y_column | notes |
|---|---|---|---|---|
| task status | pie | status | count | |
| tasks by assignee | bar | assignee | story_points | orientation=h |
| sprint velocity | bar | week | velocity | |
| burndown | line | week | remaining | |
| budget vs actual | bar | task | budget | barmode=group |
| timeline | gantt | task | | color=status |
| issues by priority | pie | priority | count | |
| workload per person | bar | assignee | story_points | orientation=h |
| completion rate | gauge | | completion | aggregation=mean |
| overdue tasks | kpi | | overdue | aggregation=count |

## 3. Dashboard Templates

### Project Overview
kpi_cards: [completion/mean/%, story_points/sum, velocity/mean]
charts: [pie(status,count), bar(assignee,story_points orientation=h), line(week,velocity)]

### Sprint Dashboard
kpi_cards: [velocity/mean, story_points/sum, completion/mean/%]
charts: [bar(week,velocity), pie(status,count), bar(assignee,story_points orientation=h)]

### Workload Dashboard
kpi_cards: [story_points/sum, headcount/count]
charts: [bar(assignee,story_points orientation=h), pie(priority,count), pie(status,count)]

## 4. Column Aliases
task = task, task_name, issue, ticket, story, feature
status = status, state, task_status, stage
assignee = assignee, assigned_to, owner, responsible, person
priority = priority, severity, urgency, importance
story_points = story_points, points, effort, estimate, size
completion = completion, completion_pct, progress, percent_done
velocity = velocity, throughput, completed_points
week = week, sprint, iteration, period

## 5. Examples

Prompt: "show tasks by status"
→ {chart_type: pie, x_column: status, y_column: count, title: Task Status Breakdown}

Prompt: "who has the most work"
→ {chart_type: bar, x_column: assignee, y_column: story_points, orientation: h, title: Workload by Assignee}

Prompt: "project overview dashboard"
→ kpi_cards=[completion mean %, story_points sum, velocity mean] charts=[pie(status,count), bar(assignee,story_points), line(week,velocity)]

Prompt: "show me a gantt chart"
→ {chart_type: gantt, x_column: task, color_column: status, title: Project Timeline}
