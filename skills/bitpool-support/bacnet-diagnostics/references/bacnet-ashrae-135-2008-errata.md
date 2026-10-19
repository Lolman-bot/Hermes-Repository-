# ASHRAE BACnet Standard 135-2008 — Errata Reference

> **Source:** ANSI/ASHRAE Standard 135-2008 — A Data Communication Protocol for Building Automation and Control Networks
> **Date:** October 25, 2010
> **Total Items:** 85 (including 8 new items 79–85 added since July 20, 2010)
> **Note:** These are formal protocol-level errata from the BACnet standard specification itself — distinct from the network diagnostic alerts in `diagnostics.md`. Items 79–85 were added since the previously published errata sheet dated July 20, 2010.

## Types of Errata in This Appendix

- **Misspellings in text or figures** (e.g., "BACent" → "BACnet", "Reponse" → "Response", "Conveter" → "Converter")
- **Incorrect or missing enumeration values** in ASN.1 productions (BACnetPropertyIdentifier, Error, BACnetPropertyStates, etc.)
- **Document structure errors** (missing Annex entries, incorrect clause numbering, misnumbered pages)
- **Algorithmic errors** (incorrect sign for Low_Diff_Limit, incorrect comparison values in MS/TP token passing)
- **Property conformance errors** (OPTIONAL marked as required or vice versa, in Annex C and property tables)
- **Wording clarifications** (timestamp semantics, hop count handling, deadband description)
- **Missing documentation** (PICS updates, new device profiles, data link options, missing error codes)
- **"read only" → "read-only" consistency fixes** (multiple clauses throughout the standard)

---

---

## Erratum 1 — Clause 21, p.468 — Incorrect pulse-rate enumeration position

**Error:** The position of the pulse-rate enumeration value in BACnetPropertyIdentifier is incorrect.

**Correction:** Moved `pulse-rate (186)` to its proper alphabetic position, removing the duplicate entry that appeared before `priority-array (87)`.

```
BACnetPropertyIdentifier ::= ENUMERATED {
    accepted-modes (175),
    ...
    priority (86),
    priority-array (87),        ← pulse-rate was incorrectly placed here
    ...
    protocol-version (98),
    pulse-rate (186),           ← correct position
    read-only (99),
    ...
}
```

---

## Erratum 2 — Clause 13.5.2, p.307 — Unclear acknowledgement timestamp

**Error:** The language was unclear about the value of the timestamp for acknowledgement messages.

**Correction:** Added clarifying sentence: *"The 'Time Stamp' conveyed in the acknowledgement notification shall not be derived from the 'Time Stamp' of the original event notification, but rather the time at which the acknowledgement notification is generated."*

---

## Erratum 3 — Clause 12.11.43, p.186 — Erroneous sentence about Slave_Address_Binding writability

**Error:** A sentence from Clause 12.11.41 was mistakenly copied here stating Slave_Address_Binding is writable on MS/TP networks.

**Correction:** Removed the sentence *"If present, and the device is directly attached to an MS/TP network, then this property shall be writable."* — Slave_Address_Binding is a combination of configured and live data and is not expected to be writable.

---

## Erratum 4 — ANNEX C, p.497 — notification-class incorrectly marked OPTIONAL

**Error:** There is a discrepancy between the Event-Enrollment object definition in section 12.12 and Annex C. The `notification-class` property is incorrectly marked as OPTIONAL in Annex C.

**Correction:** Stricken the word OPTIONAL for `notification-class [17]`.

---

## Erratum 5 — ANNEX C, p.502 — Incorrect property name in Device object

**Error:** The name of the `max-APDU-length-supported` property in the device object definition is incorrect.

**Correction:** Changed to `max-APDU-length-accepted [62] Unsigned`.

---

## Erratum 6 — Clause 12.17.32.1, p.214 — Incorrect sign on Low_Diff_Limit

**Error:** The clause incorrectly states that for the FLOATING_LIMIT algorithm, Low_Diff_Limit should be the negation of Error_Limit. The algorithm subtracts that value already, so no sign change should occur. The algorithm is unusable as written.

