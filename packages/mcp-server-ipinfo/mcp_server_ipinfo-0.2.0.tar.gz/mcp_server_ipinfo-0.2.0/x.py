from mcp_server_ipinfo.ipinfo import ipinfo_lookup

result = ipinfo_lookup(None)
print(result.timestamp)
