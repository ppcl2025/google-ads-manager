#!/usr/bin/env python3
"""
Memory Monitor for Google Ads Manager
This script helps monitor memory usage and identify potential memory leaks.
"""

import psutil
import time
import os
import gc
from datetime import datetime

class MemoryMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.memory_history = []
    
    def get_memory_usage(self):
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def log_memory(self, location=""):
        """Log current memory usage with timestamp and location."""
        memory_mb = self.get_memory_usage()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = {
            'timestamp': timestamp,
            'memory_mb': memory_mb,
            'location': location
        }
        
        self.memory_history.append(log_entry)
        
        print(f"[{timestamp}] Memory: {memory_mb:.2f} MB - {location}")
        
        # Warning if memory usage is high
        if memory_mb > 1000:  # 1GB threshold
            print(f"⚠️  WARNING: High memory usage detected: {memory_mb:.2f} MB")
        
        return memory_mb
    
    def force_garbage_collection(self):
        """Force garbage collection and log memory before/after."""
        print("🧹 Starting garbage collection...")
        before_memory = self.get_memory_usage()
        
        # Force garbage collection
        collected = gc.collect()
        
        after_memory = self.get_memory_usage()
        freed_memory = before_memory - after_memory
        
        print(f"✅ Garbage collection completed:")
        print(f"   - Objects collected: {collected}")
        print(f"   - Memory freed: {freed_memory:.2f} MB")
        print(f"   - Before: {before_memory:.2f} MB")
        print(f"   - After: {after_memory:.2f} MB")
        
        return freed_memory
    
    def get_memory_summary(self):
        """Get a summary of memory usage over time."""
        if not self.memory_history:
            return "No memory data recorded yet."
        
        memory_values = [entry['memory_mb'] for entry in self.memory_history]
        
        summary = {
            'total_entries': len(self.memory_history),
            'min_memory': min(memory_values),
            'max_memory': max(memory_values),
            'avg_memory': sum(memory_values) / len(memory_values),
            'current_memory': memory_values[-1],
            'memory_growth': memory_values[-1] - memory_values[0] if len(memory_values) > 1 else 0
        }
        
        return summary
    
    def print_summary(self):
        """Print a formatted memory summary."""
        summary = self.get_memory_summary()
        
        if isinstance(summary, str):
            print(summary)
            return
        
        print("\n" + "="*50)
        print("📊 MEMORY USAGE SUMMARY")
        print("="*50)
        print(f"Total measurements: {summary['total_entries']}")
        print(f"Current memory: {summary['current_memory']:.2f} MB")
        print(f"Minimum memory: {summary['min_memory']:.2f} MB")
        print(f"Maximum memory: {summary['max_memory']:.2f} MB")
        print(f"Average memory: {summary['avg_memory']:.2f} MB")
        print(f"Memory growth: {summary['memory_growth']:.2f} MB")
        
        if summary['memory_growth'] > 100:
            print("⚠️  WARNING: Significant memory growth detected!")
        elif summary['memory_growth'] > 50:
            print("⚠️  CAUTION: Moderate memory growth detected.")
        else:
            print("✅ Memory usage appears stable.")
        
        print("="*50)
    
    def export_history(self, filename="memory_log.txt"):
        """Export memory history to a file."""
        with open(filename, 'w') as f:
            f.write("Timestamp,Memory_MB,Location\n")
            for entry in self.memory_history:
                f.write(f"{entry['timestamp']},{entry['memory_mb']:.2f},{entry['location']}\n")
        print(f"📄 Memory history exported to {filename}")

def main():
    """Interactive memory monitoring."""
    monitor = MemoryMonitor()
    
    print("🔍 Google Ads Manager Memory Monitor")
    print("="*40)
    print("Commands:")
    print("  'log [location]' - Log current memory usage")
    print("  'gc' - Force garbage collection")
    print("  'summary' - Show memory summary")
    print("  'export' - Export memory history")
    print("  'quit' - Exit monitor")
    print("="*40)
    
    # Initial memory log
    monitor.log_memory("Monitor started")
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'quit' or command == 'exit':
                break
            elif command == 'gc':
                monitor.force_garbage_collection()
            elif command == 'summary':
                monitor.print_summary()
            elif command == 'export':
                monitor.export_history()
            elif command.startswith('log'):
                parts = command.split(' ', 1)
                location = parts[1] if len(parts) > 1 else "Manual log"
                monitor.log_memory(location)
            else:
                print("Unknown command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            print("\n\nExiting memory monitor...")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    # Final summary
    monitor.print_summary()

if __name__ == "__main__":
    main() 