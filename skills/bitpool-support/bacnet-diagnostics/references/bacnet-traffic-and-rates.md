# BACnet Diagnostics — Traffic & Rates

> **Note**
> A high rate is not automatically a fault. Several of these are advisory: the question is whether the rate is deliberate, not whether it is high.


## BACnet Request Retry

**What Happened?**

Your network test returned a "BACnet Request Retry" diagnostic. This means one or more devices are resending BACnet requests because they did not receive a timely acknowledgment (ACK). It indicates communication disruptions such as packet loss, delays, or conflicts on the network.

Common underlying causes include:
- Physical wiring problems, loose connections, or damaged cabling causing sporadic packet drops
- High network traffic, broadcast storms, or router backpressure overwhelming the segment
- Device configuration errors, duplicate addresses or instance numbers, or unreachable/phantom devices
- Latency in MS/TP token passing (e.g., excessive round-trip times >85ms) or gaps in device addressing

**How to Fix It**

Correlate this diagnostic with other Bitpool results (e.g., Lost Tokens, Checksum Errors, Duplicate diagnostics) using site analysis tools. Prioritise fixing higher-priority issues first as they often resolve retries indirectly.

- **Inspect physical layer:** Check cabling, terminations, and hardware for faults. Use the Lost Tokens diagnostic with site analysis to trace wiring issues.
- **Identify traffic offenders:** Use site analysis to pinpoint devices sending excessive broadcasts, COV messages, or Router-Busy-To-Network signals. Tune configurations to reduce rates.
- **Resolve duplicates/unreachables:** Find and reassign duplicate device instances, MAC addresses, or network numbers. Verify removed devices are no longer being polled.
- **Review configurations:** Reset querying device caches, adjust firewall/routing rules, ensure sequential MS/TP addressing.
- **Retest:** Run a new capture after fixes to confirm resolution.

## Busy Router Backpressure

**What Happened?** 

Your network test returned the “Busy Router Backpressure Messages” warning. This means one or more of your BACnet routers are receiving high levels of traffic and can’t process any more incoming messages.  

Overloaded routers can lead to a variety of network issues, including congestion, latency, data loss, and overall performance degradation. 

**How to Fix It**

There are many reasons why router backpressure may be occurring, but most originate from sources creating too much traffic. Bitpool’s site analysis results can identify devices that are generating excessive traffic or sending **Router-Busy-To-Network** messages to help you find areas to optimize your network performance.

## Excessive Broadcast by Source

**What Happened?**
The "Excessive Traffic Rate: Broadcast by Source" diagnostic alerts users when the frequency of broadcast packets exceeds the test threshold. The overview will tell you the rate of broadcast packets per minute (PPM), as well as the largest broadcast rate from a single device.

While it's common to see a lot of broadcast packets in the BACnet protocol, without managing device broadcast frequency, they can become overwhelming to the network as each device must process every broadcast message.

A broadcast flood can have serious implications on overall network performance and stability.

**How to Fix It**

- Use Bitpool site analysis(s) to identify the MAC/IP addresses of all devices transmitting a high rate of broadcast messages. Adjust the configurations of devices to lower the frequency of broadcast messages, and retest to ensure the issue has been resolved. 

- Network routing: Consider whether devices with high broadcast need to be in contact with all other devices in your network. If possible, create routing limiting the number of devices the broadcast will reach.

The next few error messages are closely related as they all reference devices sending a lot of traffic in a very short period. While the explanations might differ, the causes and solutions are usually the same.

## Excessive Change of Value (COV) Rate

**What Happened?**

Your network test returned an “Excessive Change of Value (COV) Rate” message. This means that the average gap between COV messages coming from one or more of your network devices is very small, and it’s producing a lot of data on the network. Our threshold for alerting is more than one COV message per device every five minutes. 

Excessive COV rates can negatively affect the performance of your network, leading to an increase in response times, decreased resources, and instabilities across your system.

**How to Fix It**

It’s important to note that** high COV rates aren’t always a bad thing**. There are situations where precise data, and therefore a lot of reporting, is a requirement. That said, excessive COV rates are often the result of programmers creating blanket polling policies for all object types across all devices. In a large system, this has the potential to trigger a flood of unnecessary data traffic.

Bitpool’s site analysis tools can identify the addresses of devices causing COVs above our set threshold, allowing you to deep dive into packets to understand read properties (here’s our BACnet Object Glossary to identify the points being read), and tune the number of reads per device to your needs. This can help reduce needless traffic and congestion across your network. 

Some common ways of tuning we recommend include: 

- Configuration Review: Review and verify configuration settings for data polling rates to ensure they align with the intended requirements.

- Reduce Poll Rates: Set appropriate polling frequencies based on the importance of the data, the rate of change, and the system's operational needs.

