# Widget Catalogue

The **Add Widget** modal opens with a search box, a row of **Widget Group** tiles, and then one titled section per group. Clicking a group tile highlights it and scrolls to that section.

## Widget groups

| Group | What it holds |
|---|---|
| **Data Visualisation** | Heatmaps, gauges — density and single-value visuals |
| **Charting** | Time-series charts. The workhorse group. |
| **Time and Date** | Clocks, date/time readouts, schedule visuals |
| **Display** | Text, HTML/code, image and media panels |
| **Weather** | Weather conditions and forecast panels |
| **Utility** | Utility/tariff and billing-oriented widgets |
| **Infographic** | Composed graphic panels |
| **Command and Control** | Writeable controls — setpoints, switches |

> **Note**
> Only Data Visualisation and Charting were opened in the source recording; the widgets listed below for those two are confirmed by name and description. Treat the other six as verified **group names** with unverified contents — open the group in the app and read the cards rather than guessing at widget names.


## Data Visualisation (confirmed)

| Widget | Use for |
|---|---|
| **Heatmap** | One stream, value density across a time grid — load shape by hour/day |
| **Multi-Stream Heatmap** | The same, compared across several streams |
| **Radial Gauge** | A single current value against a range |

## Charting (confirmed)

| Widget | Description as shown in-app | Reach for it when |
|---|---|---|
| **Basic Chart** | "Use this widget to create a simple column, line or area chart with multiple time-series data." | Default choice for any numeric trend. Series Type per stream lets one widget mix columns and lines. |
| **String Chart** | "Use this for a 'Basic Chart' which uses strings rather than numerical values on the y-axis." | State/mode data — Occupied/Unoccupied, fan stages, enum points |
| **Stacked Chart** | "Use this for a 'Basic Chart' which allows y-axis data to be stacked." | Parts summing to a whole — consumption split by circuit, phase, or tenancy |
| **Peak Demand** | "Find the highest power value within the time-series data stream and compare this with the overall highest value." | Demand-charge conversations, kVA/kW peaks |
| **Baseline Compare** | "Compare selected period of a time-series data stream against previous period of same data stream." | This month vs last month, this year vs last year |
| **Condition Duration** | "Use this condition widget to capture condition based monitoring of any data stream. Ie. fault analysis, people counting, alarms raised." | Time-in-condition — hours in fault, occupancy counts, alarm dwell |
| **Column Range** | (Column-range visual — min/max band per interval) | Daily min/max envelopes, comfort bands |

## Choosing by question

| The user wants to know… | Widget |
|---|---|
| How is consumption trending? | Basic Chart, Column series |
| What's the split between circuits/phases? | Stacked Chart |
| Better or worse than last year? | Baseline Compare |
| What's our worst peak? | Peak Demand |
| How long was it in fault / occupied? | Condition Duration |
| What's the value right now? | Radial Gauge |
| When in the week does load happen? | Heatmap / Multi-Stream Heatmap |
| What mode is the plant in? | String Chart |
| How spread out are daily values? | Column Range |

## Notes

- A widget added but not yet wired shows **"Not Configured! Streams have not been selected."** This is the normal intermediate state.
- Every widget header carries its own **GDRS** toggle and shows the effective range on the right (e.g. "Rolling Month"), so individual widgets can opt out of the dashboard-wide date range.
- Widget cards are cheap to add and cheap to delete — but each one costs a full configuration modal, so agree the widget list with the user before adding rather than experimenting in the app.
