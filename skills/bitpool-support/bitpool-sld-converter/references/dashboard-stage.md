# Stage 2: build the dashboard

Optional. Offer it after the drawing is handed over. If the user says no, stop there.

## 1. Ask two things

- **The dashboard name.** Free text. Suggest the board name (`MSB-1A`) as a default.
- **Which Bitpool connector.** Find the candidates live with `tool_search` ("bitpool dashboard"
  and "bitpool streams"). A Bitpool connector is an MCP server whose tool names carry its server
  name (`bitpool-[name]`) ahead of the tool. Only offer a connector that has all of
  `create_dashboard`, `add_widget`, `get_pools`, `get_streams` and `validate_dashboard`; some
  Bitpool connectors only carry scheduler tools. Offer them by name with `clarify`. If none
  qualify, check `manage_connections` for one that isn't connected yet; if there still is none, say
  so plainly and stop.

## 2. Read the connector's own guide

Call `get_dashboard_configuration_guide` once, then
`get_widget_type_details("imagefreeformwidget")`. The shapes are strict; the guide wins over this
page if they ever disagree. Call `get_session` if the connector has it, to name the organisation in
the confirmation.

## 3. Pick the site's pools

Streams live in pools, and an organisation can have dozens. Don't search them all.

1. Call `get_pools` (page through with `skip` if `TotalCount` is over 20). Suggest the pools whose
   names look like this building's site, plus the electrical / EMS / power-meter pools first.
2. Ask the user which pools to search. Allow more than one.
3. If unsure, test one known label from the screenshot against each suggested pool and keep the
   pools that return a hit.

## 4. Find one active power stream per meter

Search every label from `[board]-meters.json`, main meters and branch meters alike, in each chosen
pool:

```
get_streams(poolKey, search="[label]", take=100)
```

The search is a substring match on one term: `"TDB-L07-A-L"` works, `"TDB-L07-A-L ACTIVE_POWER"`
returns nothing. Search the label alone and filter the results yourself.

**A stream matches a meter when all of these hold:**

1. The label appears in the stream name as a whole token, bounded by spaces, `_`, `/` or the ends of
   the name. `TDB-L07-A-L` must not match `TDB-L07-A-L2`.
2. The point part of the name, after the label and any device number, is total active power.
   Accept these, in this order of preference: `ACTIVE_POWER`, `ACTIVE_POWER_TOTAL`,
   `TOTAL_ACTIVE_POWER`, `KW_TOTAL`, `TOTAL_KW`, `KW`, `Active Power`, `Real Power Total`.
3. Reject phase and derived values: anything ending `_A`, `_B`, `_C`, `_L1`–`_L3`, or containing
   `AVERAGE`, `MAX_DEMAND`, `DEMAND`, `REACTIVE`, `APPARENT`, `ENERGY` or `FACTOR`.
4. `DataType` is `Double`.

Example from a site's EMS pool. For label `TDB-L07-A-L`,
`SITE_BOX_3_EMS FD-107201 TDB-L07-A-L 101151 ACTIVE_POWER` is the match. Its siblings
`ACTIVE_POWER_A`, `ACTIVE_POWER_AVERAGE_2`, `ACTIVE_POWER_MAX_DEMAND_2` and `APPARENT_POWER` are
not.

**If a label with spaces or slashes finds nothing** (`LIFT 15 CARPARK LIFT`,
`SPRINKLER/BOOSTER PUMP-1`), retry with spaces as `_`, then as `-`, then with `/` as `_`. Stop at
the first variant that gives a match under the rules above.

**Exactly one stream per meter.** If more than one stream qualifies, take the one higher in the
preference list. On a tie (the same label under two devices), take the most recently updated
(`LastUpdate`) and flag it in the confirmation. If nothing qualifies, the meter is unmatched. Leave
it off and list it; never fall back to a near miss. Flag any matched stream whose `LastUpdate` is
more than 24 hours old as possibly offline, but still attach it.

## 5. Confirm before writing

Show, in one message:

- The dashboard name, the connector, the organisation, and that it goes at the root level.
- One table of matched meters: label, stream name, last update.
- The unmatched labels.
- Any flags: ties, stale streams.

Also run `search_dashboards(name)`. If a dashboard with that name already exists, say so and ask
whether to use a different name. Create nothing until the user says go.

## 6. Create it

1. `create_dashboard(name="[name]", scope="Organisation")`, with **no `parentId`**, so it lands at
   the root.
2. `add_widget` on the new dashboard:
   - `widgetType`: `imagefreeformwidget`
   - `title`: the dashboard name
   - `size`: `{"size":12,"sizeSM":12,"sizeMD":12,"sizeLG":12,"sizeXL":12}` (100% width at every
     breakpoint; the type's default is narrower)
   - `streamKeys`: `[{"streamKey":"…","label":"[meter label]"}, …]`, one per matched meter, main
     meters first, then branch meters in the order of `meters.json`.
   - Leave `widgetImageSrc` empty for now; step 7 attaches the image.
3. `validate_dashboard`. Fix any error it reports before handing over.

## 7. Image and point displays

The connector can't upload an image and, as of writing, has no setting for where each point display
sits. So this step is part guided, part automatic.

**The image.** `widgetImageSrc` must be a URL from the organisation's Graphic Library, which the
connector can search but not add to.

1. Tell the user to open the Graphic Library in Bitpool, upload `[board]-single-line.png`, and say
   when it's done. Give the file's full path so they can find it.
2. Look it up: `get_image_gallery(search="[board]-single-line")`. Take the match whose name is that
   file. If there are several, ask which; if none, ask the user to check the upload finished.
3. Attach it: `update_widget(dashboardId, widgetGuid, patch={"advancedWidgetSettings":
   {"widgetImageSrc":"[gallery url]"}})`. The patch merges, so the other settings stay. Use the url
   exactly as the gallery returned it.

**The point displays.** Call `get_widget_type_details("imagefreeformwidget")` again and look for a
setting that stores each stream's position on the image: a per-stream `x` / `y` / `left` / `top` /
`position` field, or a widget-level list of positions.

- **If there is one**, write every matched meter's `pct_x` and `pct_y` from `[board]-meters.json`
  into it with `update_widget`, keeping the shape the type details give. Call `get_dashboard`
  afterwards and check the positions saved. Never invent a field name: if the details don't name
  one, treat it as absent.
- **If there isn't one** (the case when this was written), say plainly that placing the displays is
  manual, and walk the user through it: open the dashboard, turn on Edit, and drag each point
  display onto its dot. For a reference, `[board]-meters.json` has every meter's `pct_x` / `pct_y`
  (percent across and down the image) and `px` / `py` (pixels).

## 8. Hand over

Give the dashboard link from the tool result, the number of streams attached out of the meters on
the drawing, whether the image is attached, and the unmatched list. Then say which of the two
placement paths applied and, for the manual one, what is left for the user to do.