- Optimize Control Programming: Optimize control programs and scripts to avoid unnecessary or redundant data polling.

- Continuous Network Monitoring: Monitor network traffic and resource usage to identify patterns of excessive read rates.

## Excessive Read Rate

**What Happened?**

Your network test returned an “Excessive Read Rate” message. This means that the average gap between reads on one or more of your network devices is very small, and it’s producing a lot of data on the network. Our threshold for alerting is more than one read per device every five minutes. 

Excessive read rates can negatively affect the performance of your network, leading to an increase in response times, decreased resources, and instabilities across your system.

**How to Fix It**

Like COV warnings, high read rates aren’t always bad, but we want you to be aware they’re happening (in case you aren’t). Excessive read rates are often the result of programmers creating blanket polling policies for all object types across all devices. In a large system, this has the potential to trigger a flood of unnecessary data traffic.

Bitpool’s site analysis tools can identify the addresses of devices causing reads above our set threshold, allowing you to deep dive into packets to understand read properties (here’s our BACnet Object Glossary to identify the points being read), and tune the number of reads per device to your needs. This can help reduce needless traffic and congestion across your network. 

Some common ways to consider tuning include: 

- Configuration Review: Review and verify configuration settings for data polling rates to ensure they align with the intended requirements.

- Reduce Poll Rates: Set appropriate polling frequencies based on the importance of the data, the rate of change, and the system's operational needs.

- Optimize Control Programming: Optimize control programs and scripts to avoid unnecessary or redundant data polling.

- Convert Reads into Change-of-Value: Instead of polling the value, use a Change-of-Value “push” notification when the value changes.

- Continuous Network Monitoring: Monitor network traffic and resource usage to identify patterns of excessive read rates.

## Excessive Write Rate

**What Happened?**

Your network test returned an “Excessive Write Rate” message. This means that your Building Automation Systems (BAS) is performing write operations (updating data or settings) to a device at an unusually high frequency. There are a few common causes for this, including:

- Incorrectly configured settings 

- Malfunctioning or inefficient control programming 

- Frequent adjustments to control loops 

- Excessive data logging

Excessive write operations can generate high levels of network traffic, impacting network performance, and contributing to increased wear and reduced device lifespan.

**How to Fix It**

Write rates should be tuned specifically to your needs, and this diagnostic result doesn’t always mean there is a problem, it’s more of a head’s up — in the event you want to optimize your settings.

Bitpool’s site analysis tools can identify all devices with excessive write rates above our set threshold, allowing you to deep dive into the results (here’s our BACnet Object Glossary to identify the points being written) and tune writes per device to your needs. 

Some common ways of tuning we recommend include:

- Configuration Review: Review and verify configuration settings for data polling rates to ensure they align with the intended requirements.

- Write Frequency Guidelines: Set write frequencies based on the frequency of control changes, data logging requirements, and system performance goals.

- Optimize Control Programming: Optimize control programs and scripts to avoid unnecessary or redundant data polling.

- Control Loop Tuning: Tune control loops to prevent rapid and unnecessary adjustments that lead to excessive write operations.

- Data Logging Strategies: Implement efficient data logging strategies to minimize unnecessary write operations for logging.

- Continuous Network Monitoring: Monitor network traffic and resource usage to identify patterns of excessive write rates.

- Testing: Conduct regular testing to ensure that the system's write rates align with operational requirements and don’t negatively impact device performance.

## Excessive Token Hold Time

**What Happened?**

Your network test returned the “Excessive Token Hold Time” error. This means Bitpool has detected a device on your network holding the MS/TP token for longer than 500ms. This suggests that an MS/TP device on your network is trying to communicate too many messages, possibly running out of time to finish before the token moves along. 

The result can be network congestion and delayed messages.

**How to Fix It**

Bitpool’s site analysis tools will identify devices with excessive token hold times. In the device configuration, you can increase the **max_info_frame **device attribute (default is 1) to flush out the buffer and/or reduce the amount of messages being sent.

## Router Rejecting Network Messages

**What Happened?**

Your network test returned a “Router Rejecting Network Messages” error. This means that a router on your network isn’t forwarding or passing on certain messages, data packets, or communication requests. This can be caused by misconfigured policies, resource overload, network congestion, and security settings. 

These types of errors can lead to data loss, communication breakdown, operational errors, congestion, and stability issues. 

**How to Fix It**

Bitpool’s site analysis tools can identify how many, and how often, routers are rejecting network messages. You can then take several actions to resolve the issue, including:

- Verifying the router's access control policies and configuration settings.

- Reviewing security settings to prevent false positives while still blocking potential threats.

- Monitoring the router performance and utilization levels.

- Conducting testing and simulations to reproduce rejected messages to identify root causes.

- Keeping router software and firmware up to date.
