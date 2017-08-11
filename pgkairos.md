## Data collection for PostgreSQL

In the PostgreSQL universe, data collection is done by adding an extension to a PostgreSQL database.

The software is delivered as  a "rpm" archive containing the extension. After installation the software will be downloaded in the directory "/usr/share/postgresql/9.6/extension".

A typical installation on a centos system is:

```
$ rpm --ignoreos -i https://github.com/gduvalsc/pgkairos/raw/master/pgkairos-0.5-1.noarch.rpm
```

In this example, pgkairos is installed in version "0.5"

After that step, the extension is available. You can check the availability by running:

```
$ psql -c "select * from pg_available_extensions" | grep kairos
```

This extension must be then created in a new PostgreSQL database named "kairos"

```
$ psql -c "create database kairos"
$ psql -d kairos -c "create extension pgkairos"
$ psql -d kairos -c "\dp"
```

The last command lists all tables created through the extension. An exmaple of the list is:

```
                                      Access privileges
 Schema |          Name           | Type  | Access privileges | Column privileges | Policies 
--------+-------------------------+-------+-------------------+-------------------+----------
 public | kpg_stat_activity        | table |                   |                   | 
 public | kpg_stat_database        | table |                   |                   | 
 public | parameters               | table |                   |                   | 
 public | psutil_cpu_times         | table |                   |                   | 
 public | psutil_disk_io_counters  | table |                   |                   | 
 public | psutil_net_io_counters   | table |                   |                   | 
 public | psutil_processes         | table |                   |                   | 
 public | psutil_swap_memory       | table |                   |                   | 
 public | psutil_virtual_memory    | table |                   |                   | 
 public | vkpg_stat_activity       | view  |                   |                   | 
 public | vkpg_stat_database       | view  |                   |                   | 
 public | vpsutil_cpu_times        | view  |                   |                   | 
 public | vpsutil_disk_io_counters | view  |                   |                   | 
 public | vpsutil_net_io_counters  | view  |                   |                   | 
 public | vpsutil_processes        | view  |                   |                   | 
 public | vpsutil_swap_memory      | view  |                   |                   | 
 public | vpsutil_virtual_memory   | view  |                   |                   | 

```

From there, the extension is operational. A lot of functions are available to collect, purge or export data.

The "config" table keeps in mind the global parameters to control this process:

```
$ psql -d kairos -c "select * from parameters"
   param   | value 
-----------+-------
 enable            | true
 system            | true
 retention         | 15.0
 directory         | /tmp
 num_rows_per_file | 10000
```

The kairos extension collects statistics if the "enable" poarameter is set to "true". Controlling the "enable" parameter allows to enable or disable the collect of statistics

The "retention" parameter specifies the number of days statistics are retained in the kairos database. When the purge is activated, data older than "retention" days is removed from kairos database.

The "directory" parameter specifies the directory in which "exports" are generated.

The "num_rows_per_file" parameter allows to control the size of exported data. When a table has a number of rows exceeding this parameter, then the exported result is splitted in several files containing at most "num_rows_per_file" rows.

All parameters of the config table can be read using the "get_param" function.

# Collecting data

The pgkairos extension contains 3 different collects: "system", "database" and "detailed". These 3 different collects are triggered independently of each other.

The "system" collect is intended to get information at system level (cpu, disks, memory, processes) independently of postgresql database. The goal is to check periodically if everything is correct at the system level. The periodicity of this collect should not be inferior to one minute.

A typical "system" collect triggered by cron is:

```
* * * * * psql -d kairos -c "select snap_system()"
```

The "database" collect is intended to get information from pg_stat_database dynamic view. The periodicity of this collect should not be inferior to one minute too.

A typical "database" collect triggered by cron is:

```
* * * * * psql -d kairos -c "select snap()"
```

The "detailed" collect is intended to get information from pg_stat_activity dynamic view. The periodicity of this collect should always be inferior to one minute (typically 10 or 5 seconds)

A typical "detailed" collect every 5 seconds triggered by cron is:

```
* * * * * TERM=xterm flock -w1 /tmp/xxx watch -n 5 -e -t --precise -x psql -d kairos -c 'select snap_detailed(5)'>>/tmp/xxx
```

cron cannot trigger something with a periodicity less than one minute. But note the usage of "watch" with the "-n" paramater as well as usage of "flock" to avoid several execution of the same command at the same time. The periodicity must also be given as a parameter of the "snap_detailed" function.

