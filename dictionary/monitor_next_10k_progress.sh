#!/bin/bash
# Monitor all next_10k dictionary workers in real-time

cd "$(dirname "$0")"

while true; do
    clear
    echo "============================================================"
    echo "Dictionary Build Progress Monitor (Next 10K: words 10,001-20,000)"
    echo "============================================================"
    echo ""
    
    # Dynamically find all worker logs
    found=0
    for log_file in german_english_dict_next_10k_worker_*.log; do
        [ -f "$log_file" ] || continue
        found=$((found + 1))
        
        # Extract worker number from filename
        worker_num=$(echo "$log_file" | grep -o 'worker_[0-9]*' | grep -o '[0-9]*')
        
        # Get last processed word line
        last_line=$(grep "Processing:" "$log_file" | tail -1)
        # Get progress stats if available
        progress=$(grep "Progress:" "$log_file" | tail -1)
        # Check if completed
        completed=$(grep "completed:" "$log_file" | tail -1)
        
        echo "Worker $worker_num:"
        if [ -n "$completed" ]; then
            echo "  ✅ $completed"
        else
            if [ -n "$last_line" ]; then
                echo "  $last_line"
            fi
            if [ -n "$progress" ]; then
                echo "  $progress"
            fi
        fi
        echo ""
    done
    
    if [ $found -eq 0 ]; then
        echo "No worker logs found yet."
        echo "Run launch_next_10k_build.py first."
        echo ""
    fi
    
    # Check if workers are still running
    running=$(ps aux | grep "build_next_10k_dictionary.py" | grep -v grep | wc -l | tr -d ' ')
    total_completed=$(grep -l "completed:" german_english_dict_next_10k_worker_*.log 2>/dev/null | wc -l | tr -d ' ')
    
    echo "============================================================"
    echo "Active workers: $running | Completed: $total_completed/$found"
    
    if [ "$running" -eq 0 ] && [ "$found" -gt 0 ]; then
        echo ""
        echo "🎉 All workers finished! Run: python3 merge_to_20k.py"
    fi
    
    echo "Press Ctrl+C to stop monitoring"
    echo "============================================================"
    
    sleep 5
done
