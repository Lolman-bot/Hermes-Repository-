# BACnet Diagnostics — Discovery & Reachability

> **Note**
> Discovery floods and unreachable devices feed each other: a device that never answers keeps being searched for, and the search traffic degrades the segment further.


## Device Global Discovery

**What Happened?**
Your network test returned a “Device Global Discovery” error. This means three or more Global **Who-Is** requests have occurred during the same capture. There are several causes for excessive Global Discovery, including configuration errors, address conflicts, or hardware failure. 

These requests trigger a flood of broadcast (**I-Am**) traffic, leading to communication conflicts and denial-of-service (DoS) issues.

**How to Fix It**
Bitpool’s site analysis tools can help to diagnose several of the most common issues to help resolve global discovery issues, including:

- An excessive number of devices on a single MS/TP network

- Duplicate device addresses on the same network

- Device instability causing traffic issues

## Excessive BACnet Discovery

**What Happened?**

Your network test returned an "Excessive BACnet Discovery" diagnostic. This means specific BACnet objects are being repeatedly queried using **WHO-HAS** requests, generating excessive discovery traffic that degrades network performance.

This is distinct from Device Global Discovery (which triggers on excessive **Who-Is** requests). Excessive BACnet Discovery is triggered when devices repeatedly broadcast WHO-HAS messages to locate BACnet objects (devices or properties), overwhelming the network instead of relying on cached object locations.

Common causes:
- Misconfigured clients that poll repeatedly instead of caching discovered objects
- Programming errors causing discovery requests to loop
- Devices with long or missing object discovery intervals

**How to Fix It**

- Use Bitpool's site analysis tools to identify the source devices and MAC/IP addresses generating excessive WHO-HAS queries
- Review which objects are repeatedly targeted and why
- Tune device configurations to:
  - Cache discovered objects rather than repeatedly querying
  - Increase discovery intervals between WHO-HAS requests
  - Fix any misconfigured clients with discovery loops
- Retest the network after changes to confirm traffic normalises

## Fully Unreachable Devices

**What Happened?**

Your network test returned a “Fully Unreachable Devices” error. This means one or more devices on your network aren’t responding to any of the **Who-Is** requests sent with an **I-Am** response during the capture. Unlike a partially unreachable device, these are completely unavailable all the time.

There are several common causes for unreachable devices, like power failures, physical disconnects, device failures, programming or configuration errors, and security/firewall settings.

**How to Fix It**
Bitpool’s site analysis tools will identify all non-responding devices on the network. Once identified, you’ve got a few actions available to resolve the issue, including:

- Reviewing device and network configurations for errors or mismatches. 

- Resetting the querying device to clear its cache and force it to reestablish connections.

- Modify the programming of the querying devices to stop searching for a removed device, and reset its cache to reestablish its connections.

- Physically inspect unreachable devices and network infrastructure for damaged cables or components, and confirm it’s still present.

- Adjust firewall and security settings to allow necessary communication for BACnet devices.

- Review your network topology to ensure devices are in the correct segments and routing is configured properly.

## Partially Unreachable Devices

**What Happened?**

Your network test returned a “Partially Unreachable Devices” error. This means one or more devices on your network have not responded to at least one of the **Who-Is** requests with an **I-Am** response during the capture. Unlike fully unreachable devices, partially unreachable devices respond sporadically—or may fail to respond to certain requests completely.

There can be several reasons devices become partially unreachable, including network congestion and geographic latency, power fluctuations, software issues, and device overload. 

**How to Fix It**

Bitpool’s site analysis tools will identify all partially responding devices on the network. Once identified, you’ve got a few actions available to resolve the issue, including:

- Physically inspecting devices and network infrastructure for issues like damaged cables or components.

- Monitoring network/subnet traffic levels and quality to identify congested segments or areas with signal interference.

- Assessing device load and distributing tasks efficiently to prevent overload.

- Checking—and then keeping—device firmware and software up to date.

- Ensuring stable power to devices to prevent voltage fluctuations that can affect communication.

- Optimize routing or network topology to reduce latency.

## Slow Response Time

**What Happened?**

Your network test returned a “Slow Response Time” message. This means a device on your network is taking longer than our recommended time (in seconds) between a **Who-Is** request and the **I-Am** response. 

Network congestion is often the culprit behind slow response times, with either the responding device being overloaded, too many network hops, or the destination device experiencing latency. Slow response times can have impacts ranging from annoying – delays in receiving messages – to an inability to monitor critical or sensitive systems in an acceptable time frame. 

**How to Fix It**

By using Bitpool’s site analysis’s** **detailed diagnostic results, you can identify the path between the requesting and responding device for each slow response time. You can then investigate the routers in the path to see the level of traffic passing between them. You can also check the responding devices to see if they are also experiencing congestion. 

Don’t forget, after optimizing your network for traffic flow, retest your network to ensure the issues are resolved.

## Unacknowledged Requests

**What Happened?**

Your network test returned a “Unacknowledged Requests” error message. This is to let you know there is one or more devices on your network that did not receive an acknowledgment after sending a message. 

This error typically occurs when the destination device (or its router) is either offline or busy. Unacknowledged requests can lead to data loss, fault detection delay, and overall degradation of system performance. 

**How to Fix It**

Bitpool’s site analysis’s detailed diagnostic results will identify which device has failed to respond, allowing you to quickly focus on resolving the issue. Inspecting the hardware for any physical issues, such as lost or damaged cables, as well as confirming proper configuration, is a good first step.

Addressing unacknowledged requests requires a combination of troubleshooting, network optimization, and careful configuration:

- Identify patterns of unacknowledged requests to pinpoint specific devices or areas in the network that are experiencing communication issues.

- Adjust retransmission parameters on devices to allow for a reasonable number of retries without overwhelming the network with unnecessary traffic.

- Review the network topology to ensure that there are no physical barriers or interference causing communication problems.

- Minimize the amount of unnecessary traffic on the network by optimizing communication patterns and avoiding excessive polling.

- Ensure that devices' clocks are synchronized to prevent timing issues that might lead to unacknowledged requests.

- Implement Quality of Service (QoS) mechanisms to prioritize critical messages and prevent them from being lost due to network congestion.

- Keep devices' firmware up to date.

- Consider segmenting the network into smaller sub-networks to reduce network congestion and improve reliability.

- Regularly test devices' communication and monitor network traffic to identify and address unacknowledged requests promptly.
