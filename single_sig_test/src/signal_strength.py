#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Revision $Id$

## Signal_strength that publishes std_msgs/String messages about the
## dBm (deciBels per milliwat, a common measure of wifi signal strength)
## at a constant rate to the 'signal_strength' topic.

import time
import rospy
from std_msgs.msg import String
import sys
import subprocess

##change these
interface = "wlp3s0"
network = ""


def sigStrength():
    pub = rospy.Publisher('signal_strength', String, queue_size=10)
    rospy.init_node('signal_strength', anonymous=True)
    rate = rospy.Rate(.2) # 1hz (potentially slow in future)
    while not rospy.is_shutdown():
	strength = "null,null"  #preset to impossible value to detect failures

        strength = testConnection()
        rospy.loginfo(strength) #logs to computer
        pub.publish(strength) #publishes to signal_strength

        rate.sleep()

##getter methods
def get_name(cell):
    return matching_line(cell,"ESSID:")[1:-1]

def get_signal_level(cell):
    return matching_line(cell,"Quality=").split("Signal level=")[1]

##Dictionary for collected data
data={"Name":get_name,
      "Signal":get_signal_level}

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


def testConnection():
    cells=[[]]
    parsed_cells=[]

    proc = subprocess.Popen(["sudo","iwlist", interface, "scan"],stdout=subprocess.PIPE, universal_newlines=True)
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

if __name__ == '__main__':
    try:
        sigStrength()
    except rospy.ROSInterruptException:
        pass