**Correction:** Changed `Low_Diff_Limit = —Error_Limit` to `Low_Diff_Limit = Error_Limit`.

---

## Erratum 7 — Clause 12.17.33, p.214 — Confusion between "Error" and signed error in Deadband

**Error:** The Deadband description defined "Error" as a signed quantity, but "Error" was also previously defined in 12.17.32.1 and 12.17.32 as an absolute value.

**Correction:** Renamed the calculated value to "**SignedError**" throughout the Deadband clause, distinguishing it from the absolute Error_Limit.

---

## Erratum 8 — Table of Contents, p.vi — Misspelled "BACnet"

**Error:** The title for L.1 reads "BACent Operator Workstation (B-OWS)".

**Correction:** Changed to "**BACnet** Operator Workstation (B-OWS)".

---

## Erratum 9 — Figure 5-9, p.43 — Misspelled "Response"

**Error:** The top of the figure reads "(Segmented Reponse, with Application Program Flow Control)".

**Correction:** Changed to "(Segmented **Response**, with Application Program Flow Control)".

---

## Erratum 10 — Clause 21, p.471 — Incorrect comments for node_subtype and node_type

**Error:** A comment incorrectly lists `node_subtype` and `node_type` again with incorrect values (216 and 217), when they are already correctly shown as values 207 and 208.

**Correction:** Replaced with: *"-- enumeration values 216-217 are reserved for future addenda"*.

---

## Erratum 11 — Clause title p.167 — Incorrect clause title

**Error:** The clause title reads "Conditions for Generating a TO-NORMAL Event" but describes OFFNORMAL conditions.

**Correction:** Changed to "12.7.25.1 Conditions for Generating a TO-**OFFNORMAL** Event".

---

## Erratum 13 — Clause 12.11.16, p.182 — "read only" should be "read-only"

**Error:** "This read only property" should use the hyphenated form.

**Correction:** Changed to "This **read-only** property is a BACnetARRAY of Object_Identifiers…"

---

## Erratum 14 — Clause 12.12.5, p.188 — "read only" should be "read-only"

**Error:** Same hyphenation issue.

**Correction:** Changed to "This **read-only** property, of type BACnetEventType…"

---

## Erratum g) — Clause D.11, p.519 — UTC_Offset value in wrong units

**Error:** The UTC_Offset is shown as `6.0` but the property has units of minutes, and 6.0 hours = 360 minutes.

**Correction:** Changed `UTC_Offset = 6.0` to `UTC_Offset = 360`.

---

## Erratum 15 — Clause 21, p.472 — Missing comma in BACnetPropertyStates

**Error:** The last line of the BACnetPropertyStates CHOICE production is missing a comma after the enumeration value name.

**Correction:** Added comma: `door-alarm-state [15] BACnetDoorAlarmState,`

---

## Erratum 16 — ANNEX C, p.509 — Incorrect OPTIONAL designators in ACCESS-DOOR

**Error:** Several OPTIONAL designators need to be corrected to match Table 12-30: `door-status`, `lock-status`, `secured-status` should be OPTIONAL; `door-extended-pulse-time` should NOT be OPTIONAL.

**Correction:** Added OPTIONAL to `door-status [231]`, `lock-status [233]`, `secured-status [235]`; removed OPTIONAL from `door-extended-pulse-time [227]`.

---

## Erratum 17 — Table 12-15, p.189 — Missing Previous_Notification_Count

**Error:** `Previous_Notification_Count` was left out of the table entry for BUFFER_READY.

**Correction:** Added `Previous_Notification_Count` event parameter to the BUFFER_READY / NORMAL row.

---

## Erratum 18 — Clause 12.12.7 — Missing property description

**Error:** No description existed for `Previous_Notification_Count` in Clause 12.12.7.

**Correction:** Added: *"Previous_Notification_Count: This parameter, of type Unsigned32, applies to the BUFFER_READY algorithm. It contains the value that Total_Record_Count had at the time the previous BUFFER_READY notification occurred."*

---

## Erratum 19 — ANNEX F, F.1.5, p.561 — Extra space in hex literal

**Error:** Two cases of X'0C' appear with an extra space, as X'0C '.

