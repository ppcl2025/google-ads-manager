# Memory Management Guide for Google Ads Manager

## Overview

This guide helps you understand and resolve memory issues in the Google Ads Manager application. The app has been updated with comprehensive memory management features to prevent the 20GB+ memory usage you were experiencing.

## Memory Issues Identified and Fixed

### 1. **Large Data Accumulation in Session State**
**Problem**: The app was storing large datasets in `st.session_state` without proper cleanup, causing memory to grow indefinitely.

**Solution**: 
- Added automatic session state cleanup on app startup
- Implemented data size limits for DataFrames
- Added manual cleanup buttons for users

### 2. **Inefficient Caching Strategy**
**Problem**: Cache TTLs were too long (30 minutes to 1 hour), causing old data to accumulate.

**Solution**:
- Reduced cache TTLs to 5-10 minutes
- Added memory monitoring to cached functions
- Implemented automatic cache clearing

### 3. **Large DataFrame Operations**
**Problem**: Multiple DataFrame copies were being created without cleanup, especially in performance analysis.

**Solution**:
- Added DataFrame size limits (max 1000 rows)
- Implemented explicit DataFrame cleanup with `del` statements
- Added garbage collection after heavy operations

### 4. **PDF Generation Memory Issues**
**Problem**: Large PDF buffers weren't being properly released.

**Solution**:
- Added proper buffer cleanup in PDF generation
- Implemented memory monitoring during PDF creation

## New Memory Management Features

### Memory Monitoring Dashboard
The app now displays current memory usage at the top of the interface:
```
💾 Current Memory Usage: 245.3 MB
```

### Memory Management Buttons
- **🧹 Clear Cache**: Clears all cached data and session state
- **🔄 Force GC**: Forces garbage collection to free memory

### Automatic Memory Management
- Memory usage logging at key points in the application
- Automatic DataFrame size limiting
- Session state cleanup on app startup
- Garbage collection after heavy operations

## How to Use Memory Management

### 1. **Monitor Memory Usage**
- Watch the memory usage display at the top of the app
- If it exceeds 1GB, consider using the cleanup buttons

### 2. **Regular Cleanup**
- Use the "🧹 Clear Cache" button periodically
- Use "🔄 Force GC" after heavy operations like performance analysis

### 3. **Best Practices**
- Avoid leaving the app running for extended periods without cleanup
- Close and restart the app if memory usage gets high
- Use the memory monitor script for detailed tracking

## Memory Monitor Script

A standalone memory monitoring script (`memory_monitor.py`) is included for detailed memory tracking:

```bash
python memory_monitor.py
```

### Commands:
- `log [location]` - Log current memory usage
- `gc` - Force garbage collection
- `summary` - Show memory summary
- `export` - Export memory history
- `quit` - Exit monitor

## Troubleshooting Memory Issues

### If Memory Usage is Still High:

1. **Check for Large Datasets**
   - Look at the performance analysis data size
   - Consider reducing the date range
   - Limit the number of sub-accounts analyzed

2. **Monitor with the Memory Script**
   ```bash
   python memory_monitor.py
   ```

3. **Restart the Application**
   - Close the Streamlit app completely
   - Restart with: `streamlit run google_ads_manager.py`

4. **Check System Resources**
   - Monitor overall system memory usage
   - Close other memory-intensive applications

### Memory Usage Thresholds:
- **Normal**: < 500 MB
- **Warning**: 500 MB - 1 GB
- **High**: 1 GB - 2 GB
- **Critical**: > 2 GB (restart recommended)

## Performance Analysis Memory Optimization

The performance analysis feature has been optimized:

1. **Limited Query Results**: Reduced from 1000 to 500 records per query
2. **DataFrame Limits**: Max 100 keywords, 200 search terms per campaign
3. **Automatic Cleanup**: DataFrames are deleted after display
4. **Garbage Collection**: Forced after processing

## Configuration Options

You can adjust memory limits in the `MemoryManager` class:

```python
# In google_ads_manager.py
class MemoryManager:
    @staticmethod
    def limit_dataframe_size(df: pd.DataFrame, max_rows: int = 1000) -> pd.DataFrame:
        # Adjust max_rows as needed
```

## Logging and Debugging

Memory usage is logged to the application logs. Look for entries like:
```
Memory usage at get_keywords_analysis_start: 245.3 MB
Memory usage at get_keywords_analysis_end: 312.7 MB
```

## Prevention Tips

1. **Regular Restarts**: Restart the app every few hours of heavy use
2. **Monitor Usage**: Keep an eye on the memory display
3. **Use Cleanup Buttons**: Use them proactively, not just when issues occur
4. **Limit Data**: Use smaller date ranges and fewer accounts when possible
5. **Close Unused Tabs**: Close browser tabs when not actively using them

## Emergency Memory Recovery

If the app becomes unresponsive due to memory:

1. **Force Close**: Close the browser tab and terminal
2. **Kill Process**: If needed, kill the Python process
3. **Restart**: Restart the application
4. **Monitor**: Use the memory monitor to track usage

## Support

If you continue to experience memory issues:

1. Run the memory monitor script and export the logs
2. Note the specific operations that cause high memory usage
3. Check the application logs for memory warnings
4. Consider reducing the scope of operations (fewer accounts, shorter date ranges)

## Technical Details

### Memory Management Implementation:
- **psutil**: For memory monitoring
- **gc**: For garbage collection
- **Session State Cleanup**: Automatic and manual
- **DataFrame Limits**: Size-based restrictions
- **Cache Management**: Reduced TTLs and monitoring

### Memory Leak Prevention:
- Explicit object deletion
- Regular garbage collection
- Session state cleanup
- DataFrame size limiting
- Buffer management in PDF generation 