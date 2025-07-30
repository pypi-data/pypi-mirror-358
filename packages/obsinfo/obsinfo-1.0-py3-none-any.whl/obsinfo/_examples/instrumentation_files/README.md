This directory contains sample information files in several directories:

* the ``./subnetwork`` directory, which has files for each data collection
  campaign.
  
* the ``./instrumentation_bases`` directory, which contains files which represent an inventory of park instruments.
  
* the ``./sensors`` directory, which contains files which represent sensors.

* the ``./preamplifiers`` directory, which contains files which represent preamplifiers.

* the ``./dataloggers`` directory, which contains files which represent dataloggers

Each one has:

  * a ``responses`` subdirectory containing individual sensor, datalogger and filter stages. These in turn have:
  * a  ``filters`` subdirectory containing filters related to the stages.

The rest are auxiliary directories.

The information files can be in YAML or JSON format.