**Correction:** Removed extra space — `X'0C '` → `X'0C'`.

---

## Erratum 20 — Clause 12.23, pp.237–243 — Misspelled "Converter"

**Error:** The subheading at the top of pages 237, 239, 241, 243 reads "Conveter".

**Correction:** Changed to "**Converter**".

---

## Erratum 21 — Clause 21, p.446 — Missing error enumerations

**Error:** The `unknown-device`, `unknown-route`, and `value-not-initialized` enumerations were left out of the Error production.

**Correction:** Inserted:
- `unknown-device (70)` (in alphabetic order, after timeout)
- `unknown-route (71)` (after unknown-property)
- `value-not-initialized (72)` (after unsupported-object-type)
- Comments for each in numeric order section

---

## Erratum 22 — Clause 13.12.1.2.1.7, p.322 — Obsolete Recipient property reference

**Error:** The last sentence about Event Enrollment Object Priority without Notification Class is no longer valid since removal of the Recipient property from Event Enrollment.

**Correction:** Deleted the sentence: *"In the case where an Event Enrollment Object is used without an associated Notification Class Object…"*

---

## Erratum 23 — Clause 21, p.469 — Missing state-description enumeration

**Error:** An enumeration for `state-description` was left out of the BACnetPropertyIdentifier production. A later comment correctly indicates its value (222), but the non-comment version was not included.

**Correction:** Inserted `state-description (222)` between `start-time (142)` and `state-text (110)`.

---

## Erratum 24 — Table of Contents, p.vi — Missing ANNEX N

**Error:** The Table of Contents is missing an entry for ANNEX N (BACnet/WS Web Services Interface).

**Correction:** Added entry for ANNEX N between M.5 and HISTORY OF REVISIONS.

---

## Erratum 25 — Clause N.4, p.652 — Incorrect title

**Error:** The title reads "N.4 Reference Notes".

**Correction:** Changed to "N.4 Reference **Nodes**".

---

## Erratum 26 — Clause 18.6 — Error codes under wrong parent clause

**Error:** DUPLICATE_NAME and DUPLICATE_OBJECT_ID error codes are listed under the SERVICES error class but should be under the PROPERTY class, based on their usage in Clauses 15.9.1.3.1 and 15.10.1.3.1.

**Correction:** Moved 18.6.4 DUPLICATE_NAME and 18.6.5 DUPLICATE_OBJECT_ID to 18.3.x and 18.3.y respectively (PROPERTY error class).

---

## Erratum 27 — History of Revisions — Missing ISO Amendment 1 reference

**Error:** Missing reference to creation of Amendment 1 to ISO standard EN ISO 16484-5 2007.

**Correction:** Added new row documenting Amendment 1 between Addendum f and Addendum b entries.

---

## Erratum 28 — Annex C, p.511 — Errors in TRENDLOG-MULTIPLE production

**Error:** Two errors: (1) ":: =" should be "::=" (no space), (2) log-device-object-property is typed incorrectly.

**Correction:** Changed to `TREND-LOG-MULTIPLE ::=` and `log-device-object-property [132] SEQUENCE OF BACnetDeviceObjectPropertyReference,`.

---

## Erratum 29 — Table 16-2, p.364 — Error Parameters conformance wrong

**Error:** The Error Parameters entry is shown as mandatory ("M") for Rsp and Conf columns, should be optional ("U").

**Correction:** Changed "M" to "U" for the Error Parameters row in Rsp and Conf columns.

---

## Erratum 30 — Clause 21, p.465 — Missing double-dash in comment

**Error:** The comment `-- see last-restart-reason (196)` has only one dash before "reason".

**Correction:** Changed to `-- see last-restart-reason (196)`.

---

## Erratum 31 — Clause 9.5.6.5, p.90 — Incorrect MS/TP token comparison

**Error:** In SoleMasterRestartMaintenancePFM, the comparison made to Npoll should be to Npoll-1 as in all other similar places. Also needed "and" keywords for consistency.

**Correction:** Updated SoleMasterRestartMaintenancePFM condition to match ResetMaintenancePFM pattern with Npoll-1.

