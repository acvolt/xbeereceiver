import json

j = json.loads ('{ "time" : "12:30", "temp" : "75.4", "setpoint" : "75" }')
print j
print "another try"
print json.dumps(j)
