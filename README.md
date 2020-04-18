# GfidChecker
GFID Checker for fix damaged files of gluster volume

### Installation

* [python3] - python3 is required for run the script.
* [gfid-resolver.sh] - Please download the script from https://gist.github.com/louiszuckerman/4392640, put it in same folder with the script

### Usage

  - Create log file of volume xxxx,yyyy
    - gfid-checker.py --log --vols xxxx,yyyy
  - Show damaged files of volume xxxx,yyyy
    - gfid-checker.py --s --vols xxxx,yyyy
  - Delete bad files, but only show without delete
    - gfid-checker.py --vols xxxx,yyyy --del_file
  - Delete bad files with confirm -y
    - gfid-checker.py --vols xxxx,yyyy --del_file -y
  - Delete gfid files, but only show without delete
    - gfid-checker.py --vols xxxx,yyyy --del_gfid
  - Delete gfid files with confirm -y
    - gfid-checker.py --vols xxxx,yyyy --del_gfid -y
