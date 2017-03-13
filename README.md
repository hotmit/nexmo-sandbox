# Best Voices
```
Joey - en-US male
Salli - en-US female

Celine - fr-FR female
```

# Create New App
```
npm install nexmo-cli -g
nexmo setup <key> <secret>

nexmo app:create "My App" http://208.124.157.3:10004/ http://208.124.157.3:10004/ --type=voice --keyfile=private.key
```

# Verify Call
```
response = client.start_verification(number='441632960960', brand='MyApp')
if response['status'] == '0':
print 'Started verification request_id=' + response['request_id']
else:
print 'Error:', response['error_text']


response = client.check_verification('00e6c3377e5348cdaf567e1417c707a5', code='1234')
if response['status'] == '0':
print 'Verification complete, event_id=' + response['event_id']
else:
print 'Error:', response['error_text']
```

# Hangup
```
response = client.update_call(uuid, action='hangup')
```

# Pip Install in Develop Mode
```
python setup.py develop
```