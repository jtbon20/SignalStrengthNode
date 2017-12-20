## Simple Module to get the wifi-strength (as measured by
## dBm on a given interface for a specified network.

import sys
import subprocess

#TODO: change these as appropriate
interface = "wlp3s0"
network = ""


##Dictionary for collected data
data={"Name":get_name,
      "Signal":get_signal_level}

##getter methods
def get_name(cell):
    return matching_line(cell,"ESSID:")[1:-1]

def get_signal_level(cell):
    return matching_line(cell,"Quality=").split("Signal level=")[1]


##matching methods for parsing 
def matching_line(lines, keyword):
    """Returns the first matching line in a list of lines. See match()"""
    for line in lines:
        matching=match(line,keyword)
        if matching!=None:
            return matching
    return None

def match(line,keyword):
    """If the first part of line (modulo blanks) matches keyword,
    returns the end of that line. Otherwise returns None"""
    line=line.lstrip()
    length=len(keyword)
    if line[:length] == keyword:
        return line[length:]
    else:
        return None

def parse_cell(cell):
    """Gathers necessary data for each cell"""
    parsed_cell={}
    for key in data:
        rule=data[key]
        parsed_cell.update({key:rule(cell)})
    return parsed_cell
 

def getConnection():
    cells=[[]]
    parsed_cells=[]

    proc = subprocess.Popen(["iwlist", interface, "scan"],stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()

    for line in out.split("\n"):
        cell_line = match(line,"Cell ")
        if cell_line != None:
            cells.append([])
            line = cell_line[-27:]
        cells[-1].append(line.rstrip())

    for cell in cells[1:]:
        parsed_cells.append(parse_cell(cell))

    cell = list(filter(lambda d: d['Name']== network, parsed_cells))

    return cell[0]['Name'] + "," + cell[0]['Signal'].split(' ')[0]
