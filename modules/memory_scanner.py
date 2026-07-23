#!/usr/bin/env python3
"""Memory scanner module for searching and editing process memory"""

import os
import sys
import struct
import ctypes

class MemoryScanner:
    """Scan and search through process memory"""
    
    def __init__(self, proc_manager, pid):
        self.proc_manager = proc_manager
        self.pid = pid
        self.last_results = []
        self.mem_fd = None
        
        if pid in proc_manager.attached_processes:
            self.mem_fd = proc_manager.attached_processes[pid]['mem_fd']
    
    def read_memory_region(self, address, size):
        """Read raw bytes from process memory"""
        if not self.mem_fd:
            raise Exception("Not attached to process")
        
        try:
            os.lseek(self.mem_fd, address, os.SEEK_SET)
            data = os.read(self.mem_fd, size)
            return data
        except Exception as e:
            raise Exception(f"Failed to read memory at {hex(address)}: {e}")
    
    def write_memory(self, address, value, data_type='int'):
        """Write a value to process memory"""
        if not self.mem_fd:
            raise Exception("Not attached to process")
        
        try:
            if data_type == 'int':
                data = struct.pack('<i', value)
            elif data_type == 'float':
                data = struct.pack('<f', value)
            elif data_type == 'double':
                data = struct.pack('<d', value)
            elif data_type == 'long':
                data = struct.pack('<q', value)
            elif data_type == 'short':
                data = struct.pack('<h', value)
            elif data_type == 'byte':
                data = struct.pack('<B', value)
            else:
                raise ValueError(f"Unknown data type: {data_type}")
            
            os.lseek(self.mem_fd, address, os.SEEK_SET)
            os.write(self.mem_fd, data)
            return True
        except Exception as e:
            raise Exception(f"Failed to write to {hex(address)}: {e}")
    
    def search_value(self, value, data_type='int'):
        """Search for a value across all writable memory regions"""
        results = []
        regions = self.proc_manager.get_memory_regions(self.pid)
        
        # Format for struct unpacking
        if data_type == 'int':
            fmt = '<i'
            size = 4
        elif data_type == 'float':
            fmt = '<f'
            size = 4
        elif data_type == 'double':
            fmt = '<d'
            size = 8
        elif data_type == 'long':
            fmt = '<q'
            size = 8
        elif data_type == 'short':
            fmt = '<h'
            size = 2
        else:
            raise ValueError(f"Unknown data type: {data_type}")
        
        target_bytes = struct.pack(fmt, value)
        
        print(f"\n[+] Searching for {value} (type: {data_type}) across memory regions...")
        
        total_size = 0
        scanned = 0
        
        for region in regions:
            if not region['readable']:
                continue
            total_size += region['size']
        
        for i, region in enumerate(regions):
            if not region['readable']:
                continue
            
            # Skip very large anonymous regions (>100MB for speed)
            if region['size'] > 100 * 1024 * 1024 and not region['writable']:
                continue
            
            try:
                # Read in chunks
                chunk_size = min(region['size'], 1024 * 1024)  # 1MB chunks
                addr = region['start']
                
                while addr < region['end']:
                    to_read = min(chunk_size, region['end'] - addr)
                    data = self.read_memory_region(addr, to_read)
                    
                    # Search for pattern
                    offset = 0
                    while True:
                        pos = data.find(target_bytes, offset)
                        if pos == -1:
                            break
                        
                        result_addr = addr + pos
                        
                        try:
                            val = struct.unpack_from(fmt, data, pos)[0]
                            results.append({
                                'address': result_addr,
                                'value': val,
                                'region': region['pathname'] if region['pathname'] else '[anonymous]',
                                'perms': region['perms']
                            })
                        except:
                            pass
                        
                        offset = pos + 1
                    
                    scanned += to_read
                    addr += to_read
                    
                    # Progress indicator
                    pct = (scanned * 100) // max(total_size, 1)
                    sys.stdout.write(f"\r  Progress: {pct}% ({scanned // 1024 // 1024}MB scanned, {len(results)} matches)")
                    sys.stdout.flush()
                    
            except Exception as e:
                continue
        
        print()  # New line after progress
        self.last_results = results
        return results
    
    def refine_search(self, value, data_type='int'):
        """Refine previous search results with a new value"""
        if not self.last_results:
            return []
        
        if data_type == 'int':
            fmt = '<i'
            size = 4
        elif data_type == 'float':
            fmt = '<f'
            size = 4
        else:
            raise ValueError(f"Unsupported type: {data_type}")
        
        new_results = []
        
        print(f"\n[+] Refining search to {value} (from {len(self.last_results)} results)...")
        
        for i, res in enumerate(self.last_results):
            sys.stdout.write(f"\r  Checking result {i+1}/{len(self.last_results)}")
            sys.stdout.flush()
            
            try:
                data = self.read_memory_region(res['address'], size)
                current_val = struct.unpack(fmt, data)[0]
                
                if current_val == value:
                    new_results.append(res)
            except:
                continue
        
        print()  # New line
        self.last_results = new_results
        return new_results
