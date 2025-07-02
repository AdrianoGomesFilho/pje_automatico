# PJE Automático - Suspend/Hibernate Solution

## Problem Solved ✅

**Issue**: When the PC was suspended or hibernated, the PJE Automático program would close/crash.

**Root Cause**: The program's continuous polling loop (checking clipboard every second) would be paused during system suspend, and browser connections would be lost, causing the program to terminate.

## Solution Implemented

### 1. Windows Power Management Integration
- Added Windows API integration using `pywin32` library
- Program now receives Windows power management notifications
- Properly handles `WM_POWERBROADCAST` messages for suspend/resume events

### 2. Smart Browser Session Management
- Detects when browser sessions become invalid
- Distinguishes between temporary connection issues and actual browser closure
- Implements graceful recovery mechanisms

### 3. Improved Error Handling
- Browser session errors are now categorized and handled appropriately
- Program continues running when possible instead of crashing
- Clean exit only when browser is actually closed by user

## How It Works

### During Suspend/Hibernate:
1. **Power Manager** detects system suspend event
2. **Monitoring loops** pause their operations
3. **State is preserved** instead of terminating

### During Resume:
1. **Power Manager** detects system resume event  
2. **Connection testing** verifies browser and clipboard access
3. **Operations resume** normally with restored connections
4. **Time gap detection** identifies potential suspend/resume cycles

### Browser Connection Recovery:
1. **Session validation** checks if WebDriver connection is still valid
2. **Process monitoring** verifies Chrome process is still running
3. **Smart retry logic** attempts recovery before giving up
4. **Clean notifications** inform user of actual program termination

## Usage Notes

- ✅ **Suspend/Hibernate**: Program now continues running after system wake-up
- ✅ **Browser Connection Issues**: Automatic detection and recovery
- ✅ **Clean Exit**: Proper notification when browser is actually closed
- ✅ **Better Logging**: Detailed messages help understand what's happening

## Technical Details

### New Dependencies
```
pywin32>=227  # Windows power management APIs
```

### Key Components Added
- `PowerManager` class: Handles Windows power events
- Enhanced error detection: Categorizes browser session vs. other errors
- Recovery mechanisms: Attempts to restore connections after disruption
- Improved monitoring: Better browser process and session validation

### Log Messages You'll See
- `[PowerManager] System is suspending` - System going to sleep
- `[PowerManager] System resumed` - System waking up
- `[Monitor] Browser session invalid` - Temporary browser issue detected
- `[Clipboard] Systems restored after resume` - Successful recovery after wake-up

This solution ensures PJE Automático remains functional even when your computer goes to sleep, providing a much more reliable user experience.
