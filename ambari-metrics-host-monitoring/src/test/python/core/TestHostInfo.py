#!/usr/bin/env python

'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import logging
from host_info import HostInfo

from unittest import TestCase
from mock.mock import patch

logger = logging.getLogger()

class TestHostInfo(TestCase):

  @patch("psutil.cpu_count")
  @patch("os.getloadavg")
  @patch("psutil.cpu_times_percent")
  def testCpuTimes(self, cp_mock, avg_mock, count_mock):
    count_mock.return_value = 1

    cp = cp_mock.return_value
    cp.user = 0.1
    cp.system = 0.1
    cp.idle = 0.7
    cp.nice = 0.1
    cp.iowait = 0
    cp.irq = 0
    cp.softirq = 0

    avg_mock.return_value  = [13, 13, 13]
    
    hostinfo = HostInfo()
    
    cpu = hostinfo.get_cpu_times()
    
    self.assertAlmostEqual(cpu['cpu_user'], 10)
    self.assertAlmostEqual(cpu['cpu_system'], 10)
    self.assertAlmostEqual(cpu['cpu_idle'], 70)
    self.assertAlmostEqual(cpu['cpu_nice'], 10)
    self.assertAlmostEqual(cpu['cpu_wio'], 0)
    self.assertAlmostEqual(cpu['cpu_intr'], 0)
    self.assertAlmostEqual(cpu['cpu_sintr'], 0)
    self.assertEqual(cpu['load_one'], 13)
    self.assertEqual(cpu['load_five'], 13)
    self.assertEqual(cpu['load_fifteen'], 13)
    
  @patch("psutil.disk_usage")
  @patch("psutil.disk_partitions")
  @patch("psutil.swap_memory")
  @patch("psutil.virtual_memory")
  def testMemInfo(self, vm_mock, sw_mock, dm_mock, du_mock):
    
    vm = vm_mock.return_value
    vm.free = 2312043
    vm.shared = 1243
    vm.buffers = 23435
    vm.cached = 23545
    
    sw = sw_mock.return_value
    sw.free = 2341234
    
    hostinfo = HostInfo()
    
    cpu = hostinfo.get_mem_info()
    
    self.assertAlmostEqual(cpu['mem_free'], 2257)
    self.assertAlmostEqual(cpu['mem_shared'], 1)
    self.assertAlmostEqual(cpu['mem_buffered'], 22)
    self.assertAlmostEqual(cpu['mem_cached'], 22)
    self.assertAlmostEqual(cpu['swap_free'], 2286)


  @patch("psutil.process_iter")
  def testProcessInfo(self, process_iter_mock):

    def side_effect_running():
      return 'running'

    class Proc:
      def status(self):
        return 'some_status'

    p1 = Proc()
    p1.status = side_effect_running
    p2 = Proc()
    p2.status = side_effect_running
    p3 = Proc()
    p4 = Proc()

    processes = [p1, p2, p3, p4]

    process_iter_mock.return_value = processes

    hostinfo = HostInfo()

    procs = hostinfo.get_process_info()

    self.assertEqual(procs['proc_run'], 2)
    self.assertEqual(procs['proc_total'], len(processes))

  @patch("psutil.disk_usage")
  @patch("psutil.disk_partitions")
  def testCombinedDiskUsage(self, dp_mock, du_mock):
    
    dp_mock.__iter__.return_value = ['a', 'b', 'c']
    
    hostinfo = HostInfo()
    
    cdu = hostinfo.get_combined_disk_usage()
    self.assertEqual(cdu['disk_total'], "0.00")
    self.assertEqual(cdu['disk_used'], "0.00")
    self.assertEqual(cdu['disk_free'], "0.00")
    self.assertEqual(cdu['disk_percent'], "0.00")
