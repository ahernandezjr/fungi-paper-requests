# Shows the current status showing:
#   Genus done so far / Total Genus at start
f = open("metadata/status.txt")

status_array = []

for row in f:
    status_array.append(row.strip())

f.close()

print("Current Status: " + status_array[0] + "/" + status_array[1])