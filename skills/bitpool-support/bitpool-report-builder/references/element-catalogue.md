# Report element catalogue

The **Add an element** modal is a flat, searchable grid of cards — no groups, unlike the dashboard
widget picker. Each card shows a title and a one-line description. Use the **Search** box when you know
the name.

The list below is what was confirmed present. The catalogue is backed by the **Elements** tab in Report
Manager and orgs can extend it, so **always scroll the real modal** rather than assuming this list is
complete. If the user names something not here, search for it before saying it doesn't exist.

## Charts

| Element | Description in-app | Reach for it when |
|---|---|---|
| **Stacked Chart** | Visualise data with a customisable stacked chart to reveal trends, patterns, and insights. | Composition over time — several streams summing to a total per period. |
| **Horizontal Stacked Chart** | Same, rotated. | Long category labels, or ranked comparison where horizontal bars read better. Supports mixed series types per stream (Column / Line / Area / Scatter). |
| **Polar Chart** | Visualise data with a polar chart to reveal trends, patterns, and insights. | Cyclical data — load shape by hour of day, wind direction. |
| **Pie Chart** | Visualise data with a pie chart to reveal trends, patterns, and insights. | Share-of-total for a handful of categories in one period. Not for time series. |
| **Baseline Compare Chart** | Compare selected period of a time-series data stream against previous period of same data stream. | "Is this month better than last month?" for a single stream. |
| **Period Compare Chart** | Compare current period data with previous period data. | Same question across several streams. |
| **String chart** | Visualise categorical data with a customisable chart to reveal distributions, frequencies, and qualitative insights. | Status / state / mode points rather than numeric ones. Has a **State Name Converters** section to map raw values to readable names. |

## Tables

| Element | Description in-app | Reach for it when |
|---|---|---|
| **Table** | Organize and display data in a customizable table for easy comparison and analysis. | The general-purpose table. |
| **Table – Scoreboard** | Organize and display data in a customizable scoreboard-style table for easy metric tracking and performance visualization. | KPI rollup — one row per metric, current value front and centre. |
| **Table – Multi Column Matrix** | Organize and display data in a customizable table for easy comparison and analysis. In the data source, name the streams as followed: name you want the row to be called in the table \| matching name listed in the "Column Headers". Please use the "\|" to separate. | Cross-tab, e.g. sites × metrics. **Note the pipe convention** — the stream Label must be `RowName\|ColumnHeader`, so plan Labels in the Data Source modal accordingly. |
| **Total Table** | Organize and display total values in a customizable table for easy comparison and analysis. | Period totals per stream, no time breakdown. |
| **Consumption Table** | Display detailed consumption data in a table format. | Metered consumption with interval detail. |

## Tariff and cost

| Element | Description in-app | Reach for it when |
|---|---|---|
| **Tariff Cost – Summary Card** | Displays tariff cost grand total with configurable tax and multiple stream data for multiple tariff selection. | A single headline cost figure at the top of a billing report. |
| **Tariff Cost – Summary Table** | Displays the group totals of multiple Commodities with the tariff costs into a table with configurable tax and grand total. | Cost broken down by commodity (electricity / gas / water). |
| **Tariff Cost – Table** | Displays meter opening/closing readings and an itemised tariff cost breakdown table with configurable tax and grand total. | A full invoice-style breakdown with meter readings. |

All three take tax configuration and multiple tariffs — get the tariff and tax treatment from the user
rather than accepting defaults, since these numbers get billed on.

## Data quality

| Element | Description in-app | Reach for it when |
|---|---|---|
| **Data Health** | — | Overall health of the streams in the report. |
| **Basic Leaderboard with Data Completeness, Missing Samples and stream links** | This element displays a table of the current stream values, along with the completeness of each stream's dataset during the specified period. Please note that in order to accurately reflect data completeness (the amount of samples with non-null values), please ensure you set the aggregation period to be the same as the expected sample period of the data. | Commissioning and monitoring reports where "is the data actually arriving?" is the point. **Its caveat is load-bearing**: set the aggregation period to the stream's real sample period or the completeness percentage is meaningless. |
| **Condition Count – Logical AND – Multiple Streams** | Counts the occurrence of a specified data condition using AND logic of multiple streams. | Rule-based counting — "hours where zone temp > 24 AND occupancy = true". |

## Energy

| Element | Description in-app | Reach for it when |
|---|---|---|
| **Energy Flowchart** | Create a visual representation of the energy flow between the energy grid, solar and load of a building. | Solar/grid/load sites. Renders GRID · SOLAR · LOAD nodes with directional arrows and a **Net** figure. Shows `N/A` on any leg whose stream isn't mapped — an `N/A` means an unmapped or empty stream, so check every leg before shipping. |

## Text and context

| Element | Description in-app | Reach for it when |
|---|---|---|
| **Markdown** | Add formatted text using Markdown syntax for customizable styling and layout. | Narrative — executive summary, methodology note, caveats. A report full of charts and no words is rarely what the recipient wanted; propose one of these at the top. |
| **Date Range** | Displays the start and end dates of the data period, showing the range of dates covered in the report. | Every scheduled report. Without it the reader cannot tell which period a PDF covers. |
| **Date** | Displays the current date, allowing users to view the current date at the time of report generation. | "Generated on" stamps. Note this is *generation* date, not the data period — pair it with Date Range, don't substitute it. |

## Choosing

- **A time series across a period** → Stacked Chart (or Horizontal Stacked Chart for long labels).
- **This period vs last** → Baseline Compare (one stream) or Period Compare (several).
- **Composition of a total** → Pie Chart for one period, Stacked Chart over time.
- **Numbers people will read off** → a table, not a chart. Charts are for shape; tables are for values.
- **Money** → the Tariff Cost family. Never hand-build cost in a plain table.
- **"Is our data any good?"** → Basic Leaderboard with Data Completeness, plus Data Health.
- **States/modes rather than numbers** → String chart with State Name Converters.
- **Solar site** → Energy Flowchart, then the detail charts beneath it.

Every report should carry a **Date Range** element and at least one **Markdown** block of context.
Those two are what make a PDF readable by someone who wasn't in the conversation.
