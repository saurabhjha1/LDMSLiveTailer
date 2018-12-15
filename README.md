# Live Tailing of LDMS Data

## Notes
* Never put space between commas of python arguments for these programs

## LINK COMPUTATION
------
/tmp/test is either a nic file or an rtr file that is generated through test/test.py to emulate live behavior
##### all links
```shell
./linkcomputation.py --logfile /tmp/test --headerfile ../../metric_set_rtr_3_2_s.HEADER.1498195310 
```
##### select tiles
```shell
./linkcomputation.py --logfile /tmp/test --headerfile ../../metric_set_rtr_3_2_s.HEADER.1498195310 --tilelist 0_2,2_5
```

## NIC COMPUTATION
##### all nodes in the file
```shell
./niccomputation.py --logfile /tmp/test --headerfile ../../metric_set_nic.HEADER.1496978510
```

##### select nodes
```shell
./niccomputation.py --logfile /tmp/test --headerfile ../../metric_set_nic.HEADER.1496978510 --nidlist nid00630,nid00151
```
