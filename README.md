# Bandwidth monitor usage 
This allows to monitor an uplink interface bandwidth (bps) and report the peak bps value and time for a given month. This is an onbox reporting tool which allows to a user to view the peak bps for a given month/year

It consists of 2 parts
1. event script which runs every one hour to gather the stats and compare to the previous peak to report
    - the reported stats are stored as json files under `/var/log/peak_<year>_<month>.json format`
2. yang package which allows a user to run a show command to view the peak accounted bandwidth

## Installing 

### Event scripts
Run script every 1 min. This gives same functionality as a cronjob. Similarly you can change the granularity to one hour.

#### Config needed on the node
Can be a vSRX/MX/SRX etc 

```
set system scripts language python3
set system services netconf ssh

set event-options generate-event every-1-min time-interval 60
set event-options policy check-heartbeat events every-1-min
set event-options policy check-heartbeat then event-script bw_account.py
set event-options event-script file bw_account.py
```

#### Copy the event script to the DUT
Copy the python script/app under the below directory to ensure it works as expected 
```
/var/db/scripts/event
```

#### Validate
Once data has been generated a file would be created as below for every month in a year
The below is ingress BPS. File would be created upon executing the event script. 
```
root@vmx3> show log peak_2022_nov.json
{
    "time": "2022-11-04T03:52:33.113325",
    "BPS": "84000"
}
```

you can also validate by checking the event script log 

```
root@vsrx> show log escript.log | last

Nov  4 15:01:03 event script execution successful for 'bw_account.py' with return: 0
Nov  4 15:01:03 finished event script 'bw_account.py'
Nov  4 15:01:03 event script processing ends
Nov  4 15:02:01 event script processing begins
Nov  4 15:02:01 running event script 'bw_account.py'
Nov  4 15:02:01 opening event script '/var/db/scripts/event/bw_account.py'
Nov  4 15:02:01 reading event script 'bw_account.py'
Nov  4 15:02:02: /opt/lib/python3.7/site-packages/paramiko/rsakey.py:129: CryptographyDeprecationWarning: signer and verifier have been deprecated. Please use sign and verify instead.

Nov  4 15:02:06 event script execution successful for 'bw_account.py' with return: 0
Nov  4 15:02:06 finished event script 'bw_account.py'
Nov  4 15:02:06 event script processing ends
```

### Using of yang package
Copy the files from the director `yang-bandwidth-account` to the DUT under director `/tmp`  

Login to the node and execute the below command to install the package

```
root@vmx3> request system yang add package bandwidth-account module [/tmp/bandwidth-account.yang /tmp/junos-extension-odl.yang /tmp/junos-extension.yang] action-script /tmp/bw_account_action.py
```

Once the above is installed you will notice the installation is successful
```
YANG modules validation : START
YANG modules validation : SUCCESS
Scripts syntax validation : START
Scripts syntax validation : SUCCESS
TLV generation: START
TLV generation: SUCCESS
Building schema and reloading /config/juniper.conf.gz ...
Restarting mgd ...

WARNING: cli has been replaced by an updated version:
CLI release 20220203.184547_builder.r1238228 built by builder on 2022-02-03 19:13:54 UTC
Restart cli using the new version ? [yes,no] (yes) yes

Restarting cli ...
```
#### Verify

##### Possible completions
```
root@vmx3> show bandwidth-account ?
Possible completions:
  <[Enter]>            Execute this command
  detail               detailed view of bps across all monitored interfaces
  month                3 letter month format. eg jan,feb..
  year                 4 digit year representation
  |                    Pipe through a command
```

##### Get stats

This shows the peak-bps during the month was noticed at given time.

```
root@vmx3> show bandwidth-account month nov year 2022
Bandwidth accounting information
	time	      : 2022-11-11T12:06:00.711660
	peak-bps      : 63400
```

Detailed view

```
root@vmx3> show bandwidth-account month nov year 2022 detail
Bandwidth accounting information
	time	      : 2022-11-11T12:06:00.711660
	interface     : ge-0/0/0.0
	intf-peak-bps : 32600

	time	      : 2022-11-11T12:06:00.711660
	interface     : ge-0/0/1.0
	intf-peak-bps : 30800

```