# Purging data

The "parameters" table contains a prameter to define data retention within the "kairos" database. By default, this parameter defines a data retention of 15 days. 

Purging data is not automatically triggered. To be effective, "purging" must be trigerred by a scheduler like this (example with cron):

```
0 4 * * * psql -d kairos -c "select purge()"
```
Here data older than the retention parameter will be removed from the kairos database at 04h00 AM every day.

# Exporting data

Export can be triggered manually or through a scheduler like cron on a regularly basis (typically once a day).

2 different export are provided: "full" or "daily"

The "full" export is generally triggered manually to get the whole content of the kairos database.

```
$ psql -d kairos -c "select export_full()"
NOTICE:  Exporting vpsutil_cpu_times ...
NOTICE:  Writing file: vpsutil_cpu_times_0 ...
NOTICE:  Exporting vpsutil_virtual_memory ...
NOTICE:  Writing file: vpsutil_virtual_memory_0 ...
NOTICE:  Exporting vpsutil_swap_memory ...
NOTICE:  Writing file: vpsutil_swap_memory_0 ...
NOTICE:  Exporting vpsutil_disk_io_counters ...
NOTICE:  Writing file: vpsutil_disk_io_counters_0 ...
NOTICE:  Exporting vpsutil_net_io_counters ...
NOTICE:  Writing file: vpsutil_net_io_counters_0 ...
NOTICE:  Exporting vpsutil_processes ...
NOTICE:  Writing file: vpsutil_processes_0 ...
NOTICE:  Exporting vkpg_stat_activity ...
NOTICE:  Writing file: vkpg_stat_activity_0 ...
NOTICE:  Exporting vkpg_stat_database ...
NOTICE:  Writing file: vkpg_stat_database_0 ...
   export_full   
-----------------
 /tmp/centos.zip
```

The result is a zip file in which the output directory can be controlled by changing the directory parameter. The file name is the name of the system (result of uname -n).

The "daily" export is generally triggered on a regularly basis (every day).

For example, to trigger this kind of report each day at 5.00 AM:

```
0 5 * * * psql -d kairos -c "select export_relative_day(1)"
```

The parameter given to "export_relative_day" is the day computed from the current date. 0 means "today", 1 means "yesterday", ....

The same expression leads to different results every day.

Examples:

```
$ psql -d kairos -c "select export_relative_day(0)"
NOTICE:  Exporting vpsutil_cpu_times ...
NOTICE:  Writing file: vpsutil_cpu_times_0 ...
NOTICE:  Exporting vpsutil_virtual_memory ...
NOTICE:  Writing file: vpsutil_virtual_memory_0 ...
NOTICE:  Exporting vpsutil_swap_memory ...
NOTICE:  Writing file: vpsutil_swap_memory_0 ...
NOTICE:  Exporting vpsutil_disk_io_counters ...
NOTICE:  Writing file: vpsutil_disk_io_counters_0 ...
NOTICE:  Exporting vpsutil_net_io_counters ...
NOTICE:  Writing file: vpsutil_net_io_counters_0 ...
NOTICE:  Exporting vpsutil_processes ...
NOTICE:  Writing file: vpsutil_processes_0 ...
NOTICE:  Exporting vkpg_stat_activity ...
NOTICE:  Writing file: vkpg_stat_activity_0 ...
NOTICE:  Exporting vkpg_stat_database ...
NOTICE:  Writing file: vkpg_stat_database_0 ...
    export_relative_day     
----------------------------
 /tmp/centos_2017-06-29.zip
(1 row)

$ psql -d kairos -c "select export_relative_day(1)"
NOTICE:  Exporting vpsutil_cpu_times ...
NOTICE:  Exporting vpsutil_virtual_memory ...
NOTICE:  Exporting vpsutil_swap_memory ...
NOTICE:  Exporting vpsutil_disk_io_counters ...
NOTICE:  Exporting vpsutil_net_io_counters ...
NOTICE:  Exporting vpsutil_processes ...
NOTICE:  Exporting vkpg_stat_activity ...
NOTICE:  Exporting vkpg_stat_database ...
    export_relative_day     
----------------------------
 /tmp/centos_2017-06-30.zip
(1 row)

```

In case of "daily" export, the resulting file name contains the generated day as well as the system name.