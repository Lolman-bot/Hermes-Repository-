# BACnet Diagnostics — TrendLogs & Error Classes

> **Note**
> The four error-message classes are buckets, not specific faults. Treat them as a pointer to which devices to investigate, alongside the more specific diagnostics.


## Excessive TrendLog Buffer Read Rate

**What Happened?**

Your network test returned the "Excessive TrendLog Buffer Read Rate" diagnostic alert. This alert is to let you know Bitpool has detected a frequency of read requests to a TrendLog buffer that exceeds our threshold of once every 10 minutes. 

While some rapid reads are normal from time to time, a consistently high read rate can be an indication of configuration or programming issues.

Excessive read rates generate a high volume of network traffic, affecting network performance, response times, and affecting overall system stability.

**How to Fix it:**

Bitpool site analysis tools can identify the MAC/IP addresses of all devices with excessive TrendLog buffer read rates. Follow-up steps include:

- Configuration Review: Review and verify configuration settings for the TrendLog object highlighted in the diagnostic event. Ensure that the threshold and buffer size are set to appropriate levels to avoid filling up the buffer too quickly. Retest to ensure the issue has been resolved. 

- Testing: Conduct testing to ensure that the system's read rates are within acceptable limits and that data is collected efficiently.

## Excessive TrendLog Buffer Ready Notification

**What Happened?**

The "Excessive TrendLog Buffer Ready Notification" is an alert to let you know when a TrendLog buffer is being filled more than once every 10 minutes. 

While TrendLog notifications are a normal process, you should be aware when the notifications for the same Trendlog object are high—it can be a sign of configuration or programming issues.

Excessive read rates generate a high volume of network traffic, affecting network performance, response times, and affecting overall system stability.

**How to Fix It:**

- Bitpool site analysis tools can identify the MAC/IP addresses of the device with buffer full notifications higher than our set threshold. Adjust the configurations of devices to lower the frequency of TrendLog buffering, and retest to ensure the issue has been resolved. 

- Configuration Review: Review and verify configuration settings for the TrendLog object highlighted in the diagnostic event. Make sure that the threshold and buffer size are set to appropriate levels to avoid filling up the buffer too quickly. 

- **Te**s**ting:** Conduct testing to ensure that the system's read rates are within acceptable limits and that data is collected efficiently.

## Number of TrendLog Objects

**What Happened?**

It can be difficult to know how many processes might be running in the background within a BACnet system. The "Number of TrendLog Objects" diagnostic is informational only— designed to quickly let you know what devices on your network currently have TrendLogs active. Removing unnecessary Trendlog objects will reduce memory and storage resources.

**More information**:

- This diagnostic will identify the total number of active TrendLogs on your network and highlight the object with the highest number of active TrendLogs.

- An active TrendLog is defined as a TrendLog object that has sent at least one **BUFFER_READY** notification.

- The maximum number of TrendLogs per device is 50.

## Error Messages of Interoperability Type

**What Happened?**
Your network test returned an “Error Messages of Interoperability Type” message. This means there are compatibility issues between different devices or components on your network:

- Vendor-specific protocols that are not being understood by other devices.

- Features or capabilities not supported by another device are causing communication errors.

- Differences in BACnet profiles used by devices are leading to communication conflicts.

- Timing variations in device responses trigger communication timeouts or synchronization issues.

**How to Fix It**
Bitpool’s site analysis tools will identify the specific devices that are returning interoperability errors in your network for further investigation

However, proactive research and pre-deployment testing are the best ways to prevent interoperability errors:

- When sourcing devices and components, ensure that devices follow BACnet standards and profiles. 

- Thoroughly test the interoperability of devices in a controlled environment to identify and address issues.

- Employ consistent configuration profiles, data points, and unit make/model to create consistent and accurate information.

- Verify data mappings and translations between devices to ensure it’s still accurate.

- Keep device firmware up to date to address interoperability-related bugs or issues.

## Error Messages of Operational Type

**What Happened?**
Your network test returned an “Error Messages of Operational Type” message. These issues involve general system faults, and can include a broad number of issues you’ll likely see alongside other specific diagnostic results:

- **Device Faults:** device malfunctions, hardware failures, or communication problems.

- **Communication Errors:** failures transmitting or receiving data, indicating potential network communication issues.

- **Sensor or Actuator Errors:** anomalies or malfunctions in sensors, actuators, or other control devices.

- **Network Issues:** network congestion, disconnectivity, or instability.

- **System Alarm Conditions:** predefined alarm conditions, such as temperature thresholds, pressure limits, or security breaches.

- **Configuration Errors:** incorrect device settings, addressing conflicts, or improper configurations.

- **Security Breaches:** unauthorized access attempts or security breaches.

- **Critical Conditions**: potentially critical situations that require immediate attention to prevent system failures or safety risks.

**How To Fix It**
Bitpool’s site analysis tools can identify the specific devices that are returning operational errors in your network. However, proactive research and pre-deployment testing are the best ways to prevent interoperability errors:

- Continuously monitor the network and devices for error messages and anomalies.

- Use diagnostic tools and software to identify the root causes of operational errors.

- Regularly perform maintenance, updates, and inspections on devices 

- Take appropriate corrective actions quickly, such as reconfiguring devices, replacing faulty components, or addressing security breaches.

## Error Messages of Programming Type

**What Happened?**
Your network test returned an “Error Messages of Programming Type” message. These issues involve general errors in programming, configuration, or logic with your OT network, including:

- **Programming Errors:** incorrect or faulty logic programming within controllers or devices.

- **Data Mapping Errors:**  incorrect mapping of data points, sensors, or actuators.

- **Control Sequence Errors:** flawed control sequences, schedules, or sequences of operations.

- **Communication Configuration:** misconfigured communication settings that hinder proper data exchange between devices.

- **Addressing Conflicts:** duplicate device addresses or addressing conflicts.

- **Program Execution Errors:** runtime errors, exceptions, or script failures.

- **Alarm and Event Configuration:** incorrectly configured alarms, events, or notifications.

**How to Fix It**
Bitpool’s diagnostics provide detailed results across several of the categories that fall under this umbrella of errors. Bitpool’s site analysis tools can then help you drill down to devices that are reporting many of these errors. 

We also recommend Bitpool users upload new PCAP files (or set up continuous monitoring with an compatible BACnet capture hardware or software) to confirm improvements to your network health. 

There are also several proactive practices to help prevent future programming errors:

- Regularly check your device configs, addressing, and communication settings.

- Test programmed control sequences, logic, and configurations in a controlled environment.

- Use debugging tools, virtual environments, and diagnostic logs to resolve programming errors.

- Make training and knowledge to maintain these best practices part of your onboarding.

## Error Messages of Unknown Type

**What Happened?**
Your network test returned an “Error Messages of an Unknown Type” message. These messages have no specific category or classification. They serve as a generic “something unexpected has occurred” head’s up. Common causes for this message include: 

- **Undetermined System Behavior:** Notifications about unexpected behavior that aren't easily categorized.

- **Ambiguous Faults:** Messages indicating a problem that could have multiple potential causes, making it hard to classify.

- **Data Corruption:** Data corruption or anomalies that don't fit into a specific error category.

- **Unexpected Results:** Outcomes or responses that were not anticipated or covered by existing error codes.

- **Unrecognized Events:** Alerts about events or conditions that the system can't identify based on its existing error code list.

**How to Fix It**
Bitpool’s site analysis tools provide detailed results across several categories that will allow you to drill down to devices that are reporting many of these errors. 

We recommend Bitpool users upload new PCAP files (or set up continuous monitoring with an compatible BACnet capture hardware or software) to confirm improvements to your network health. 

There are also several root cause analysis practices you can adopt to your troubleshooting processes to help prevent future programming errors:

- Record these error messages for further review.

- Examine the circumstances leading to these messages to try and identify any patterns.

- Look for recurring or similar unknown errors to identify potential commonalities.

- Conduct controlled testing to reproduce the unknown error messages to gather more information.

- Seek assistance from system vendors or experts who might have encountered similar issues.
