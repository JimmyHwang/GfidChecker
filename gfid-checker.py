#!/usr/bin/python
import subprocess
import sys, getopt
import os

VerboseFlag = False
ResolverFile = "./gfid-resolver.sh"
VolumeList = None
YesFlag = False           # Confirm for --del_file --del_gfid

def ExecCommand(cmds):
  process = subprocess.Popen(cmds.split(), stdout=subprocess.PIPE,universal_newlines=True)
  output, error = process.communicate()
  return output

def Resolver(brick_folder, gfid):
  global VerboseFlag
  if VerboseFlag:
    print("gfid = %s" % (gfid))
  cmds = "%s %s %s" % (ResolverFile, brick_folder, gfid)
  output = ExecCommand(cmds)
  return output
  
def ShowFiles(log_fn):
  brick_path = ""
  fp = open(log_fn, "r")
  count = 0
  while True:
    line = fp.readline()
    if line == "":
      break
    line = line.rstrip()
    count = count + 1  
    #
    # Parse Brick & gfid
    #
    if "Brick" in line:
      p = line.find(":")
      brick_path = line[p+1:]      
    elif "Status:" in line:
      brick_path = ""
    elif "gfid:" in line:
      p = line.find(":")
      gfid = line[p+1:-1]
      if brick_path != "":
        info = Resolver(brick_path, gfid)
        print(info)
      else:
        print("Error: brick_path is NULL")
  fp.close()
   
def DeleleFiles(log_fn):
  global VerboseFlag
  global YesFlag

  hint_flag = False
  brick_path = ""
  fp = open(log_fn, "r")
  count = 0
  while True:
    line = fp.readline()
    if line == "":
      break
    line = line.rstrip()
    count = count + 1  
    #
    # Parse Brick & gfid
    #
    if "Brick" in line:
      p = line.find(":")
      brick_path = line[p+1:]
    elif "Status:" in line:
      brick_path = ""
    elif "gfid:" in line:
      p = line.find(":")
      gfid = line[p+1:-1]
      if brick_path != "":
        output = Resolver(brick_path, gfid)
        if "File:" in output:
          p = output.find("/")
          fn = output[p:].strip()
          if fn != "":
            print("Delete [%s]" % fn)        
            if YesFlag:
              if os.path.exists(fn):
                os.remove(fn)
              else:
                print("Error: [%s] not exist" % (fn))              
            else:
              hint_flag = True
      else:
        print("Error: brick_path is NULL")
  fp.close()
  #
  # Hint if no confirm for delete
  #
  if hint_flag:
    print("Info: -y for confirm execute delete")
    
def FindGfidFiles(folder, fn):
  result = []
  for root, dirs, files in os.walk(folder):
    for name in files:
      if name == fn:
        result.append(os.path.join(root, name))
  return result

def DeleleGfid(log_fn):
  global VerboseFlag
  global YesFlag
  
  hint_flag = False
  brick_path = ""
  fp = open(log_fn, "r")
  count = 0
  while True:
    line = fp.readline()
    if line == "":
      break
    line = line.rstrip()
    count = count + 1  
    #
    # Parse Brick & gfid
    #
    if "Brick" in line:
      p = line.find(":")
      brick_path = line[p+1:]
    elif "Status:" in line:
      brick_path = ""
    elif "gfid:" in line:
      p = line.find(":")
      gfid = line[p+1:-1]
      if brick_path != "":
        output = Resolver(brick_path, gfid)
        if "File:" in output:
          p = output.find("==")
          gfid = output[:p].strip()
          if VerboseFlag:
            print("Info: gfid [%s]" % gfid)          
          list = FindGfidFiles(brick_path, gfid)
          if len(list) > 0:
            for fn in list:
              print("Delete [%s]" % fn)        
              if YesFlag:
                if os.path.exists(fn):
                  os.remove(fn)
                else:
                  print("Error: [%s] not exist" % (fn))
              else:
                hint_flag = True
      else:
        print("Error: brick_path is NULL")
  fp.close()
  #
  # Hint if no confirm for delete
  #
  if hint_flag:
    print("Info: -y for confirm execute delete")
  
def WriteTextToFile(fn, data):
  fp = open(fn,"w") 
  fp.write(data) 
  fp.close()

def PrintHelp():
  print('Create log file of volume xxxx,yyyy')
  print('  gfid-checker.py --log --vols xxxx,yyyy')
  print('Show damaged files of volume xxxx,yyyy')
  print('  gfid-checker.py --s --vols xxxx,yyyy')
  print('Delete bad files, but only show wihtou delete')
  print('  gfid-checker.py --vols xxxx,yyyy --del_file')
  print('Delete bad files with confirm -y')
  print('  gfid-checker.py --vols xxxx,yyyy --del_file -y')
  print('Delete gfid files with confirm -y')
  print('  gfid-checker.py --vols xxxx,yyyy --del_gfid -y')

def main(argv):
  global VerboseFlag
  global YesFlag
  
  log_flag = False
  show_flag = False
  del_file_flag = False
  del_gfid_flag = False
  
  try:
    opts, args = getopt.getopt(argv,"vhdsyi:o:",["vols=", "log", "show", "del_file", "del_gfid", "yes"])
  except getopt.GetoptError:
    PrintHelp()
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      PrintHelp()      
      sys.exit()
    elif opt in ("-v"):
      VerboseFlag = True
    elif opt in ("--del_file"):
      del_file_flag = True
    elif opt in ("--del_gfid"):
      del_gfid_flag = True
    elif opt in ("-s", "--show"):
      show_flag = True
    elif opt in ("-y", "--yes"):
      YesFlag = True
    elif opt in ("--log"):
      log_flag = True
    elif opt in ("--vols"):
      VolumeList = arg.split(",")       
  #
  # Command Process
  #
  if len(VolumeList) == 0:
    print("Error: --vols is requied")
    exit()
    
  if log_flag == True:
    for vol in VolumeList: 
      log_fn = "%s.log" % (vol)
      cmds = "gluster volume heal %s info" % (vol)
      data = ExecCommand(cmds)
      WriteTextToFile(log_fn, data)

  if show_flag == True:
    for vol in VolumeList: 
      log_fn = "%s.log" % (vol)
      ShowFiles(log_fn)
   
  if del_file_flag == True:
    for vol in VolumeList: 
      log_fn = "%s.log" % (vol)
      DeleleFiles(log_fn)

  if del_gfid_flag == True:
    for vol in VolumeList: 
      log_fn = "%s.log" % (vol)
      DeleleGfid(log_fn)
  
if __name__ == '__main__':
   main(sys.argv[1:])
