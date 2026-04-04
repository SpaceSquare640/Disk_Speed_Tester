================================================================================
  DISK I/O SPEED TESTER  —  README
  Version : 3.3
  File    : Disk_Speed_Tester.py
================================================================================


OVERVIEW
--------
Disk I/O Speed Tester is a cross-platform Python application that benchmarks
the sequential read and write throughput of your storage drives.  Results are
displayed in real-time inside a clean dark-themed PyQt5 GUI, and can
optionally be forwarded to a Discord channel via a Webhook in a rich,
structured embed format.

A full test report can be downloaded at any time via a native file-save
dialog, or configured to download automatically after every test completes.


FEATURES
--------
  * Sequential write-speed test  (data written to temp file, fsync'd)
  * Sequential read-speed test   (pre-written temp file, 1 MiB chunks)
  * Test a single selected drive or all detected drives in one pass
  * Live progress bars and MB/s readout updated every 1 MiB
  * Discord Webhook integration with detailed, colour-coded embeds
  * Live language switching — English, Traditional Chinese, Simplified Chinese
    switch instantly with no restart required
  * Persistent settings (language, Webhook URL) stored between sessions
  * Drive info panel: capacity, used/free space, filesystem type
  * Results History tab with inline preview
  * Download Report button - save a full detailed report to any location
    via a native OS file-save dialog
  * Auto-download option - automatically prompt to save report after each
    test completes
  * Fully self-contained single-file script  -  no external assets needed


REQUIREMENTS
------------
  Python   3.8 or later  (https://www.python.org/)

  Third-party libraries:
    PyQt5    >= 5.15   - GUI framework
    psutil   >= 5.9    - Cross-platform disk/partition info
    requests >= 2.28   - Discord Webhook HTTP calls

  Install all dependencies in one command:
    pip install PyQt5 psutil requests


INSTALLATION
------------
  1. Clone or download this repository.

  2. (Optional) Create and activate a virtual environment:
       python -m venv .venv
       Windows     : .venv\Scripts\activate
       macOS/Linux : source .venv/bin/activate

  3. Install dependencies:
       pip install PyQt5 psutil requests

  4. Run the application:
       python Disk_Speed_Tester.py


USAGE
-----
  Speed Test Tab
  --------------
  1. Select a drive from the drop-down (click "Refresh Drives" if needed).
  2. Set the test file size (default: 100 MB; larger = more accurate).
  3. Click "Test Selected Drive" or "Test All Drives".
  4. Watch the live progress bars and speed readouts.
  5. Results appear in the table below when the test finishes.

  Changing Language
  -----------------
  * Open the Settings tab.
  * Under "Language", select English, Traditional Chinese (繁體中文), or
    Simplified Chinese (简体中文) from the drop-down.
  * The entire UI — all tabs, buttons, labels, group boxes, table headers,
    and status bar — switches immediately with no restart required.
  * The chosen language is saved and restored automatically on next launch.

  Downloading the Test Report
  ---------------------------
  * Click "Download Report" (highlighted button below the results table)
    at any time after running at least one test.
  * A native OS file-save dialog appears - choose any folder and filename.
  * The report is saved as a UTF-8 plain-text (.txt) file.
  * Tick "Auto-download report after test" to be prompted automatically
    every time a test finishes.

  The downloaded report contains:
    - Generated timestamp
    - System information (OS, Python version)
    - Webhook configuration (enabled/disabled status + full URL)
    - Per-drive section:
        Drive name and device ID / path
        Mount point
        Storage protocol (NVMe PCIe, SATA, USB, Network, etc.)
        File system type
        Total capacity  (GB and MB)
        Used space      (GB and MB)
        Free space      (GB and MB)
        Usage percentage
    - Test results per drive:
        Write speed  (MB/s) + performance rating
        Read speed   (MB/s) + performance rating
        Average speed (MB/s)
        Write elapsed time (s)
        Read elapsed time  (s)
        Read/Write speed ratio
        Test start and completion timestamps
    - Multi-drive ranked summary table (when testing all drives)

  Drive Info Tab
  --------------
  Shows all detected partitions with capacity, usage, and filesystem type.

  Results History Tab
  -------------------
  Inline preview of all completed test results in the current session.
  Use "Export to TXT" to save to the system temp folder automatically,
  or use "Download Report" to choose where to save.

  Settings Tab
  ------------
  Webhook URL  -  Paste your Discord Webhook URL, click Save.
                  Enable / disable the feature with the checkbox.
                  Click "Test Connection" to verify before running tests.

  Language     -  Choose English, Traditional Chinese, or Simplified Chinese.
                  UI updates instantly — no restart needed.


DISCORD WEBHOOK SETUP
---------------------
  1. Open your Discord server settings.
  2. Go to  Integrations > Webhooks > New Webhook.
  3. Choose a channel, copy the Webhook URL.
  4. In the app, open the Settings tab, paste the URL, and click Save.

  Each completed drive test sends one embed containing:
    * Webhook URL (masked for security - domain + path prefix only)
    * Drive device path and mount point
    * Storage protocol
    * File system type
    * Total / Used / Free capacity in both MB and GB
    * Test file size in MB and GB
    * Write speed (MB/s) + performance rating
    * Read speed  (MB/s) + performance rating
    * Average speed (MB/s)
    * Write and read elapsed time
    * Read/Write speed ratio
    * Test start and completion timestamps

  When "Test All Drives" finishes, an additional ranked summary embed is
  sent showing all drives sorted by average speed.


PERFORMANCE RATING SCALE
------------------------
  NVMe SSD          >= 1000 MB/s
  SSD               >= 500  MB/s
  Fast HDD / SSD    >= 200  MB/s
  HDD 7200 RPM      >= 100  MB/s
  HDD 5400 RPM      >= 50   MB/s
  USB 2.0           >= 10   MB/s
  Very Slow          < 10   MB/s


NOTES AND LIMITATIONS
---------------------
  * The write test calls os.fsync() to flush OS buffers; this gives
    real-world (not cache-inflated) write figures.
  * Read speed may be elevated on small test sizes due to OS page-cache.
    Use 512 MB or larger for the most accurate results.
  * On Linux / macOS you may need to run as root to access some partitions.
  * Network drives and RAM disks are included if visible to psutil.
  * All temporary test files are automatically removed after each test.
    If the test is interrupted mid-run, the temp file may remain
    (named _dst_<timestamp>.tmp) and can be safely deleted manually.
  * Storage protocol detection is heuristic-based (device path + FS type).
    For authoritative interface info use OS-level tools (lsblk, WMI, etc.)


PROJECT STRUCTURE
-----------------
  Disk_Speed_Tester.py   -  Main application (single file)
  README.txt             -  This file


LICENSE
-------
  MIT License

  Copyright (c) 2025

  Permission is hereby granted, free of charge, to any person obtaining
  a copy of this software and associated documentation files (the
  "Software"), to deal in the Software without restriction, including
  without limitation the rights to use, copy, modify, merge, publish,
  distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to
  the following conditions:

  The above copyright notice and this permission notice shall be included
  in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


CHANGELOG
---------
  v3.3  -  Live language switching (bug fix)
            [CRITICAL] Language change now applies instantly to all UI
              elements — tabs, group boxes, labels, buttons, checkboxes,
              table column headers, status bar — with no restart required.
              Root cause: _on_language_change() only saved the setting and
              updated the window title; it never updated any widget text.
            Added _retranslate_ui() method that updates every translatable
              widget in-place when the user selects a new language.
            All group boxes (QGroupBox) are now stored as self._grp_*
              instance attributes so _retranslate_ui() can reach them.
            All static QLabels that needed retranslation are now stored as
              self._lbl_* instance attributes.
            Removed misleading "restart to apply" status bar message.

  v3.2  -  Bug fixes (static analysis pass)
            [CRITICAL] Fixed get_drives() missing its def line
            [CRITICAL] Removed duplicate detect_protocol() function
            [MINOR] Removed 6 dead imports (platform, threading, json,
              QPalette, QIcon, QTimer)
            [MINOR] Removed 30 orphaned translation dict entries

  v3.1  -  Download Report feature
            Download Report button with native OS file-save dialog
            Auto-download report after test checkbox option
            Detailed report content: webhook URL, drive name/ID, storage
            protocol, total/used/free capacity in both MB and GB,
            test results in MB/s, performance ratings, timestamps
            Webhook embeds updated: storage protocol, used space,
            dual MB+GB capacity units, masked webhook URL
            ReportGenerator class for structured plain-text output
            detect_storage_protocol() heuristic (NVMe/SATA/USB/Network)

  v3.0  -  Complete rewrite
            PyQt5 GUI with dark Catppuccin-inspired theme
            Live progress bars and speed indicators
            Multi-language support (EN / zh-TW / zh-CN)
            Structured Discord embeds with detailed formatting
            Configurable Webhook URL via Settings tab
            Results export and persistent settings
            Removed hardcoded Webhook credentials from source

  v2.0  -  Original CLI version
            Basic write / read speed test
            Discord Webhook (hardcoded URL)
            Chinese-only interface

================================================================================