---

## Erratum 32 — Clause 16.10.2, p.376 — "confirmed" used where "unconfirmed" needed

**Error:** In two places the word "confirmed" is used where it should be "unconfirmed". There is no "confirmed" Who-Is service. Also missing final period.

**Correction:** Changed two instances of "confirmed" to "**unconfirmed**"; added missing period at end of clause.

---

## Erratum 33 — Clause 18.6, p.394 — Missing LIST_ELEMENT_NOT_FOUND error code

**Error:** Addendum 135-2004b included a definition for `LIST_ELEMENT_NOT_FOUND` that was not carried into 135-2008.

**Correction:** Inserted new clause 18.6.X: *"LIST_ELEMENT_NOT_FOUND: A list data item required for carrying out the service request was not found."*

---

## Erratum 34 — Clause 21, p.445 — Missing list-element-not-found enumeration

**Error:** The `list-element-not-found` error code enumeration was not included in the Error production.

**Correction:** Inserted `list-element-not-found (81)` in alphabetic order and added corresponding comment in numeric order section.

---

## Erratum 35 — Clause 12.11.28, p.184 — APDU_Timeout default values not updated

**Error:** Addendum 135-2004d made changes to default APDU_Timeout values that were not carried into 135-2008.

**Correction:** Changed suggested value from 10,000 to **6,000** ms; default from 60,000 to **10,000** ms.

---

## Erratum 36 — Figure 5-1, p.14 — Missing shading in figure

**Error:** The shading was left off a portion of the figure showing the BACnet architecture layers.

**Correction:** Updated figure to show correct gray shading extending through Application Entity and BACnet elements down to NSAP.

---

## Erratum 37 — Clause 13.3.6, p.301 — Erroneous Boolean statement in analog algorithm

**Error:** There is an erroneous statement about Boolean data in the description of an analog OUT_OF_RANGE algorithm.

**Correction:** Removed: *"Note that the limit values may be Boolean TRUE or FALSE as well as analog values."*

---

## Erratum 38 — Clause 21, p.473 — Erroneous comma and ellipsis in BACnetRestartReason

**Error:** There is an erroneous comma after `hardware-watchdog` and a single ellipsis character should be three periods.

**Correction:** Changed `hardware-watchdog, (5)` to `hardware-watchdog (5)` and replaced single-character ellipsis with `...`.

---

## Erratum 39 — Clause 21, p.438 — Misspelling in ReadRange-ACK

**Error:** In the ReadRange-ACK production, ABSTRACT-SYNTAX.&Type is misspelled as &TYPE.

**Correction:** Changed `ABSTRACT-SYNTAX.&TYPE` to `ABSTRACT-SYNTAX.&Type`.

---

## Erratum 40 — Clause 21, p.445 — Erroneous comma after invalid-tag

**Error:** `invalid-tag, (57)` has an extraneous comma.

**Correction:** Changed to `invalid-tag (57)`.

---

## Erratum 41 — Clause 21, p.459 — Misspelled "SEQUENCE OF" in BACnetLogData

**Error:** "SEQUENCE of" uses lowercase "of" instead of "OF".

**Correction:** Changed to `SEQUENCE OF`.

---

## Erratum 42 — Clause 21, p.460 — Erroneous comma after logDatum

**Error:** An extraneous comma appears after logDatum in BACnetLogRecord.

**Correction:** Removed the comma.

---

## Erratum 43 — Clause 21, p.460 — Single ellipsis character in BACnetLoggingType

**Error:** Single ellipsis character should be three periods.

**Correction:** Changed to `...`.

---

## Erratum 44 — Clause 21, p.460 — Extraneous comma after logData

**Error:** Extra comma after `logData [1] BACnetLogData,` in BACnetLogMultipleRecord.

**Correction:** Removed the comma.

---

## Erratum 45 — Clause 21, p.461 — Extraneous comma after "other"

**Error:** Extra comma after `other (11),` in BACnetNodeType.

**Correction:** Removed the comma.

---

## Erratum 46 — ANNEX C, p.497 — Incorrect profile-name property number

