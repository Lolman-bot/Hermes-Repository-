# BACnet Diagnostics — Addressing & Topology

> **Note**
> Most of these are configuration errors rather than faults — they are fixed by reassigning an address or a setting, not by replacing hardware.


## Duplicate Device Address

**What Happened?**
Your network test returned a “Duplicate Device Address” error. A simple mistake that can be hard to diagnose, this happens when two devices are assigned the same network address. 

Duplication issues can lead to communication conflicts, disruptions, and confusion within the network.

**How to Fix It**
Bitpool’s site analysis tools identify the devices with duplicate MAC/IP addresses without having to resort to network bifurcation (splitting your network to see which side the problem persists on). Simply reassign those devices with a new unique MAC or IP address, and retest your network to ensure the issue is resolved.

## Duplicate Device Instance Number

**What Happened?**

Your network test returned a “Duplicate Device Instance Number” error. This means two or more devices on your network have the same BACnet device instance number. This can lead to communication conflicts and disrupt the normal operation of the OT network.

**How to Fix It **

Bitpool’s site analysis tools will identify the devices with duplicate BACnet device instances without having to bifurcate your network. Simply reassign those devices with a new unique BACnet instance number, and retest your network to ensure the issue is resolved.

## Duplicate Network Number

**What Happened?**
Your network test returned a “Duplicate Network Number” error. This means two or more routers are directing traffic to the same network segment. This can lead to communication conflicts and disrupt the normal operation of the network.

**How to Fix It**
Bitpool’s site analysis tools identify the addresses of all the routers with duplicate network numbers. Simply reassign those devices with a new unique network number, and retest your network to ensure the issue is resolved.

## Duplicate BACnet Broadcast Management Device (BBMD)

**What Happened?**

Your network test returned a "Duplicate BBMD" diagnostic. This means two or more BACnet Broadcast Management Devices (BBMDs) on the same IP subnet are forwarding broadcast messages to the same destination subnet(s). This doubles or multiplies unnecessary traffic and risks broadcast storms.

BBMDs relay BACnet broadcast messages across routed IP subnets via a Broadcast Distribution Table (BDT). While multiple BBMDs on one segment aren't inherently problematic, duplicates forwarding from the same source to the same destinations cause redundant traffic amplification.

Common causes:
- Configuration errors: multiple devices (often mixed-vendor) set as BBMDs with overlapping BDTs on the same subnet
- New or expanded sites set up without coordination
- Reused configs or untracked device swaps

**How to Fix It**

Bitpool's site analysis will identify duplicate BBMD IP/MAC addresses and their BDT destination overlaps.

- **Option A:** If BDTs match, disable BBMD on all but one device on that subnet
- **Option B:** Edit BDTs to eliminate overlaps — remove duplicate destination subnets and ensure no repeated BBMD IPs appear in tables
- Reassign unique BACnet device addresses if needed
- Rerun diagnostics to verify resolution
- Document changes and review BBMD configs regularly to prevent recurrence

> **Tip:** There should ideally be only **one BBMD per network segment**.

## Detected Circular Networks

**What Happened?**

Your network test returned a "Detected Circular Networks" diagnostic. This means Bitpool has identified a loop in your BACnet network where packets circulate repeatedly. This is detected by analysing BACnet NPDU packets from the same source with varying (decrementing) hop count values — flagged when hop count drops below 10.

Common causes:
- Multiple protocols enabled simultaneously on a controller (e.g., both BACnet/IP and Ethernet enabled during migration or setup)
- Redundant or overlapping routes creating unintended circular paths

This primarily affects BACnet/IP networks (rare on MS/TP) and always coincides with Low Hop Count alerts. The resulting broadcast storm can completely block access to affected controllers.

**How to Fix It**

1. Use Bitpool to identify the BACnet routers or controllers involved (IP/MAC addresses highlighted in diagnostic results)
2. Unplug the network connection of one implicated controller and isolate it
3. Reconfigure the device to remove redundant routes or protocols (e.g., disable the duplicate protocol)
4. Reconnect the device to the network
5. Recapture traffic and rerun diagnostics in Bitpool to confirm the loop is resolved

**Prevention:** Enable only necessary protocols on devices. Design networks with clear, non-overlapping routes. Test thoroughly after any migration.

## Gap in MSTP Device Addressing

**What Happened?**

Your network test returned the “Gap in MSTP Device Addressing” error. This means Bitpool has detected that devices are not addressed sequentially within your network. 

This can lead to communication delays as devices take time to repeatedly look for (**poll-for-master**) those missing MAC addresses every 50 token cycles.

**How to Fix It**

Bitpool’s site analysis tools will identify exactly which addresses are missing in the sequence, so you can quickly re-configure device addresses to fill any gaps.

## Excessive Number of Devices on a Single MSTP Network

**What Happened?**

Your network test returned the “Excessive Number of Devices on Single MSTP Network” error. This means Bitpool has detected more than 32 master devices on an MS/TP network – which typically leads to a loss of speed and integrity. 

While an MS/TP network can officially accommodate 127 devices on a single network, it’s generally accepted that more than 32 impacts performance significantly. 

**How to Fix It**

To resolve this, we recommend breaking up larger MS/TP networks into two or more smaller segments using BACnet routers.

## Excessive Max Master

**What Happened?**

Your network test returned the “Excessive Max Master” message. This means the max master setting on your MS/TP network exceeds the last master device by more than two – for example, you have 20 devices on your network but the **max_master** value is set to 23 or higher. The usual cause for this is that the factory default setting of 127 was never modified.

An incorrect max master setting will cause unnecessary **poll-for-master** calls, slowing down communications on the network.

**How to Fix It**

Configure your **max_master** value on the device to be no more than two above the last master device on the network.
