#! /bin/bash
source venv/bin/activate
# virtualenv is now active.
#
echo "Start to backup database."
python dailybackupv2.py
echo "End of the job."