**Error:** The property number for `profile-name` is shown as 167, should be 168.

**Correction:** Changed to `profile-name [168]`.

---

## Erratum 47 — ANNEX C, p.497 — Incorrect scale property number in ACCUMULATOR

**Error:** The `scale` property number is 186, should be 187.

**Correction:** Changed to `scale [187] BACnetScale`.

---

## Erratum 48 — ANNEX C, p.502 — Multiple errors in DEVICE production

**Error:** Multiple tentative correctness issues:
- `apdu-timeout [11]` should not be OPTIONAL
- `configuration-files` needs OPTIONAL suffix
- `slave-proxy-enable [172]` needs SEQUENCE OF BOOLEAN OPTIONAL
- `auto-slave-discovery [169]` needs SEQUENCE OF BOOLEAN OPTIONAL

**Correction:** Applied all corrections to the DEVICE ASN.1 production.

---

## Erratum 49 — ANNEX C, pp.503, 511 — Erroneous space in ::= operator

**Error:** EVENT-LOG and TREND-LOG-MULTIPLE have ":: =" instead of "::=".

**Correction:** Changed both to `::=`.

---

## Erratum 50 — ANNEX C, p.510 — Incorrect property number and comment formatting in LOAD-CONTROL

**Error:** (1) `state-description` property number is 282, should be 222. (2) Single dash `–` should be double dash `--` in comment for event-time-stamps.

**Correction:** Changed property number to 222 and comment to `-- accessed as a BACnetARRAY`.

---

## Erratum 51 — ANNEX C, p.511 — node-type incorrectly marked OPTIONAL in STRUCTURED-VIEW

**Error:** `node-type` should not be marked OPTIONAL in the STRUCTURED-VIEW production.

**Correction:** Removed OPTIONAL from `node-type [208] BACnetNodeType`.

---

## Erratum 52 — Figure 12-3, p.234 — Incorrect HALTED state transitions

**Error:** The transitions from the HALTED state are incorrectly shown in the Life Safety state machine.

**Correction:** Updated figure to show correct HALTED → IDLE/READY transitions.

---

## Erratum 53 — ANNEX A, p.494 — Missing PICS device profiles

**Error:** Addendum 135-2008l added two new device profiles (B-AWS, B-OD) but did not update the PICS.

**Correction:** Added B-AWS (BACnet Advanced Operator Workstation) and B-OD (BACnet Operator Display) to the PICS.

---

## Erratum 54 — ANNEX A, p.494 — Missing PICS data link option

**Error:** Addendum 135-2008g added BACnet/ZigBee but did not update the PICS.

**Correction:** Added *BACnet/ZigBee (ANNEX O)* to Data Link Layer Options.

---

## Erratum 55 — Clause 12.23.19, p.241 — Missing reference to Clause 13.1

**Error:** No cross-reference to Clause 13.1 in COV_Period property description.

**Correction:** Added: *"See clause 13.1"*.

---

## Erratum 56a — Clause 12.17.16, p.212 — Confusing Setpoint_Reference wording

**Error:** The language about zero or one references is confusing.

**Correction:** Clarified to use "absence of a reference" vs "presence of a reference" terminology.

---

## Erratum 56b — Clause 9.5.5, p.212 — Misleading comment about line contention

**Error:** The comment "in order to avoid line contention" could be misconstrued as making the Tturnaround delay optional.

**Correction:** Removed the comment — the delay is mandatory.

---

## Erratum 57 — Clause 6.5.2.2, p.57 — Inconsistent message rejection behavior

**Error:** The clause language is inconsistent with Clause 6.6.3.5 regarding when Reject-Message-To-Network is returned.

**Correction:** Added qualification: *"if the message was directed specifically at the router"* before requiring Reject-Message-To-Network.

---

## Erratum 58 — Clause 12.25.5, p.251 — Erroneous conditional phrase on Enable writability

**Error:** The Enable property must always be writable; the conditional "If Enable is writable" is incorrect.

**Correction:** Changed to affirm Enable IS writable. Strike "If Enable is writable" phrase.

---

## Erratum 59 — Clause 12.14.6, p.195 — "read only" should be "read-only" (quoted form)

