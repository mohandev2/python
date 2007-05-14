#!/usr/bin/env python
#
# (C) Copyright IBM Corp. 2006
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. This
# file and program are licensed under a BSD style license. See
# the Copying file included with the OpenHPI distribution for
# full licensing terms.
#
"""
Read/Set analog fan controls

This is a port from the C version of hpifan over to Python.
The C version comes bundled with the OpenHPI package.

Author(s):
	Renier Morales <renier@openhpi.org>
"""

import sys
from optparse import OptionParser
from openhpi import *

parser = OptionParser()
parser.add_option('-s',
		  '--set',
		  dest='fan_speed',
		  help='set the fan speed level (also sets manual mode)',
		  metavar='<fan speed>')
parser.add_option('-a',
		  '--auto',
		  dest='auto_mode',
		  action='store_true',
		  help='sets the fan to auto mode')

options, args = parser.parse_args()

def get_fan_speed(sid, rid, num):
	state = SaHpiCtrlStateT()
	error, mode = saHpiControlGet(sid, rid, num, state)
	if error != SA_OK:
		print 'Cannot get fan state: %s' % oh_lookup_error(error)
		return error
	
	if state.Type != SAHPI_CTRL_TYPE_ANALOG:
		print 'Cannot handle non-analog fan state!'
		return SA_ERR_HPI_ERROR

	speed = state.StateUnion.Analog

	return SA_OK, speed, mode

def set_fan(sid, rid, num, speed=None):
	state = SaHpiCtrlStateT()
	state.Type = SAHPI_CTRL_TYPE_ANALOG
	mode = SAHPI_CTRL_MODE_AUTO
	if speed:
		state.StateUnion.Analog = speed
		mode = SAHPI_CTRL_MODE_MANUAL
	
	error = saHpiControlSet(sid, rid, num, mode, state)
	if error != SA_OK:
		print 'Cannot set fan state or mode: (%s, %s)' % (oh_lookup_error(error),
								  oh_lookup_ctrlmode(mode))
		return error

	return SA_OK

def do_fan(sid, rid, rdr):
	ctrl_rec = rdr.RdrTypeUnion.CtrlRec
	print '\tFan: Num %d, Id "%s"' % (ctrl_rec.Num, rdr.IdString.Data)
	if ctrl_rec.Type != SAHPI_CTRL_TYPE_ANALOG:
		print 'Cannot handle non analog fan controls!'
		return 0
	
	print '\t\tMin       %d' % ctrl_rec.TypeUnion.Analog.Min
	print '\t\tMax       %d' % ctrl_rec.TypeUnion.Analog.Max
	print '\t\tDefault   %d' % ctrl_rec.TypeUnion.Analog.Default

	error, fan_speed, ctrl_mode = get_fan_speed(sid, rid, ctrl_rec.Num)
	if error != SA_OK:
		return 0
	
	print '\t\tCurrent   %d (%s)' % (fan_speed, oh_lookup_ctrlmode(ctrl_mode))
	
	if options.fan_speed:
		fan_speed = int(options.fan_speed)
		if (fan_speed < ctrl_rec.TypeUnion.Analog.Min or
		    fan_speed > ctrl_rec.TypeUnion.Analog.Max):
			print 'Fan speed %d is out of range [%d, %d] !' % (
				fan_speed,
				ctrl_rec.TypeUnion.Analog.Min,
				ctrl_rec.TypeUnion.Analog.Max)
			return 0

		error = set_fan(sid, rid, ctrl_rec.Num, fan_speed)
		if error != SA_OK:
			return 0
	
	elif options.auto_mode:
		error = set_fan(sid, rid, ctrl_rec.Num)
		if error != SA_OK:
			return 0
	
	else:
		return 0

	error, fan_speed, ctrl_mode = get_fan_speed(sid, rid, ctrl_rec.Num)
	if error != SA_OK:
		return 0

	print '\t\tNew speed %d (%s) set' % (fan_speed,
					     oh_lookup_ctrlmode(ctrl_mode))
	return 0
	
def discover_domain(sid):
	found = 0
	nextid = SAHPI_FIRST_ENTRY
	res = SaHpiRptEntryT()
	while nextid != SAHPI_LAST_ENTRY:
		currid = nextid
		error, nextid = saHpiRptEntryGet(sid, currid, res)
		if error != SA_OK:
			print 'saHpiRptEntryGet: %s' % oh_lookup_error(error)
			return 1
		
		if (not(res.ResourceCapabilities & SAHPI_CAPABILITY_RDR) or
		    not(res.ResourceCapabilities & SAHPI_CAPABILITY_CONTROL)):
		    	continue
		
		nextid2 = SAHPI_FIRST_ENTRY
		rid = res.ResourceId
		rdr = SaHpiRdrT()
		while nextid2 != SAHPI_LAST_ENTRY:
			currid2 = nextid2
			error, nextid2 = saHpiRdrGet(sid, rid, currid2, rdr)
			if error != SA_OK:
				print 'saHpiRdrGet: %s' % oh_lookup_error(error)
				return 1
			
			if rdr.RdrType != SAHPI_CTRL_RDR:
				continue
			
			if (rdr.RdrTypeUnion.CtrlRec.OutputType !=
			    SAHPI_CTRL_FAN_SPEED):
				continue
			
			oh_print_ep(res.ResourceEntity, 0)
			do_fan(sid, rid, rdr)
			found += 1

	if found == 0:
		print 'No controllable fans found.'

	return 0

# main()
error, sid = saHpiSessionOpen(SAHPI_UNSPECIFIED_DOMAIN_ID, None)
if error != SA_OK:
	print 'saHpiSessionOpen: %s' % oh_lookup_error(error)
	sys.exit(1)

error = saHpiDiscover(sid)
if error != SA_OK:
	print 'saHpiDiscover: %s' % oh_lookup_error(error)
	sys.exit(1)

rc = discover_domain(sid)
error = saHpiSessionClose(sid)
if error != SA_OK:
	print 'saHpiSessionClose: %s' % oh_lookup_error(error)

sys.exit(rc)

