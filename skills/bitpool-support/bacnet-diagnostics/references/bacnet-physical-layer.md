# BACnet Diagnostics — Physical & Wiring Layer

> **Note**
> These three almost always share a root cause in the physical layer. If you see one, check for the other two before touching any configuration.


## Checksum Errors

**What Happened?**
Your network test returned the “Checksum Errors” message. Checksum errors are commonly the result of physical wiring issues or hardware failures.

Checksum errors typically result in malformed (basically garbled data) and dropped packets.

**How to Fix It**
Because of the gibberish nature of the data received, you can’t rely on the source addresses in the packet to be correct. We recommend you trace the issue using Bitpool’s Lost Tokens Diagnostic with an active site analysis applied to your account. This will help track down devices with wiring or other physical issues. 

You can then quickly inspect and fix any faulty wiring terminations for these devices, then repeat your capture to confirm the problem is resolved.

## Lost Tokens

**What Happened?**

Your network test returned the “Lost Tokens” error. This means Bitpool has detected a **Reply-To-Poll-For-Master (RTPFM)** message on your network. While this can sometimes result from adding a new device while capturing packet data, it’s most likely a physical wiring issue somewhere on the network. 

Lost Tokens will result in communication loss between devices, and dropped packets.

**How to Fix It **

Bitpool’s site analysis tools will quickly identify the source and destination devices with lost tokens. You’ll have to physically inspect and fix any faulty wiring issues, then repeat your capture to confirm the problem is resolved.

## Excessive MS/TP Round Trip Token Time

**What Happened?**

Your network test returned the “Excessive MSTP Round Trip Token Time” message. This means the average token trip time around the network is longer than two seconds. The optimal round-trip time is 85ms or less. 

This issue is often wiring-related, and the latency leads to communication conflicts and lost messages.

**How to Fix It**

Bitpool’s site analysis tools results can identify devices with excessive round-trip times. You’ll have to physically inspect and fix any faulty wiring terminations at these devices, then repeat your capture to confirm the problem is resolved.
