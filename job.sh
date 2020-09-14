#! /bin/bash
source venv/bin/activate
# virtualenv is now active.
#
echo "Start to backup database."
python dailybackup.py
echo "End of the job."