**Error:** Uses quoted "read only" instead of hypenated read-only.

**Correction:** Changed to **read-only** property.

---

## Erratum 60 — Clause 19.2, p.401 — "read only" should be "read-only"

**Error:** Priority_Array is described as a "read only" array.

**Correction:** Changed to **read-only** array.

---

## Erratum 61 — Clause 19.2.1, p.402 — "read only" should be "read-only"

**Error:** Same hyphenation issue for Priority_Array property.

**Correction:** Changed `read only` to `read-only`.

---

## Erratum 62 — Clause D.26, p.531 — Incorrect enumeration value

**Error:** The enumeration shown for door-status is "OPEN" when the correct enumeration is "OPENED".

**Correction:** Changed `door-status = OPEN` to `door-status = OPENED`.

---

## Erratum 63 — Clause 6.3.1, p.54 — Missing BACnet/IP multicast support

**Error:** BACnet/IP is left off the list of data links that support multicast addresses.

**Correction:** Added *"and BACnet/IP (as defined in Annex J)"* to the list.

---

## Erratum 64 — Clause D.15, p.522 — Inconsistent example values (Life Safety Point)

**Error:** The example values do not represent a consistent state. Present_Value should be ALARM when Tracking_Value is ALARM.

**Correction:** Changed both Present_Value and Tracking_Value to ALARM.

---

## Erratum 65 — Clause D.16, p.523 — Inconsistent example values (Life Safety Zone)

**Error:** The example Event_State of LIFE_SAFETY_ALARM is inconsistent with Present_Value of PREALARM.

**Correction:** Changed Event_State to OFFNORMAL.

---

## Erratum 66 — Clause 12.24.10, p.246 — Wrong property name (singular vs plural)

**Error:** The title reads "List_Of_Object_Property_Reference" (singular).

**Correction:** Changed to "List_Of_Object_Property_References" (plural).

---

## Erratum 67 — Clause 13.5.2, p.246 — Extra space in error code name

**Error:** "NO_ALARM_ CONFIGURED" has an extra space.

**Correction:** Changed to "NO_ALARM_CONFIGURED".

---

## Erratum 68 — Clause 12.11.27, p.183 — APDU_Segment_Timeout not reflecting Addendum d-7

**Error:** The suggested default of 5000 does not show formatting separator. Should be 5,000.

**Correction:** Updated to 5,000 milliseconds.

---

## Erratum 69 — Clause 12.11.28, p.184 — APDU_Timeout missing "default" qualifier

**Error:** The language doesn't properly distinguish suggested from default values for APDU_Timeout.

**Correction:** Added "default" qualifier to differentiate suggested/adjustable value from hard default.

---

## Erratum 70 — Clause 12.11.29, p.184 — Truncated sentence in Number_Of_APDU_Retries

**Error:** The sentence was accidentally truncated; suggested default value "is." is incomplete.

**Correction:** Changed to *"...a suggested default value for this property is 3."*

---

## Erratum 71 — Clause 18.3, p.391 — LOG_BUFFER_FULL under wrong error class

**Error:** LOG_BUFFER_FULL is specified elsewhere to use the OBJECT error class, but is shown under PROPERTY class in Clause 18.3.6.

**Correction:** Moved from 18.3.6 (PROPERTY) to 18.2.x (OBJECT).

---

## Erratum 72 — Table 12-35, p.282 — Incomplete footnote

**Error:** Footnote 2 is not filled out to match the property description in Clause 12.30.13.

**Correction:** Added: *"This property is required to be writable when Logging_Type has the value POLLED and is required to be read-only when Logging_Type has the value TRIGGERED."*

---

## Erratum 73 — Clause 9.5.6.3, p.88 — Missing "BACnet" prefix in MS/TP handling

**Error:** In two places, "Data Expecting Reply" and "Data Not Expecting Reply" should have "BACnet" prefix.

**Correction:** Added BACnet prefix to both SendNoWait and SendAndWait cases.

---

## Erratum 74 — Clause 13.5.2, p.307 — Error table in wrong location

