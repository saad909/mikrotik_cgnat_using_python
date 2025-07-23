1. Add NATTING Mappings in "ip_pools.xls"

Private Pool	Public IP
100.64.0.0/26	1.1.1.1
100.64.0.64/26	1.1.1.2


2. run the script main_v2.py. Script will nat accordingly and will ask for project name
3. Make sure project name is not present already. Otherwise it will replace previous project files
4. Script will generate two output files in output folder accroding to its project name
    a. Excel sheet contains mapping of private -> Public IP and Port range
    b. script file to configure on mikrotik
5. Copy script file into winbox by dragging file into winbox
6. import rsc file to install all commands
    `/import file-name=<filename>.rsc`
