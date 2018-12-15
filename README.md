# Live Tailing of LDMS Data

## LINK COMPUTATION
------
### Notes
* --logfile : rtr file
* --headerfile: header file
* --nidlist: tile list separated by commas. Tiles are given in the form of r_c
* Never put space between commas of python arguments for these programs


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
### Notes
* --logfile : nic file
* --headerfile: header file
* --nidlist: node list separated by commas
* Never put space between commas of python arguments for these programs



##### all nodes in the file
```shell
./niccomputation.py --logfile /tmp/test --headerfile ../../metric_set_nic.HEADER.1496978510
```

##### select nodes
```shell
./niccomputation.py --logfile /tmp/test --headerfile ../../metric_set_nic.HEADER.1496978510 --nidlist nid00630,nid00151
```