**Error:** The table describing error conditions should not appear in Service Procedure but rather in the Error Type clause.

**Correction:** Moved the error conditions table from 13.5.2 to 13.5.1.10.

---

## Erratum 75 — Clause 6.2.3, p.51 — Hop Count decrement past zero not disallowed

**Error:** As Hop Count is an unsigned 8-bit value, it cannot meaningfully decrement below zero. This should be explicit.

**Correction:** Added explicit instruction: *"If the Hop Count reaches a value of zero, the router shall discard the message and not forward it to the next router."*

---

## Erratum 76 — Clause 6.5.4, p.57 — Confusing duplicate Hop Count decrement

**Error:** Hop Count is always decremented per Clause 6.2.3. The additional decrement described in one of three cases in 6.5.4 was confusing and redundant.

**Correction:** Removed the second instance of "the Hop Count shall be decremented" from the routed case. Simplified to check if count is still > 0 after the mandatory decrement.

---

## Erratum 77 — Clause 15.8.1.1.4.1.2, p.354 — Misleading "oldest"/"newest" in ReadRange

**Error:** The 'By Position' form of ReadRange is not time-based, so "oldest" and "newest" descriptions for positive/negative Count are incorrect.

**Correction:** Removed "and oldest" and "and newest" from the positive/negative Count descriptions.

---

## Erratum 78 — Clause 15.4.4.4, p.30 — Incorrect PDU type name

**Error:** "ComplexACK PDU" should be "BACnet-ComplexACK-PDU" in the LastSegmentOfComplexACK_Received transition.

**Correction:** Corrected PDU type name.

---

## Erratum 79 — Table 12-27, p.238 — Unnecessary footnote in Pulse Converter

**Error:** Footnote 2 stating Count_Change_Time and Count_Before_Change are required if writable is unnecessary — they are always required properties.

**Correction:** Deleted footnote 2 and renumbered subsequent footnotes 3→2 and 4→3.

---

## Erratum 80 — Clause 12.23.13, p.240 — Inappropriate conditional in Adjust_Value

**Error:** The phrase "If this property is writable" is inappropriate — Adjust_Value is always required to be writable.

**Correction:** Changed to direct statement: *"The following series of operations shall be performed atomically when this property is written:"*

---

## Erratum 81 — Clause 12 (Various) — Missing X' prefix in hex values

**Error:** Many Event_Time_Stamp definitions in Clause 12 incorrectly show 'FF' instead of 'XFF'.

**Correction:** Added X' prefix wherever absent on hex time/date sentinel values.

---

## Erratum 82 — Clause 3.3, pp.5–7 — Missing UTC abbreviation

**Error:** Although UTC was used throughout the standard, there was no formal definition.

**Correction:** Added *"UTC Universal Time Coordinated"* to Clause 3.3 abbreviations list.

---

## Erratum 83 — Clause 20.1.12/20.1.13, p.422 — Missing clarification on local date/time

**Error:** No explicit statement that dates and times are local unless specified otherwise.

**Correction:** Added clarifying statements that date and time values shall be local unless specified otherwise (e.g., UTC).

---

## Erratum 84 — Clause 16.8.2, p.373 — Missing "UTC_" prefix in property name

**Error:** The Service Procedure for UTCTimeSynchronization incorrectly references Time_Synchronization_Recipients without the UTC_ prefix.

**Correction:** Changed all references to **UTC_Time_Synchronization_Recipients**.

---

## Erratum 85 — Clause 15.6.3.1.2.4, p.348 — Invalid seconds value in example

**Error:** Comparison value shows 99 seconds (:23:99.0) which is invalid.

**Correction:** Changed `6:23:99.0` to `6:23:00.0`.

---

> **Note:** Item numbers 1–11, 13–21 include corrections that were missed in earlier 135-2004 publications. Items 79–85 were added since July 20, 2010. The errata document is marked "Product Code: 86441 12/05" on the outside back cover identifying the first printing of Standard 135-2008.
>
> This appendix serves as a companion reference for BACnet network diagnostics and troubleshooting. Understanding formal protocol specification errors helps interpret unexpected device behavior on OT networks.
