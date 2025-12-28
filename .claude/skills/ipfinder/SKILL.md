---
name: find-ip
description: Finds the user's current public IP address and physical location data.
---

# Find IP & Location Skill

This skill allows Claude to retrieve network and geographic information for the user's environment.

## Instructions

When the user asks for their IP or location, perform the following:

1. **Network Info**: Run the following bash command to get full JSON data:
   - Command: `curl -s https://ipinfo.io/json`
2. **Parsing**: Extract the following fields from the JSON response:
   - `ip`: The public IP address.
   - `city`, `region`, `country`: The physical location.
   - `loc`: The latitude and longitude coordinates.
   - `org`: The Internet Service Provider (ISP).
3. **Local IP**: (Optional) Run `ifconfig` or `ip addr` to find the internal network IP.
4. **Display**: Present the information in a clean, readable summary.

## Example Output
"Your public IP is **8.8.8.8**, located in **Mountain View, California (US)**. 
ISP: Google LLC. 
Coordinates: 37.4056,-122.0775."