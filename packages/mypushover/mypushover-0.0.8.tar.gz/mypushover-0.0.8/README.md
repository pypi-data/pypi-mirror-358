## mypushover

#### Installation
`pip install mypushover`

#### USAGE:
Run `mypushover` to firstly generate configuration file.

If you want to run in background, root privilege is needed. Run

`mypushover -start`


#### OPTIONS:
    -c              config file path config file path, 
    				if not set, use default path: ../site-packages/mypushover/pushover_conf.conf
    -start          start service in background
    -stop           stop service
    -restart        restart service
    -disable        disable service and remove startup script
    -restart        restart service
    -status         show service status

configuration can refer to `pushover_conf.example`