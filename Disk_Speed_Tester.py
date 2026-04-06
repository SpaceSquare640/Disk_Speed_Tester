"""
================================================================================
  Disk I/O Speed Tester  —  disk_speed_tester.py
================================================================================
  Description : A cross-platform disk read/write speed benchmark tool with
                a full PyQt5 GUI.  Results are displayed in real-time and can
                optionally be forwarded to a Discord webhook in a rich-embed
                format.

  Features    :
    - Sequential write & read speed test (configurable file size)
    - Test a single drive or all detected drives in one pass
    - Live progress bars and speed readouts inside the GUI
    - Discord webhook integration with structured, detailed embeds
    - Multi-language UI  —  English (default), Traditional Chinese, Simplified Chinese
    - Persistent webhook URL management (add / edit / disable)
    - Drive info panel showing capacity and usage
    - Download test report as a formatted .txt file (manual or auto after test)
    - Report includes: webhook config, drive name/ID, storage protocol,
      capacity (MB & GB), used/free space, speeds (MB/s), ratings, timestamps

  Requirements:
    Python 3.8+
    PyQt5        — pip install PyQt5
    psutil       — pip install psutil
    requests     — pip install requests

  Usage       :
    python disk_speed_tester.py

  Author      : SpaceSquare & Claude Code AI
  Version     : 3.3
  License     : MIT
================================================================================
"""

import os
import sys
import time
import tempfile
from datetime import datetime, timezone

import psutil
import requests
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QSettings
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QLineEdit,
    QProgressBar, QTextEdit, QGroupBox, QTabWidget, QSpinBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QFrame, QStatusBar, QDialog, QDialogButtonBox,
    QCheckBox, QScrollArea, QFileDialog
)

# ──────────────────────────────────────────────────────────────────────────────
# TRANSLATIONS
# ──────────────────────────────────────────────────────────────────────────────

TRANSLATIONS = {
    "en": {
        # Window / titles
        "app_title":            "Disk I/O Speed Tester v3.4",
        "tab_test":             "Speed Test",
        "tab_drives":           "Drive Info",
        "tab_results":          "Results History",
        "tab_settings":         "Settings",

        # Drive selection
        "group_drive":          "Drive Selection",
        "label_select_drive":   "Select Drive:",
        "label_test_size":      "Test File Size (MB):",
        "btn_refresh_drives":   "Refresh Drives",
        "btn_test_single":      "Test Selected Drive",
        "btn_test_all":         "Test All Drives",
        "btn_stop":             "Stop Test",

        # Progress
        "group_progress":       "Test Progress",
        "label_write":          "Write Speed:",
        "label_read":           "Read Speed:",
        "label_status":         "Status:",
        "status_idle":          "Idle — ready to test.",
        "status_testing_write": "Testing write speed…",
        "status_testing_read":  "Testing read speed…",
        "status_done":          "Test completed.",
        "status_stopped":       "Test stopped by user.",

        # Results
        "group_results":        "Current Results",
        "col_drive":            "Drive",
        "col_mount":            "Mount Point",
        "col_fs":               "File System",
        "col_write":            "Write (MB/s)",
        "col_read":             "Read (MB/s)",
        "col_avg":              "Avg (MB/s)",
        "col_rating":           "Rating",
        "col_time":             "Timestamp",
        "btn_clear_results":    "Clear Results",
        "btn_export_results":   "Export to TXT",
        "btn_download_report":  "Download Report",

        # Log
        "group_log":            "Activity Log",
        "btn_clear_log":        "Clear Log",

        # Drive info tab
        "group_drive_info":     "Available Drives",
        "col_device":           "Device",
        "col_total":            "Total (GB)",
        "col_used":             "Used (GB)",
        "col_free":             "Free (GB)",
        "col_usage":            "Usage %",
        "col_fstype":           "FS Type",

        # Settings tab
        "group_webhook":        "Discord Webhook",
        "label_webhook_url":    "Webhook URL:",
        "btn_save_webhook":     "Save",
        "btn_test_webhook":     "Test Connection",
        "btn_clear_webhook":    "Clear",
        "webhook_enabled":      "Enable Discord Webhook",
        "group_language":       "Language",
        "label_language":       "Interface Language:",

        # Performance ratings
        "rating_nvme":          "NVMe SSD",
        "rating_ssd":           "SSD",
        "rating_fast_hdd":      "Fast HDD",
        "rating_hdd":           "HDD 7200RPM",
        "rating_slow_hdd":      "HDD 5400RPM",
        "rating_very_slow":     "Very Slow / Network Drive",

        # Dialogs / messages
        "msg_no_drives":        "No accessible drives found.",
        "msg_webhook_ok":       "Webhook connection successful!",
        "msg_webhook_fail":     "Webhook connection failed: {error}",
        "msg_webhook_empty":    "Please enter a Webhook URL first.",
        "msg_webhook_saved":    "Webhook URL saved.",
        "msg_webhook_cleared":  "Webhook URL cleared.",
        "msg_test_running":     "A test is already in progress.",
        "msg_export_done":      "Results exported to:\n{path}",
        "msg_confirm_clear":    "Clear all results?",
        "msg_confirm":          "Confirm",

        # Webhook embed strings
        "embed_title_single":   "Disk Speed Test Report",
        "embed_title_all":      "All Drives Speed Test Report",
        "embed_footer":         "Disk Speed Tester v3.4",
        "embed_drive":          "Drive",
        "embed_mount":          "Mount Point",
        "embed_fs":             "File System",
        "embed_total":          "Total Capacity",
        "embed_used":           "Used Space",
        "embed_free":           "Free Space",
        "embed_protocol":       "Storage Protocol",
        "embed_test_size":      "Test File Size",
        "embed_write_speed":    "Write Speed",
        "embed_read_speed":     "Read Speed",
        "embed_avg_speed":      "Average Speed",
        "embed_write_time":     "Write Time",
        "embed_read_time":      "Read Time",
        "embed_rw_ratio":       "Read / Write Ratio",
        "embed_start_time":     "Test Started",
        "embed_end_time":       "Test Completed",
        "embed_drives_tested":  "Drives Tested",
        "embed_rank":           "Rank",

        # Report download
        "btn_download_report":      "Download Report",
        "chk_download_after_test":  "Auto-download report after test",
        "report_dialog_title":      "Save Test Report",
        "report_filter":            "Text Files (*.txt);;All Files (*)",
        "report_saved":             "Report saved to:\n{path}",
        "report_no_results":        "No results to save. Please run a test first.",
        "report_header":            "DISK I/O SPEED TEST REPORT",
        "report_generated":         "Generated",
        "report_section_system":    "SYSTEM INFORMATION",
        "report_section_webhook":   "WEBHOOK CONFIGURATION",
        "report_webhook_url":       "Webhook URL",
        "report_webhook_status":    "Webhook Status",
        "report_webhook_enabled":   "Enabled",
        "report_webhook_disabled":  "Disabled",
        "report_section_drive":     "DRIVE INFORMATION",
        "report_drive_name":        "Drive Name",
        "report_drive_id":          "Drive ID / Device Path",
        "report_drive_mount":       "Mount Point",
        "report_drive_protocol":    "Storage Protocol",
        "report_drive_fs":          "File System",
        "report_drive_total_gb":    "Total Capacity (GB)",
        "report_drive_total_mb":    "Total Capacity (MB)",
        "report_drive_used_gb":     "Used Space (GB)",
        "report_drive_used_mb":     "Used Space (MB)",
        "report_drive_free_gb":     "Free Space (GB)",
        "report_drive_free_mb":     "Free Space (MB)",
        "report_drive_usage":       "Usage",
        "report_section_results":   "TEST RESULTS",
        "report_test_size_mb":      "Test File Size (MB)",
        "report_write_speed":       "Write Speed (MB/s)",
        "report_read_speed":        "Read Speed (MB/s)",
        "report_avg_speed":         "Average Speed (MB/s)",
        "report_write_time":        "Write Elapsed Time (s)",
        "report_read_time":         "Read Elapsed Time (s)",
        "report_rw_ratio":          "Read / Write Ratio",
        "report_write_rating":      "Write Performance Rating",
        "report_read_rating":       "Read Performance Rating",
        "report_start_ts":          "Test Started",
        "report_end_ts":            "Test Completed",
        "report_section_summary":   "SUMMARY (ALL DRIVES)",
        "report_footer":            "End of Report — Disk Speed Tester v3.4",
    },

    "zh-TW": {
        "app_title":            "磁碟 I/O 速度測試工具 v3.4",
        "tab_test":             "速度測試",
        "tab_drives":           "磁碟資訊",
        "tab_results":          "歷史結果",
        "tab_settings":         "設定",

        "group_drive":          "磁碟選擇",
        "label_select_drive":   "選擇磁碟：",
        "label_test_size":      "測試檔案大小 (MB)：",
        "btn_refresh_drives":   "重新整理",
        "btn_test_single":      "測試所選磁碟",
        "btn_test_all":         "測試所有磁碟",
        "btn_stop":             "停止測試",

        "group_progress":       "測試進度",
        "label_write":          "寫入速度：",
        "label_read":           "讀取速度：",
        "label_status":         "狀態：",
        "status_idle":          "閒置 — 準備就緒。",
        "status_testing_write": "正在測試寫入速度…",
        "status_testing_read":  "正在測試讀取速度…",
        "status_done":          "測試完成。",
        "status_stopped":       "測試已被使用者停止。",

        "group_results":        "目前結果",
        "col_drive":            "磁碟",
        "col_mount":            "掛載點",
        "col_fs":               "檔案系統",
        "col_write":            "寫入 (MB/s)",
        "col_read":             "讀取 (MB/s)",
        "col_avg":              "平均 (MB/s)",
        "col_rating":           "評級",
        "col_time":             "時間",
        "btn_clear_results":    "清除結果",
        "btn_export_results":   "匯出至 TXT",
        "btn_download_report":  "下載測試報告",

        "group_log":            "活動記錄",
        "btn_clear_log":        "清除記錄",

        "group_drive_info":     "可用磁碟機",
        "col_device":           "裝置",
        "col_total":            "總容量 (GB)",
        "col_used":             "已用 (GB)",
        "col_free":             "可用 (GB)",
        "col_usage":            "使用率 %",
        "col_fstype":           "檔案系統",

        "group_webhook":        "Discord Webhook",
        "label_webhook_url":    "Webhook URL：",
        "btn_save_webhook":     "儲存",
        "btn_test_webhook":     "測試連線",
        "btn_clear_webhook":    "清除",
        "webhook_enabled":      "啟用 Discord Webhook",
        "group_language":       "語言",
        "label_language":       "介面語言：",

        "rating_nvme":          "NVMe SSD",
        "rating_ssd":           "SSD",
        "rating_fast_hdd":      "高速 HDD",
        "rating_hdd":           "HDD 7200RPM",
        "rating_slow_hdd":      "HDD 5400RPM",
        "rating_very_slow":     "極慢 / 網路磁碟機",

        "msg_no_drives":        "找不到可存取的磁碟機。",
        "msg_webhook_ok":       "Webhook 連線成功！",
        "msg_webhook_fail":     "Webhook 連線失敗：{error}",
        "msg_webhook_empty":    "請先輸入 Webhook URL。",
        "msg_webhook_saved":    "Webhook URL 已儲存。",
        "msg_webhook_cleared":  "Webhook URL 已清除。",
        "msg_test_running":     "測試正在進行中。",
        "msg_export_done":      "結果已匯出至：\n{path}",
        "msg_confirm_clear":    "清除所有結果？",
        "msg_confirm":          "確認",

        "embed_title_single":   "磁碟速度測試報告",
        "embed_title_all":      "所有磁碟速度測試報告",
        "embed_footer":         "磁碟速度測試工具 v3.4",
        "embed_drive":          "磁碟",
        "embed_mount":          "掛載點",
        "embed_fs":             "檔案系統",
        "embed_total":          "總容量",
        "embed_used":           "已使用容量",
        "embed_free":           "可用空間",
        "embed_protocol":       "儲存協議",
        "embed_test_size":      "測試檔案大小",
        "embed_write_speed":    "寫入速度",
        "embed_read_speed":     "讀取速度",
        "embed_avg_speed":      "平均速度",
        "embed_write_time":     "寫入時間",
        "embed_read_time":      "讀取時間",
        "embed_rw_ratio":       "讀取 / 寫入比例",
        "embed_start_time":     "測試開始時間",
        "embed_end_time":       "測試完成時間",
        "embed_drives_tested":  "已測試磁碟數",
        "embed_rank":           "排名",

        # Report download
        "btn_download_report":      "下載測試報告",
        "chk_download_after_test":  "測試完成後自動下載報告",
        "report_dialog_title":      "儲存測試報告",
        "report_filter":            "文字檔案 (*.txt);;所有檔案 (*)",
        "report_saved":             "報告已儲存至：\n{path}",
        "report_no_results":        "尚無測試結果，請先執行測試。",
        "report_header":            "磁碟 I/O 速度測試報告",
        "report_generated":         "生成時間",
        "report_section_system":    "系統資訊",
        "report_section_webhook":   "WEBHOOK 設定",
        "report_webhook_url":       "Webhook URL",
        "report_webhook_status":    "Webhook 狀態",
        "report_webhook_enabled":   "已啟用",
        "report_webhook_disabled":  "已停用",
        "report_section_drive":     "磁碟機資訊",
        "report_drive_name":        "磁碟名稱",
        "report_drive_id":          "磁碟代號 / 裝置路徑",
        "report_drive_mount":       "掛載點",
        "report_drive_protocol":    "儲存協議",
        "report_drive_fs":          "檔案系統",
        "report_drive_total_gb":    "總容量 (GB)",
        "report_drive_total_mb":    "總容量 (MB)",
        "report_drive_used_gb":     "已使用 (GB)",
        "report_drive_used_mb":     "已使用 (MB)",
        "report_drive_free_gb":     "可用空間 (GB)",
        "report_drive_free_mb":     "可用空間 (MB)",
        "report_drive_usage":       "使用率",
        "report_section_results":   "測試結果",
        "report_test_size_mb":      "測試檔案大小 (MB)",
        "report_write_speed":       "寫入速度 (MB/s)",
        "report_read_speed":        "讀取速度 (MB/s)",
        "report_avg_speed":         "平均速度 (MB/s)",
        "report_write_time":        "寫入耗時 (秒)",
        "report_read_time":         "讀取耗時 (秒)",
        "report_rw_ratio":          "讀取 / 寫入比例",
        "report_write_rating":      "寫入效能評級",
        "report_read_rating":       "讀取效能評級",
        "report_start_ts":          "測試開始時間",
        "report_end_ts":            "測試完成時間",
        "report_section_summary":   "綜合摘要（所有磁碟）",
        "report_footer":            "報告結束 — 磁碟速度測試工具 v3.1",
    },

    "zh-CN": {
        "app_title":            "磁盘 I/O 速度测试工具 v3.4",
        "tab_test":             "速度测试",
        "tab_drives":           "磁盘信息",
        "tab_results":          "历史结果",
        "tab_settings":         "设置",

        "group_drive":          "磁盘选择",
        "label_select_drive":   "选择磁盘：",
        "label_test_size":      "测试文件大小 (MB)：",
        "btn_refresh_drives":   "刷新",
        "btn_test_single":      "测试所选磁盘",
        "btn_test_all":         "测试所有磁盘",
        "btn_stop":             "停止测试",

        "group_progress":       "测试进度",
        "label_write":          "写入速度：",
        "label_read":           "读取速度：",
        "label_status":         "状态：",
        "status_idle":          "空闲 — 就绪。",
        "status_testing_write": "正在测试写入速度…",
        "status_testing_read":  "正在测试读取速度…",
        "status_done":          "测试完成。",
        "status_stopped":       "测试已被用户停止。",

        "group_results":        "当前结果",
        "col_drive":            "磁盘",
        "col_mount":            "挂载点",
        "col_fs":               "文件系统",
        "col_write":            "写入 (MB/s)",
        "col_read":             "读取 (MB/s)",
        "col_avg":              "平均 (MB/s)",
        "col_rating":           "评级",
        "col_time":             "时间",
        "btn_clear_results":    "清除结果",
        "btn_export_results":   "导出为 TXT",
        "btn_download_report":  "下载测试报告",

        "group_log":            "活动日志",
        "btn_clear_log":        "清除日志",

        "group_drive_info":     "可用磁盘",
        "col_device":           "设备",
        "col_total":            "总容量 (GB)",
        "col_used":             "已用 (GB)",
        "col_free":             "可用 (GB)",
        "col_usage":            "使用率 %",
        "col_fstype":           "文件系统",

        "group_webhook":        "Discord Webhook",
        "label_webhook_url":    "Webhook URL：",
        "btn_save_webhook":     "保存",
        "btn_test_webhook":     "测试连接",
        "btn_clear_webhook":    "清除",
        "webhook_enabled":      "启用 Discord Webhook",
        "group_language":       "语言",
        "label_language":       "界面语言：",

        "rating_nvme":          "NVMe SSD",
        "rating_ssd":           "SSD",
        "rating_fast_hdd":      "高速 HDD",
        "rating_hdd":           "HDD 7200RPM",
        "rating_slow_hdd":      "HDD 5400RPM",
        "rating_very_slow":     "极慢 / 网络驱动器",

        "msg_no_drives":        "未找到可访问的磁盘。",
        "msg_webhook_ok":       "Webhook 连接成功！",
        "msg_webhook_fail":     "Webhook 连接失败：{error}",
        "msg_webhook_empty":    "请先输入 Webhook URL。",
        "msg_webhook_saved":    "Webhook URL 已保存。",
        "msg_webhook_cleared":  "Webhook URL 已清除。",
        "msg_test_running":     "测试正在进行中。",
        "msg_export_done":      "结果已导出至：\n{path}",
        "msg_confirm_clear":    "清除所有结果？",
        "msg_confirm":          "确认",

        "embed_title_single":   "磁盘速度测试报告",
        "embed_title_all":      "所有磁盘速度测试报告",
        "embed_footer":         "磁盘速度测试工具 v3.4",
        "embed_drive":          "磁盘",
        "embed_mount":          "挂载点",
        "embed_fs":             "文件系统",
        "embed_total":          "总容量",
        "embed_used":           "已使用容量",
        "embed_free":           "可用空间",
        "embed_protocol":       "存储协议",
        "embed_test_size":      "测试文件大小",
        "embed_write_speed":    "写入速度",
        "embed_read_speed":     "读取速度",
        "embed_avg_speed":      "平均速度",
        "embed_write_time":     "写入时间",
        "embed_read_time":      "读取时间",
        "embed_rw_ratio":       "读取 / 写入比例",
        "embed_start_time":     "测试开始时间",
        "embed_end_time":       "测试完成时间",
        "embed_drives_tested":  "已测试磁盘数",
        "embed_rank":           "排名",

        # Report download
        "btn_download_report":      "下载测试报告",
        "chk_download_after_test":  "测试完成后自动下载报告",
        "report_dialog_title":      "保存测试报告",
        "report_filter":            "文本文件 (*.txt);;所有文件 (*)",
        "report_saved":             "报告已保存至：\n{path}",
        "report_no_results":        "暂无测试结果，请先执行测试。",
        "report_header":            "磁盘 I/O 速度测试报告",
        "report_generated":         "生成时间",
        "report_section_system":    "系统信息",
        "report_section_webhook":   "WEBHOOK 配置",
        "report_webhook_url":       "Webhook URL",
        "report_webhook_status":    "Webhook 状态",
        "report_webhook_enabled":   "已启用",
        "report_webhook_disabled":  "已禁用",
        "report_section_drive":     "磁盘信息",
        "report_drive_name":        "磁盘名称",
        "report_drive_id":          "磁盘代号 / 设备路径",
        "report_drive_mount":       "挂载点",
        "report_drive_protocol":    "存储协议",
        "report_drive_fs":          "文件系统",
        "report_drive_total_gb":    "总容量 (GB)",
        "report_drive_total_mb":    "总容量 (MB)",
        "report_drive_used_gb":     "已用空间 (GB)",
        "report_drive_used_mb":     "已用空间 (MB)",
        "report_drive_free_gb":     "可用空间 (GB)",
        "report_drive_free_mb":     "可用空间 (MB)",
        "report_drive_usage":       "使用率",
        "report_section_results":   "测试结果",
        "report_test_size_mb":      "测试文件大小 (MB)",
        "report_write_speed":       "写入速度 (MB/s)",
        "report_read_speed":        "读取速度 (MB/s)",
        "report_avg_speed":         "平均速度 (MB/s)",
        "report_write_time":        "写入耗时 (秒)",
        "report_read_time":         "读取耗时 (秒)",
        "report_rw_ratio":          "读取 / 写入比例",
        "report_write_rating":      "写入性能评级",
        "report_read_rating":       "读取性能评级",
        "report_start_ts":          "测试开始时间",
        "report_end_ts":            "测试完成时间",
        "report_section_summary":   "综合摘要（所有磁盘）",
        "report_footer":            "报告结束 — 磁盘速度测试工具 v3.1",
    },
}

LANGUAGE_NAMES = {
    "en":    "English",
    "zh-TW": "繁體中文",
    "zh-CN": "简体中文",
}


# ──────────────────────────────────────────────────────────────────────────────
# HELPER UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def tr(lang: str, key: str, **kwargs) -> str:
    """Return a translated string for the given language and key."""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def performance_rating(lang: str, speed_mbs: float) -> tuple[str, str]:
    """
    Return (emoji, rating_label) based on speed in MB/s.
    Thresholds are approximate real-world storage class boundaries.
    """
    if speed_mbs >= 1000:
        return "🚀", tr(lang, "rating_nvme")
    elif speed_mbs >= 500:
        return "🔥", tr(lang, "rating_ssd")
    elif speed_mbs >= 200:
        return "⚡", tr(lang, "rating_fast_hdd")
    elif speed_mbs >= 100:
        return "👍", tr(lang, "rating_hdd")
    elif speed_mbs >= 50:
        return "⚠️", tr(lang, "rating_slow_hdd")
    elif speed_mbs >= 10:
        return "🐌", tr(lang, "rating_usb2")
    else:
        return "💔", tr(lang, "rating_very_slow")


def speed_color(speed_mbs: float) -> int:
    """Return a Discord embed sidebar colour based on average speed."""
    if speed_mbs >= 500:
        return 0x00FF00   # bright green
    elif speed_mbs >= 200:
        return 0x90FF00   # yellow-green
    elif speed_mbs >= 100:
        return 0xFFFF00   # yellow
    elif speed_mbs >= 50:
        return 0xFF9900   # orange
    else:
        return 0xFF0000   # red

def get_drives() -> list[dict]:
    """Return a list of accessible non-virtual disk partitions."""
    drives = []
    for part in psutil.disk_partitions():
        # Skip optical drives and pseudo-filesystems
        skip_fs = {"squashfs", "tmpfs", "devtmpfs", "overlay", "proc", "sysfs"}
        if os.name == "nt" and ("cdrom" in part.opts or not part.fstype):
            continue
        if os.name != "nt" and part.fstype in skip_fs:
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            drives.append({
                "device":     part.device,
                "mountpoint": part.mountpoint,
                "fstype":     part.fstype,
                "protocol":   detect_storage_protocol(
                                  part.device, part.mountpoint, part.fstype),
                "total_gb":   usage.total / (1024 ** 3),
                "used_gb":    usage.used  / (1024 ** 3),
                "free_gb":    usage.free  / (1024 ** 3),
                "usage_pct":  usage.percent,
            })
        except PermissionError:
            continue
    return drives


# ──────────────────────────────────────────────────────────────────────────────
# DISK TEST WORKER (runs in a QThread to keep GUI responsive)
# ──────────────────────────────────────────────────────────────────────────────

class DiskTestWorker(QThread):
    """Background thread that performs the actual read/write benchmarks."""

    # Signals emitted to the main thread
    sig_progress    = pyqtSignal(str, int)      # (phase, percent)
    sig_speed       = pyqtSignal(str, float)    # (phase, speed_mbs)
    sig_result      = pyqtSignal(dict)           # completed result dict
    sig_log         = pyqtSignal(str)            # log message
    sig_error       = pyqtSignal(str)            # error message
    sig_done        = pyqtSignal()               # all tests finished

    def __init__(
        self,
        drives: list[dict],
        file_size_mb: int,
        lang: str,
    ):
        super().__init__()
        self.drives       = drives
        self.file_size_mb = file_size_mb
        self.lang         = lang
        self._stop_flag   = False

    def stop(self):
        self._stop_flag = True

    # ── internal helpers ──────────────────────────────────────────────────────

    def _write_test(self, mount: str) -> tuple[float, float]:
        """
        Write `file_size_mb` MB of zeros to a temp file and measure throughput.
        Returns (speed_mbs, elapsed_seconds).
        """
        chunk     = b"\x00" * (1024 * 1024)   # 1 MiB chunk
        tmp_path  = os.path.join(mount, f"_dst_{int(time.time())}.tmp")
        written   = 0

        try:
            t0 = time.perf_counter()
            with open(tmp_path, "wb") as fh:
                for i in range(self.file_size_mb):
                    if self._stop_flag:
                        break
                    fh.write(chunk)
                    written += len(chunk)
                    pct = int((i + 1) / self.file_size_mb * 100)
                    self.sig_progress.emit("write", pct)
                    self.sig_speed.emit("write", written / (1024 ** 2) / max(time.perf_counter() - t0, 0.001))
                fh.flush()
                os.fsync(fh.fileno())   # ensure data hits the medium
            elapsed = time.perf_counter() - t0
            speed   = written / (1024 ** 2) / elapsed
            return speed, elapsed
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    def _read_test(self, mount: str) -> tuple[float, float]:
        """
        Write then read back `file_size_mb` MB and measure read throughput.
        Returns (speed_mbs, elapsed_seconds).
        """
        chunk    = b"\x00" * (1024 * 1024)
        tmp_path = os.path.join(mount, f"_dst_{int(time.time())}.tmp")

        # Create the reference file
        with open(tmp_path, "wb") as fh:
            for _ in range(self.file_size_mb):
                fh.write(chunk)
            fh.flush()
            os.fsync(fh.fileno())

        read_bytes = 0
        chunks_done = 0
        total_chunks = self.file_size_mb

        try:
            t0 = time.perf_counter()
            with open(tmp_path, "rb") as fh:
                while True:
                    if self._stop_flag:
                        break
                    data = fh.read(1024 * 1024)
                    if not data:
                        break
                    read_bytes  += len(data)
                    chunks_done += 1
                    pct = int(chunks_done / total_chunks * 100)
                    self.sig_progress.emit("read", pct)
                    self.sig_speed.emit("read", read_bytes / (1024 ** 2) / max(time.perf_counter() - t0, 0.001))
            elapsed = time.perf_counter() - t0
            speed   = read_bytes / (1024 ** 2) / elapsed
            return speed, elapsed
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    # ── QThread entry point ───────────────────────────────────────────────────

    def run(self):
        for drive in self.drives:
            if self._stop_flag:
                break

            mount = drive["mountpoint"]
            self.sig_log.emit(f"▶  Testing  {drive['device']}  ({mount})")

            start_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Write test
            self.sig_log.emit(f"   {tr(self.lang, 'status_testing_write')}")
            try:
                write_speed, write_time = self._write_test(mount)
            except Exception as exc:
                self.sig_error.emit(f"Write test failed on {mount}: {exc}")
                continue

            if self._stop_flag:
                break

            # Read test
            self.sig_log.emit(f"   {tr(self.lang, 'status_testing_read')}")
            try:
                read_speed, read_time = self._read_test(mount)
            except Exception as exc:
                self.sig_error.emit(f"Read test failed on {mount}: {exc}")
                continue

            end_ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            avg     = (write_speed + read_speed) / 2
            emoji_w, label_w = performance_rating(self.lang, write_speed)
            emoji_r, label_r = performance_rating(self.lang, read_speed)

            result = {
                "device":      drive["device"],
                "mountpoint":  mount,
                "fstype":      drive["fstype"],
                "protocol":    drive.get("protocol", "Unknown"),
                "total_gb":    drive["total_gb"],
                "used_gb":     drive.get("used_gb", 0.0),
                "free_gb":     drive["free_gb"],
                "file_size_mb":self.file_size_mb,
                "write_speed": write_speed,
                "read_speed":  read_speed,
                "avg_speed":   avg,
                "write_time":  write_time,
                "read_time":   read_time,
                "write_rating":f"{emoji_w} {label_w}",
                "read_rating": f"{emoji_r} {label_r}",
                "start_ts":    start_ts,
                "end_ts":      end_ts,
            }

            self.sig_log.emit(
                f"   ✅  Write: {write_speed:.1f} MB/s  |  "
                f"Read: {read_speed:.1f} MB/s  |  "
                f"Avg: {avg:.1f} MB/s"
            )
            self.sig_result.emit(result)

        self.sig_done.emit()


# ──────────────────────────────────────────────────────────────────────────────
# DISCORD WEBHOOK SENDER
# ──────────────────────────────────────────────────────────────────────────────

class WebhookSender:
    """Builds and posts richly-formatted Discord embeds."""

    def __init__(self, url: str, lang: str):
        self.url  = url
        self.lang = lang

    def _post(self, payload: dict) -> tuple[bool, str]:
        """
        POST a JSON payload to the webhook URL.
        Returns (True, "") on success, or (False, error_message) on failure.
        Error messages are human-readable and suitable for logging/display.
        """
        if not self.url:
            return False, "No webhook URL configured"
        try:
            resp = requests.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status_code in (200, 204):
                return True, ""
            # Include HTTP status + Discord error body for diagnosis
            try:
                body = resp.json()
                detail = body.get("message", resp.text[:120])
            except Exception:
                detail = resp.text[:120]
            return False, f"HTTP {resp.status_code}: {detail}"
        except requests.exceptions.Timeout:
            return False, "Request timed out (10 s)"
        except requests.exceptions.ConnectionError as exc:
            return False, f"Connection error: {exc}"
        except requests.exceptions.RequestException as exc:
            return False, f"Request error: {exc}"

    def send_single_result(self, result: dict) -> bool:
        """Send a detailed embed for a single drive result."""
        L    = self.lang
        avg  = result["avg_speed"]

        # Dual-unit capacity helpers
        total_mb  = result["total_gb"] * 1024
        used_mb   = result.get("used_gb", 0.0) * 1024
        free_mb   = result["free_gb"] * 1024
        size_mb   = result["file_size_mb"]
        size_gb   = size_mb / 1024

        # Mask the webhook URL for security (show domain + first 20 chars of path)
        wh_display = self.url
        try:
            parts = self.url.split("/")
            wh_display = "/".join(parts[:5]) + "/…"
        except Exception:
            pass

        description = (
            f"**🔗 Webhook:** `{wh_display}`\n"
            f"\n"
            f"**🖥️ {tr(L, 'embed_drive')}:** `{result['device']}`\n"
            f"**📁 {tr(L, 'embed_mount')}:** `{result['mountpoint']}`\n"
            f"**💽 {tr(L, 'embed_fs')}:** `{result['fstype']}`\n"
            f"**🔌 {tr(L, 'embed_protocol')}:** `{result.get('protocol', 'Unknown')}`\n"
            f"\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"**💾 {tr(L, 'embed_total')}:**  `{total_mb:,.0f} MB`  /  `{result['total_gb']:.2f} GB`\n"
            f"**📊 {tr(L, 'embed_used')}:**   `{used_mb:,.0f} MB`  /  `{result.get('used_gb', 0):.2f} GB`\n"
            f"**🆓 {tr(L, 'embed_free')}:**   `{free_mb:,.0f} MB`  /  `{result['free_gb']:.2f} GB`\n"
            f"**📏 {tr(L, 'embed_test_size')}:** `{size_mb} MB`  /  `{size_gb:.3f} GB`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"**📝 {tr(L, 'embed_write_speed')}:** `{result['write_speed']:.2f} MB/s`  —  {result['write_rating']}\n"
            f"**📖 {tr(L, 'embed_read_speed')}:**  `{result['read_speed']:.2f} MB/s`  —  {result['read_rating']}\n"
            f"**📈 {tr(L, 'embed_avg_speed')}:**   `{avg:.2f} MB/s`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"**⏱️ {tr(L, 'embed_write_time')}:**  `{result['write_time']:.3f} s`\n"
            f"**⏱️ {tr(L, 'embed_read_time')}:**   `{result['read_time']:.3f} s`\n"
            f"**🔄 {tr(L, 'embed_rw_ratio')}:**    `{result['read_speed'] / max(result['write_speed'], 0.001):.2f}×`\n"
            f"\n"
            f"**⏰ {tr(L, 'embed_start_time')}:** `{result['start_ts']}`\n"
            f"**✅ {tr(L, 'embed_end_time')}:**   `{result['end_ts']}`\n"
        )

        payload = {
            "embeds": [{
                "title":       f"💾  {tr(L, 'embed_title_single')}  —  {result['device']}",
                "description": description,
                "color":       speed_color(avg),
                "timestamp":   datetime.now(timezone.utc).isoformat(),
                "footer":      {"text": tr(L, "embed_footer")},
            }]
        }
        return self._post(payload)

    def send_all_results(self, results: list[dict]) -> bool:
        """Send a summary embed ranking all drives by average speed."""
        L       = self.lang
        sorted_ = sorted(results, key=lambda r: r["avg_speed"], reverse=True)

        # Masked webhook URL
        wh_display = self.url
        try:
            parts = self.url.split("/")
            wh_display = "/".join(parts[:5]) + "/…"
        except Exception:
            pass

        lines = [f"**🔗 Webhook:** `{wh_display}`\n"]
        for rank, r in enumerate(sorted_, 1):
            emoji, _ = performance_rating(L, r["avg_speed"])
            total_mb = r["total_gb"] * 1024
            used_mb  = r.get("used_gb", 0.0) * 1024
            free_mb  = r["free_gb"] * 1024
            lines.append(
                f"**{tr(L, 'embed_rank')} #{rank}  {emoji}  {r['device']}**\n"
                f"> 🔌 {tr(L, 'embed_protocol')}: `{r.get('protocol', 'Unknown')}`  |  "
                f"💽 {tr(L, 'embed_fs')}: `{r['fstype']}`\n"
                f"> 💾 {tr(L, 'embed_total')}: `{total_mb:,.0f} MB` / `{r['total_gb']:.2f} GB`  |  "
                f"📊 {tr(L, 'embed_used')}: `{used_mb:,.0f} MB` / `{r.get('used_gb', 0):.2f} GB`  |  "
                f"🆓 {tr(L, 'embed_free')}: `{free_mb:,.0f} MB` / `{r['free_gb']:.2f} GB`\n"
                f"> 📝 {tr(L, 'embed_write_speed')}: `{r['write_speed']:.2f} MB/s`  |  "
                f"📖 {tr(L, 'embed_read_speed')}: `{r['read_speed']:.2f} MB/s`  |  "
                f"📈 {tr(L, 'embed_avg_speed')}: `{r['avg_speed']:.2f} MB/s`\n"
                f"> {r['write_rating']}  |  {r['read_rating']}\n"
            )

        overall_avg = sum(r["avg_speed"] for r in results) / len(results)

        description = (
            "\n".join(line.rstrip("\n") for line in lines)
            + f"\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"**{tr(L, 'embed_drives_tested')}:** `{len(results)}`\n"
            f"**{tr(L, 'embed_end_time')}:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
        )

        payload = {
            "embeds": [{
                "title":       f"📊  {tr(L, 'embed_title_all')}",
                "description": description,
                "color":       speed_color(overall_avg),
                "timestamp":   datetime.now(timezone.utc).isoformat(),
                "footer":      {"text": tr(L, "embed_footer")},
            }]
        }
        return self._post(payload)

    def send_test_connection(self) -> tuple[bool, str]:
        """
        Send a simple test message to verify the webhook is reachable.
        Returns (success, error_message).
        """
        payload = {
            "content": (
                f"🔗  **Disk Speed Tester — Webhook Test**\n"
                f"> Time: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
                f"> Status: ✅  Connection successful"
            )
        }
        try:
            resp = requests.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status_code in (200, 204):
                return True, ""
            return False, f"HTTP {resp.status_code}"
        except requests.exceptions.RequestException as exc:
            return False, str(exc)


# ──────────────────────────────────────────────────────────────────────────────
# STORAGE PROTOCOL DETECTION
# ──────────────────────────────────────────────────────────────────────────────

def detect_storage_protocol(device: str, mountpoint: str, fstype: str) -> str:
    """
    Attempt to infer the storage interface/protocol from the device path,
    mount point, and filesystem type.  Returns a human-readable string such
    as "NVMe (PCIe)", "SATA / ATA", "USB", "Network (SMB/NFS)", etc.

    This is a best-effort heuristic — authoritative info requires OS-level
    APIs (e.g. WMI on Windows, udev on Linux) which are out of scope here.
    """
    dev  = device.lower()
    mnt  = mountpoint.lower()
    fs   = fstype.lower()

    # ── Network / virtual ────────────────────────────────────────────────────
    if fs in ("nfs", "nfs4", "cifs", "smb", "smbfs", "afpfs", "sshfs",
              "fuse.sshfs", "fuse.glusterfs", "fuse.s3fs"):
        return "Network Drive (NFS/SMB/FUSE)"
    if dev.startswith("//") or dev.startswith("\\\\") or ":" in dev and dev[1] != ":":
        return "Network Drive (UNC Path)"
    if fs in ("tmpfs", "ramfs"):
        return "RAM / tmpfs"
    if fs == "overlay":
        return "Overlay (Container / VM)"

    # ── Windows drive letters ─────────────────────────────────────────────────
    if os.name == "nt":
        # On Windows we can't reliably detect protocol without WMI; give a
        # sensible default based on letter conventions
        if dev.startswith("c:") or dev.startswith("d:"):
            return "SATA / NVMe (Internal)"
        if dev.startswith("e:") or dev.startswith("f:") or dev.startswith("g:"):
            return "USB / Removable"
        return "Internal / Unknown"

    # ── Linux / macOS device paths ────────────────────────────────────────────
    if "/dev/nvme" in dev:
        return "NVMe (PCIe)"
    if "/dev/sd" in dev:
        # sda-sdz could be SATA or USB; distinguish by mountpoint hints
        if any(x in mnt for x in ("usb", "removable", "media")):
            return "USB Storage (Mass Storage)"
        return "SATA / SAS (HDD or SSD)"
    if "/dev/hd" in dev:
        return "PATA / IDE"
    if "/dev/vd" in dev:
        return "VirtIO (Virtual Machine)"
    if "/dev/xvd" in dev:
        return "Xen Virtual Disk"
    if "/dev/mmcblk" in dev:
        return "eMMC / SD Card"
    if "/dev/fd" in dev:
        return "Floppy Disk"
    if "/dev/sr" in dev or "/dev/cdrom" in dev:
        return "Optical Drive (CD/DVD)"
    if "disk" in dev and "s" in dev:          # macOS: /dev/disk0s1
        return "SATA / NVMe (macOS)"
    if "disk" in dev:
        return "Disk (macOS)"

    return "Unknown / Other"


# ──────────────────────────────────────────────────────────────────────────────
# REPORT GENERATOR
# ──────────────────────────────────────────────────────────────────────────────

class ReportGenerator:
    """
    Builds a detailed, human-readable plain-text report from a list of test
    result dicts.  The report includes:
      • System information
      • Webhook configuration (URL + enabled state)
      • Per-drive section: name, ID/path, storage protocol, FS type,
        total / used / free capacity in both MB and GB
      • Test results: write/read/avg speeds in MB/s, elapsed times,
        read-write ratio, performance ratings
      • Multi-drive summary table ranked by average speed
    """

    WIDTH = 72   # column width for the separator lines

    def __init__(
        self,
        results:        list[dict],
        lang:           str,
        webhook_url:    str  = "",
        webhook_enabled:bool = False,
    ):
        self.results         = results
        self.lang            = lang
        self.webhook_url     = webhook_url
        self.webhook_enabled = webhook_enabled

    # ── public API ────────────────────────────────────────────────────────────

    def build(self) -> str:
        """Return the complete report as a multi-line string."""
        L    = self.lang
        sep  = "=" * self.WIDTH
        thin = "-" * self.WIDTH
        now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines: list[str] = []

        # ── Header ────────────────────────────────────────────────────────────
        lines += [
            sep,
            f"  {tr(L, 'report_header')}",
            sep,
            f"  {tr(L, 'report_generated')}: {now}",
            "",
        ]

        # ── System information ────────────────────────────────────────────────
        lines += [
            thin,
            f"  {tr(L, 'report_section_system')}",
            thin,
            f"  OS            : {sys.platform}",
            f"  Python        : {sys.version.split()[0]}",
            "",
        ]

        # ── Webhook configuration ─────────────────────────────────────────────
        wh_status = (
            tr(L, "report_webhook_enabled")
            if self.webhook_enabled
            else tr(L, "report_webhook_disabled")
        )
        wh_url_display = self.webhook_url if self.webhook_url else "(not set)"

        lines += [
            thin,
            f"  {tr(L, 'report_section_webhook')}",
            thin,
            f"  {tr(L, 'report_webhook_status'):<28}: {wh_status}",
            f"  {tr(L, 'report_webhook_url'):<28}: {wh_url_display}",
            "",
        ]

        # ── Per-drive results ─────────────────────────────────────────────────
        for idx, r in enumerate(self.results, 1):
            total_mb = r["total_gb"] * 1024
            used_mb  = (r["total_gb"] - r["free_gb"]) * 1024
            free_mb  = r["free_gb"]  * 1024
            used_gb  = r["total_gb"] - r["free_gb"]
            usage_pct = (used_gb / r["total_gb"] * 100) if r["total_gb"] > 0 else 0

            protocol = detect_storage_protocol(
                r["device"], r["mountpoint"], r["fstype"]
            )

            lines += [
                sep,
                f"  [{idx}]  {r['device']}  ({r['mountpoint']})",
                sep,
            ]

            # Drive identity
            lines += [
                f"  {tr(L, 'report_section_drive')}",
                thin,
                f"  {tr(L, 'report_drive_name'):<28}: {r['device']}",
                f"  {tr(L, 'report_drive_id'):<28}: {r['device']}",
                f"  {tr(L, 'report_drive_mount'):<28}: {r['mountpoint']}",
                f"  {tr(L, 'report_drive_protocol'):<28}: {protocol}",
                f"  {tr(L, 'report_drive_fs'):<28}: {r['fstype']}",
                "",
            ]

            # Capacity — both GB and MB
            lines += [
                f"  {tr(L, 'report_drive_total_gb'):<28}: {r['total_gb']:.3f} GB",
                f"  {tr(L, 'report_drive_total_mb'):<28}: {total_mb:.1f} MB",
                f"  {tr(L, 'report_drive_used_gb'):<28}: {used_gb:.3f} GB",
                f"  {tr(L, 'report_drive_used_mb'):<28}: {used_mb:.1f} MB",
                f"  {tr(L, 'report_drive_free_gb'):<28}: {r['free_gb']:.3f} GB",
                f"  {tr(L, 'report_drive_free_mb'):<28}: {free_mb:.1f} MB",
                f"  {tr(L, 'report_drive_usage'):<28}: {usage_pct:.1f}%",
                "",
            ]

            # Test results
            rw_ratio = r["read_speed"] / max(r["write_speed"], 0.001)
            lines += [
                f"  {tr(L, 'report_section_results')}",
                thin,
                f"  {tr(L, 'report_test_size_mb'):<28}: {r['file_size_mb']} MB",
                f"  {tr(L, 'report_write_speed'):<28}: {r['write_speed']:.2f} MB/s",
                f"  {tr(L, 'report_read_speed'):<28}: {r['read_speed']:.2f} MB/s",
                f"  {tr(L, 'report_avg_speed'):<28}: {r['avg_speed']:.2f} MB/s",
                f"  {tr(L, 'report_write_time'):<28}: {r['write_time']:.3f} s",
                f"  {tr(L, 'report_read_time'):<28}: {r['read_time']:.3f} s",
                f"  {tr(L, 'report_rw_ratio'):<28}: {rw_ratio:.2f}x",
                f"  {tr(L, 'report_write_rating'):<28}: {r['write_rating']}",
                f"  {tr(L, 'report_read_rating'):<28}: {r['read_rating']}",
                f"  {tr(L, 'report_start_ts'):<28}: {r['start_ts']}",
                f"  {tr(L, 'report_end_ts'):<28}: {r['end_ts']}",
                "",
            ]

        # ── Multi-drive summary ───────────────────────────────────────────────
        if len(self.results) > 1:
            sorted_r = sorted(self.results, key=lambda x: x["avg_speed"], reverse=True)
            lines += [
                sep,
                f"  {tr(L, 'report_section_summary')}",
                sep,
                f"  {'#':<4}  {'Drive':<18}  {'Write MB/s':>12}  {'Read MB/s':>12}  {'Avg MB/s':>10}  {'Rating'}",
                thin,
            ]
            for rank, r in enumerate(sorted_r, 1):
                emoji, _ = performance_rating(L, r["avg_speed"])
                lines.append(
                    f"  {rank:<4}  {r['device']:<18}  "
                    f"{r['write_speed']:>12.2f}  "
                    f"{r['read_speed']:>12.2f}  "
                    f"{r['avg_speed']:>10.2f}  "
                    f"{emoji}"
                )
            lines.append("")

        # ── Footer ────────────────────────────────────────────────────────────
        lines += [
            sep,
            f"  {tr(L, 'report_footer')}",
            sep,
            "",
        ]

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN WINDOW
# ──────────────────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """Primary application window."""

    # Custom signal for thread-safe log messages (emitted from worker threads)
    _log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # ── persistent settings ───────────────────────────────────────────────
        self._settings   = QSettings("DiskSpeedTester", "DST")
        self._lang             = self._settings.value("language", "en")
        self._webhook          = self._settings.value("webhook_url", "")
        self._wh_enabled       = self._settings.value("webhook_enabled", True, type=bool)
        self._auto_dl_report   = self._settings.value("auto_download_report", False, type=bool)

        # ── state ─────────────────────────────────────────────────────────────
        self._drives  : list[dict] = []
        self._results : list[dict] = []
        self._worker  : DiskTestWorker | None = None

        # ── UI setup ──────────────────────────────────────────────────────────
        self._build_ui()
        self._apply_dark_theme()
        self._refresh_drives()
        self._update_window_title()

        # Connect thread-safe log signal to the append_log slot
        self._log_signal.connect(self._append_log)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        L = self._lang
        self.setMinimumSize(960, 680)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(6)
        root.setContentsMargins(8, 8, 8, 8)

        self._tabs = QTabWidget()
        root.addWidget(self._tabs)

        self._build_test_tab()
        self._build_drives_tab()
        self._build_results_tab()
        self._build_settings_tab()

        # Status bar
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._statusbar.showMessage(tr(L, "status_idle"))

    # ── Test tab ──────────────────────────────────────────────────────────────

    def _build_test_tab(self):
        L      = self._lang
        tab    = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        # ── Drive selection group ─────────────────────────────────────────────
        self._grp_drive = QGroupBox(tr(L, "group_drive"))
        grp_drive = self._grp_drive
        g1        = QGridLayout(grp_drive)

        self._lbl_select_drive = QLabel(tr(L, "label_select_drive"))
        g1.addWidget(self._lbl_select_drive, 0, 0)
        self._combo_drive = QComboBox()
        self._combo_drive.setMinimumWidth(280)
        g1.addWidget(self._combo_drive, 0, 1)

        self._btn_refresh = QPushButton(tr(L, "btn_refresh_drives"))
        self._btn_refresh.clicked.connect(self._refresh_drives)
        g1.addWidget(self._btn_refresh, 0, 2)

        self._lbl_test_size = QLabel(tr(L, "label_test_size"))
        g1.addWidget(self._lbl_test_size, 1, 0)
        self._spin_size = QSpinBox()
        self._spin_size.setRange(10, 4096)
        self._spin_size.setValue(100)
        self._spin_size.setSuffix(" MB")
        g1.addWidget(self._spin_size, 1, 1)

        btn_row = QHBoxLayout()
        self._btn_single = QPushButton(tr(L, "btn_test_single"))
        self._btn_single.clicked.connect(self._run_single)
        self._btn_single.setFixedHeight(34)
        btn_row.addWidget(self._btn_single)

        self._btn_all = QPushButton(tr(L, "btn_test_all"))
        self._btn_all.clicked.connect(self._run_all)
        self._btn_all.setFixedHeight(34)
        btn_row.addWidget(self._btn_all)

        self._btn_stop = QPushButton(tr(L, "btn_stop"))
        self._btn_stop.clicked.connect(self._stop_test)
        self._btn_stop.setFixedHeight(34)
        self._btn_stop.setEnabled(False)
        btn_row.addWidget(self._btn_stop)

        g1.addLayout(btn_row, 2, 0, 1, 3)
        layout.addWidget(grp_drive)

        # ── Progress group ────────────────────────────────────────────────────
        self._grp_prog = QGroupBox(tr(L, "group_progress"))
        grp_prog  = self._grp_prog
        g2        = QGridLayout(grp_prog)

        self._lbl_write_lbl = QLabel(tr(L, "label_write"))
        g2.addWidget(self._lbl_write_lbl, 0, 0)
        self._bar_write = QProgressBar()
        self._bar_write.setTextVisible(True)
        g2.addWidget(self._bar_write, 0, 1)
        self._lbl_write_speed = QLabel("—")
        self._lbl_write_speed.setMinimumWidth(120)
        g2.addWidget(self._lbl_write_speed, 0, 2)

        self._lbl_read_lbl = QLabel(tr(L, "label_read"))
        g2.addWidget(self._lbl_read_lbl, 1, 0)
        self._bar_read = QProgressBar()
        self._bar_read.setTextVisible(True)
        g2.addWidget(self._bar_read, 1, 1)
        self._lbl_read_speed = QLabel("—")
        g2.addWidget(self._lbl_read_speed, 1, 2)

        self._lbl_status_lbl = QLabel(tr(L, "label_status"))
        g2.addWidget(self._lbl_status_lbl, 2, 0)
        self._lbl_status = QLabel(tr(L, "status_idle"))
        self._lbl_status.setStyleSheet("color: #aaaaaa;")
        g2.addWidget(self._lbl_status, 2, 1, 1, 2)

        layout.addWidget(grp_prog)

        # ── Splitter: results table + log ─────────────────────────────────────
        splitter = QSplitter(Qt.Vertical)

        self._grp_results = QGroupBox(tr(L, "group_results"))
        grp_results  = self._grp_results
        rv           = QVBoxLayout(grp_results)
        self._table  = self._make_results_table()
        rv.addWidget(self._table)
        rc = QHBoxLayout()
        self._btn_clear_results  = QPushButton(tr(L, "btn_clear_results"))
        self._btn_clear_results.clicked.connect(self._clear_results)
        self._btn_export_results = QPushButton(tr(L, "btn_export_results"))
        self._btn_export_results.clicked.connect(self._export_results)
        self._btn_download_report = QPushButton(tr(L, "btn_download_report"))
        self._btn_download_report.clicked.connect(self._download_report)
        self._btn_download_report.setStyleSheet(
            "QPushButton { background: #313244; color: #89b4fa; border: 1px solid #89b4fa; border-radius: 4px; padding: 5px 12px; }"
            "QPushButton:hover { background: #45475a; }"
        )
        self._chk_auto_download = QCheckBox(tr(L, "chk_download_after_test"))
        self._chk_auto_download.setChecked(
            self._settings.value("auto_download_report", False, type=bool)
        )
        self._chk_auto_download.stateChanged.connect(self._on_auto_download_toggle)
        rc.addWidget(self._btn_clear_results)
        rc.addWidget(self._btn_export_results)
        rc.addWidget(self._btn_download_report)
        rc.addSpacing(16)
        rc.addWidget(self._chk_auto_download)
        rc.addStretch()
        rv.addLayout(rc)
        splitter.addWidget(grp_results)

        self._grp_log = QGroupBox(tr(L, "group_log"))
        grp_log     = self._grp_log
        lv          = QVBoxLayout(grp_log)
        self._log   = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(QFont("Consolas", 9))
        lv.addWidget(self._log)
        lc = QHBoxLayout()
        self._btn_clear_log = QPushButton(tr(L, "btn_clear_log"))
        self._btn_clear_log.clicked.connect(self._log.clear)
        lc.addWidget(self._btn_clear_log)
        lc.addStretch()
        lv.addLayout(lc)
        splitter.addWidget(grp_log)

        splitter.setSizes([260, 140])
        layout.addWidget(splitter, 1)

        self._tabs.addTab(tab, tr(L, "tab_test"))

    def _make_results_table(self) -> QTableWidget:
        L    = self._lang
        cols = [
            tr(L, "col_drive"), tr(L, "col_mount"), tr(L, "col_fs"),
            tr(L, "col_write"), tr(L, "col_read"), tr(L, "col_avg"),
            tr(L, "col_rating"), tr(L, "col_time"),
        ]
        t = QTableWidget(0, len(cols))
        t.setHorizontalHeaderLabels(cols)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        t.horizontalHeader().setStretchLastSection(True)
        t.setSelectionBehavior(QTableWidget.SelectRows)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setAlternatingRowColors(True)
        return t

    # ── Drives info tab ───────────────────────────────────────────────────────

    def _build_drives_tab(self):
        L      = self._lang
        tab    = QWidget()
        layout = QVBoxLayout(tab)

        self._grp_drive_info = QGroupBox(tr(L, "group_drive_info"))
        grp    = self._grp_drive_info
        gv     = QVBoxLayout(grp)

        cols = [
            tr(L, "col_device"), tr(L, "col_mount"), tr(L, "col_fstype"),
            tr(L, "col_total"), tr(L, "col_used"), tr(L, "col_free"),
            tr(L, "col_usage"),
        ]
        self._drive_table = QTableWidget(0, len(cols))
        self._drive_table.setHorizontalHeaderLabels(cols)
        self._drive_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._drive_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._drive_table.setAlternatingRowColors(True)
        gv.addWidget(self._drive_table)

        layout.addWidget(grp)
        self._tabs.addTab(tab, tr(L, "tab_drives"))

    # ── Results history tab ───────────────────────────────────────────────────

    def _build_results_tab(self):
        L      = self._lang
        tab    = QWidget()
        layout = QVBoxLayout(tab)

        self._results_text = QTextEdit()
        self._results_text.setReadOnly(True)
        self._results_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self._results_text)

        self._tabs.addTab(tab, tr(L, "tab_results"))

    # ── Settings tab ─────────────────────────────────────────────────────────

    def _build_settings_tab(self):
        L      = self._lang
        tab    = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # Webhook group
        self._grp_wh = QGroupBox(tr(L, "group_webhook"))
        grp_wh = self._grp_wh
        gw     = QGridLayout(grp_wh)

        self._chk_webhook = QCheckBox(tr(L, "webhook_enabled"))
        self._chk_webhook.setChecked(self._wh_enabled)
        self._chk_webhook.stateChanged.connect(self._on_webhook_toggle)
        gw.addWidget(self._chk_webhook, 0, 0, 1, 3)

        self._lbl_webhook_url = QLabel(tr(L, "label_webhook_url"))
        gw.addWidget(self._lbl_webhook_url, 1, 0)
        self._edit_webhook = QLineEdit(self._webhook)
        self._edit_webhook.setPlaceholderText("https://discord.com/api/webhooks/…")
        self._edit_webhook.setMinimumWidth(420)
        gw.addWidget(self._edit_webhook, 1, 1)

        wh_btns = QHBoxLayout()
        self._btn_save_wh  = QPushButton(tr(L, "btn_save_webhook"))
        self._btn_save_wh.clicked.connect(self._save_webhook)
        self._btn_test_wh  = QPushButton(tr(L, "btn_test_webhook"))
        self._btn_test_wh.clicked.connect(self._test_webhook)
        self._btn_clear_wh = QPushButton(tr(L, "btn_clear_webhook"))
        self._btn_clear_wh.clicked.connect(self._clear_webhook)
        wh_btns.addWidget(self._btn_save_wh)
        wh_btns.addWidget(self._btn_test_wh)
        wh_btns.addWidget(self._btn_clear_wh)
        wh_btns.addStretch()
        gw.addLayout(wh_btns, 2, 1)

        layout.addWidget(grp_wh)

        # Language group
        self._grp_lang = QGroupBox(tr(L, "group_language"))
        grp_lang = self._grp_lang
        gl       = QHBoxLayout(grp_lang)
        self._lbl_language = QLabel(tr(L, "label_language"))
        gl.addWidget(self._lbl_language)
        self._combo_lang = QComboBox()
        for code, name in LANGUAGE_NAMES.items():
            self._combo_lang.addItem(name, code)
        # Set current
        idx = list(LANGUAGE_NAMES.keys()).index(self._lang) if self._lang in LANGUAGE_NAMES else 0
        self._combo_lang.setCurrentIndex(idx)
        self._combo_lang.currentIndexChanged.connect(self._on_language_change)
        gl.addWidget(self._combo_lang)
        gl.addStretch()
        layout.addWidget(grp_lang)

        layout.addStretch()
        self._tabs.addTab(tab, tr(L, "tab_settings"))

    # ── Styling ───────────────────────────────────────────────────────────────

    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget        { background: #1e1e2e; color: #cdd6f4; }
            QGroupBox                   { border: 1px solid #45475a; border-radius: 6px;
                                          margin-top: 10px; padding-top: 8px;
                                          font-weight: bold; color: #cba6f7; }
            QGroupBox::title            { subcontrol-origin: margin; left: 10px; }
            QTabWidget::pane            { border: 1px solid #45475a; border-radius: 4px; }
            QTabBar::tab                { background: #313244; color: #cdd6f4; padding: 6px 14px;
                                          border-radius: 4px 4px 0 0; margin-right: 2px; }
            QTabBar::tab:selected       { background: #45475a; color: #cba6f7; }
            QComboBox, QLineEdit, QSpinBox {
                background: #313244; color: #cdd6f4; border: 1px solid #45475a;
                border-radius: 4px; padding: 4px 8px; }
            QComboBox::drop-down        { border: none; }
            QPushButton                 { background: #45475a; color: #cdd6f4; border: none;
                                          border-radius: 4px; padding: 5px 12px; }
            QPushButton:hover           { background: #585b70; }
            QPushButton:pressed         { background: #6c6f85; }
            QPushButton:disabled        { background: #313244; color: #6c6f85; }
            QProgressBar                { background: #313244; border: 1px solid #45475a;
                                          border-radius: 4px; height: 18px; text-align: center; }
            QProgressBar::chunk        { background: #89b4fa; border-radius: 3px; }
            QTableWidget                { background: #181825; gridline-color: #313244;
                                          border: 1px solid #45475a; border-radius: 4px; }
            QHeaderView::section        { background: #313244; color: #cba6f7; padding: 5px;
                                          border: none; border-bottom: 1px solid #45475a; }
            QTableWidget::item          { padding: 4px; }
            QTableWidget::item:selected { background: #45475a; }
            QTextEdit                   { background: #181825; color: #a6e3a1; border: 1px solid #45475a;
                                          border-radius: 4px; font-family: Consolas, monospace; }
            QCheckBox                   { color: #cdd6f4; }
            QScrollBar:vertical         { background: #313244; width: 10px; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #585b70; border-radius: 5px; }
            QStatusBar                  { background: #181825; color: #6c6f85; }
        """)

    # ── Drive management ──────────────────────────────────────────────────────

    def _refresh_drives(self):
        self._drives = get_drives()
        self._combo_drive.clear()
        for d in self._drives:
            label = f"{d['device']}  ({d['mountpoint']})  —  {d['free_gb']:.1f} GB free"
            self._combo_drive.addItem(label)

        # Update drive info table
        self._drive_table.setRowCount(0)
        for d in self._drives:
            row = self._drive_table.rowCount()
            self._drive_table.insertRow(row)
            vals = [
                d["device"], d["mountpoint"], d["fstype"],
                f"{d['total_gb']:.1f}", f"{d['used_gb']:.1f}",
                f"{d['free_gb']:.1f}", f"{d['usage_pct']:.1f}%",
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self._drive_table.setItem(row, col, item)

    # ── Test control ──────────────────────────────────────────────────────────

    def _run_single(self):
        if self._worker and self._worker.isRunning():
            QMessageBox.warning(self, tr(self._lang, "msg_confirm"),
                                tr(self._lang, "msg_test_running"))
            return
        if not self._drives:
            QMessageBox.warning(self, "", tr(self._lang, "msg_no_drives"))
            return
        idx   = self._combo_drive.currentIndex()
        drive = self._drives[idx : idx + 1]
        self._start_test(drive)

    def _run_all(self):
        if self._worker and self._worker.isRunning():
            QMessageBox.warning(self, tr(self._lang, "msg_confirm"),
                                tr(self._lang, "msg_test_running"))
            return
        if not self._drives:
            QMessageBox.warning(self, "", tr(self._lang, "msg_no_drives"))
            return
        self._start_test(self._drives)

    def _start_test(self, drives: list[dict]):
        self._bar_write.setValue(0)
        self._bar_read.setValue(0)
        self._lbl_write_speed.setText("—")
        self._lbl_read_speed.setText("—")
        self._set_testing(True)

        self._worker = DiskTestWorker(drives, self._spin_size.value(), self._lang)
        self._worker.sig_progress.connect(self._on_progress)
        self._worker.sig_speed.connect(self._on_speed_update)
        self._worker.sig_result.connect(self._on_result)
        self._worker.sig_log.connect(self._append_log)
        self._worker.sig_error.connect(self._on_error)
        self._worker.sig_done.connect(self._on_done)
        self._worker.start()

    def _stop_test(self):
        if self._worker:
            self._worker.stop()
            self._lbl_status.setText(tr(self._lang, "status_stopped"))

    # ── Worker callbacks ──────────────────────────────────────────────────────

    def _on_progress(self, phase: str, pct: int):
        if phase == "write":
            self._bar_write.setValue(pct)
            self._lbl_status.setText(tr(self._lang, "status_testing_write"))
        else:
            self._bar_read.setValue(pct)
            self._lbl_status.setText(tr(self._lang, "status_testing_read"))
        self._statusbar.showMessage(f"{phase.capitalize()} {pct}%")

    def _on_speed_update(self, phase: str, speed: float):
        text = f"{speed:.1f} MB/s"
        if phase == "write":
            self._lbl_write_speed.setText(text)
        else:
            self._lbl_read_speed.setText(text)

    def _on_result(self, result: dict):
        self._results.append(result)
        self._add_table_row(result)
        self._update_results_text()

        # Send to webhook in a background thread to avoid blocking the GUI
        if self._wh_enabled and self._webhook:
            self._send_webhook_async(
                "single",
                result=result,
                label=result.get("device", "drive"),
            )

    def _send_webhook_async(self, mode: str, result: dict = None,
                            results: list = None, label: str = ""):
        """
        Fire-and-forget webhook POST executed in a daemon thread so the GUI
        thread is never blocked.  Logs success / failure to the activity log.
        """
        import threading

        webhook_url = self._webhook
        lang        = self._lang
        wh_enabled  = self._wh_enabled

        def _worker():
            sender = WebhookSender(webhook_url, lang)
            if mode == "single" and result is not None:
                ok, err = sender.send_single_result(result)
            elif mode == "all" and results is not None:
                ok, err = sender.send_all_results(results)
            else:
                return

            # Emit log signal — safe to call from any thread because
            # _log_signal is connected with Qt.QueuedConnection by default
            if ok:
                self._log_signal.emit(f"📡  Webhook sent OK  [{label}]")
            else:
                self._log_signal.emit(f"❌  Webhook FAILED  [{label}]: {err}")

        t = threading.Thread(target=_worker, daemon=True)
        t.start()



    def _on_error(self, msg: str):
        self._append_log(f"❌  {msg}")
        QMessageBox.warning(self, "Error", msg)

    def _on_done(self):
        self._set_testing(False)
        self._lbl_status.setText(tr(self._lang, "status_done"))
        self._statusbar.showMessage(tr(self._lang, "status_done"))

        # Send summary webhook for multi-drive (async, non-blocking)
        if len(self._results) > 1 and self._wh_enabled and self._webhook:
            self._send_webhook_async(
                "all",
                results=list(self._results),
                label="all drives summary",
            )

        # Auto-download report if the option is checked
        if self._auto_dl_report and self._results:
            self._download_report(auto=True)

    def _append_log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self._log.append(f"[{ts}]  {msg}")

    # ── Download report ───────────────────────────────────────────────────────

    def _download_report(self, auto: bool = False):
        """
        Build a detailed test report and prompt the user to choose a save
        location via a native file-save dialog.
        When `auto=True` (called from _on_done), a default filename is
        suggested but the save dialog still appears so the user can confirm.
        """
        L = self._lang

        if not self._results:
            QMessageBox.warning(self, "", tr(L, "report_no_results"))
            return

        # Build report text
        generator = ReportGenerator(
            results=self._results,
            lang=self._lang,
            webhook_url=self._webhook,
            webhook_enabled=self._wh_enabled,
        )
        report_text = generator.build()

        # Suggest a default filename
        ts           = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"disk_speed_report_{ts}.txt"
        default_path = os.path.join(os.path.expanduser("~"), default_name)

        # Show native save-file dialog
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr(L, "report_dialog_title"),
            default_path,
            tr(L, "report_filter"),
        )

        if not path:
            return   # user cancelled

        # Ensure .txt extension
        if not path.lower().endswith(".txt"):
            path += ".txt"

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(report_text)

        self._append_log(f"📄  Report saved: {path}")
        QMessageBox.information(self, "", tr(L, "report_saved", path=path))

    def _on_auto_download_toggle(self, state: int):
        """Persist the auto-download preference."""
        self._auto_dl_report = state == Qt.Checked
        self._settings.setValue("auto_download_report", self._auto_dl_report)

    # ── Results table helpers ─────────────────────────────────────────────────

    def _add_table_row(self, r: dict):
        row = self._table.rowCount()
        self._table.insertRow(row)
        vals = [
            r["device"], r["mountpoint"], r["fstype"],
            f"{r['write_speed']:.2f}",
            f"{r['read_speed']:.2f}",
            f"{r['avg_speed']:.2f}",
            r["write_rating"],
            r["end_ts"],
        ]
        for col, val in enumerate(vals):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, col, item)

        # Colour the average column by speed
        avg_item = self._table.item(row, 5)
        avg_item.setForeground(QColor(*self._speed_qcolor(r["avg_speed"])))

    @staticmethod
    def _speed_qcolor(speed: float) -> tuple[int, int, int]:
        if speed >= 500:
            return (0, 255, 100)
        elif speed >= 200:
            return (144, 255, 0)
        elif speed >= 100:
            return (255, 255, 0)
        elif speed >= 50:
            return (255, 153, 0)
        else:
            return (255, 80, 80)

    def _clear_results(self):
        reply = QMessageBox.question(
            self, tr(self._lang, "msg_confirm"),
            tr(self._lang, "msg_confirm_clear"),
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._results.clear()
            self._table.setRowCount(0)
            self._results_text.clear()

    def _export_results(self):
        if not self._results:
            return
        path = os.path.join(
            tempfile.gettempdir(),
            f"disk_speed_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self._results_text.toPlainText())
        QMessageBox.information(
            self, tr(self._lang, "msg_confirm"),
            tr(self._lang, "msg_export_done", path=path),
        )

    def _update_results_text(self):
        lines = ["=" * 70, "  DISK I/O SPEED TEST RESULTS", "=" * 70, ""]
        for i, r in enumerate(self._results, 1):
            used_gb = r["total_gb"] - r["free_gb"]
            used_mb = used_gb * 1024
            protocol = detect_storage_protocol(r["device"], r["mountpoint"], r["fstype"])
            lines += [
                f"Result #{i}",
                f"  Drive              : {r['device']}",
                f"  Mount Point        : {r['mountpoint']}",
                f"  Storage Protocol   : {protocol}",
                f"  File System        : {r['fstype']}",
                f"  Total Capacity     : {r['total_gb']:.3f} GB  /  {r['total_gb']*1024:.1f} MB",
                f"  Used Space         : {used_gb:.3f} GB  /  {used_mb:.1f} MB",
                f"  Free Space         : {r['free_gb']:.3f} GB  /  {r['free_gb']*1024:.1f} MB",
                f"  Test Size          : {r['file_size_mb']} MB",
                f"  Write Speed        : {r['write_speed']:.2f} MB/s  ({r['write_rating']})",
                f"  Read Speed         : {r['read_speed']:.2f} MB/s  ({r['read_rating']})",
                f"  Average Speed      : {r['avg_speed']:.2f} MB/s",
                f"  Write Time         : {r['write_time']:.3f} s",
                f"  Read Time          : {r['read_time']:.3f} s",
                f"  Started            : {r['start_ts']}",
                f"  Completed          : {r['end_ts']}",
                "",
            ]
        self._results_text.setPlainText("\n".join(lines))

    # ── Settings callbacks ────────────────────────────────────────────────────

    def _on_webhook_toggle(self, state: int):
        self._wh_enabled = state == Qt.Checked
        self._settings.setValue("webhook_enabled", self._wh_enabled)

    def _save_webhook(self):
        url = self._edit_webhook.text().strip()
        self._webhook = url
        self._settings.setValue("webhook_url", url)
        self._append_log(tr(self._lang, "msg_webhook_saved"))
        self._statusbar.showMessage(tr(self._lang, "msg_webhook_saved"), 3000)

    def _clear_webhook(self):
        self._edit_webhook.clear()
        self._webhook = ""
        self._settings.setValue("webhook_url", "")
        self._append_log(tr(self._lang, "msg_webhook_cleared"))

    def _test_webhook(self):
        url = self._edit_webhook.text().strip()
        if not url:
            QMessageBox.warning(self, "", tr(self._lang, "msg_webhook_empty"))
            return
        sender         = WebhookSender(url, self._lang)
        success, error = sender.send_test_connection()
        if success:
            QMessageBox.information(self, "", tr(self._lang, "msg_webhook_ok"))
        else:
            QMessageBox.warning(self, "", tr(self._lang, "msg_webhook_fail", error=error))

    def _on_language_change(self, idx: int):
        """Switch UI language live — no restart required."""
        code = self._combo_lang.itemData(idx)
        self._lang = code
        self._settings.setValue("language", code)
        self._retranslate_ui()

    def _retranslate_ui(self):
        """
        Update every translatable widget label in-place using the current
        self._lang.  Called immediately when the user picks a new language
        so the entire UI switches without restarting.
        """
        L = self._lang

        # ── Window title ──────────────────────────────────────────────────
        self.setWindowTitle(tr(L, "app_title"))

        # ── Tab bar ───────────────────────────────────────────────────────
        self._tabs.setTabText(0, tr(L, "tab_test"))
        self._tabs.setTabText(1, tr(L, "tab_drives"))
        self._tabs.setTabText(2, tr(L, "tab_results"))
        self._tabs.setTabText(3, tr(L, "tab_settings"))

        # ── Speed Test tab — group boxes ──────────────────────────────────
        self._grp_drive.setTitle(tr(L, "group_drive"))
        self._grp_prog.setTitle(tr(L, "group_progress"))
        self._grp_results.setTitle(tr(L, "group_results"))
        self._grp_log.setTitle(tr(L, "group_log"))

        # ── Speed Test tab — labels ───────────────────────────────────────
        self._lbl_select_drive.setText(tr(L, "label_select_drive"))
        self._lbl_test_size.setText(tr(L, "label_test_size"))
        self._lbl_write_lbl.setText(tr(L, "label_write"))
        self._lbl_read_lbl.setText(tr(L, "label_read"))
        self._lbl_status_lbl.setText(tr(L, "label_status"))
        self._lbl_status.setText(tr(L, "status_idle"))

        # ── Speed Test tab — buttons ──────────────────────────────────────
        self._btn_refresh.setText(tr(L, "btn_refresh_drives"))
        self._btn_single.setText(tr(L, "btn_test_single"))
        self._btn_all.setText(tr(L, "btn_test_all"))
        self._btn_stop.setText(tr(L, "btn_stop"))
        self._btn_clear_results.setText(tr(L, "btn_clear_results"))
        self._btn_export_results.setText(tr(L, "btn_export_results"))
        self._btn_download_report.setText(tr(L, "btn_download_report"))
        self._btn_clear_log.setText(tr(L, "btn_clear_log"))
        self._chk_auto_download.setText(tr(L, "chk_download_after_test"))

        # ── Speed Test tab — results table column headers ─────────────────
        self._table.setHorizontalHeaderLabels([
            tr(L, "col_drive"), tr(L, "col_mount"), tr(L, "col_fs"),
            tr(L, "col_write"), tr(L, "col_read"), tr(L, "col_avg"),
            tr(L, "col_rating"), tr(L, "col_time"),
        ])

        # ── Drive Info tab ────────────────────────────────────────────────
        self._grp_drive_info.setTitle(tr(L, "group_drive_info"))
        self._drive_table.setHorizontalHeaderLabels([
            tr(L, "col_device"), tr(L, "col_mount"), tr(L, "col_fstype"),
            tr(L, "col_total"), tr(L, "col_used"), tr(L, "col_free"),
            tr(L, "col_usage"),
        ])

        # ── Settings tab — group boxes ────────────────────────────────────
        self._grp_wh.setTitle(tr(L, "group_webhook"))
        self._grp_lang.setTitle(tr(L, "group_language"))

        # ── Settings tab — labels & widgets ──────────────────────────────
        self._lbl_webhook_url.setText(tr(L, "label_webhook_url"))
        self._lbl_language.setText(tr(L, "label_language"))
        self._chk_webhook.setText(tr(L, "webhook_enabled"))
        self._btn_save_wh.setText(tr(L, "btn_save_webhook"))
        self._btn_test_wh.setText(tr(L, "btn_test_webhook"))
        self._btn_clear_wh.setText(tr(L, "btn_clear_webhook"))

        # ── Status bar ────────────────────────────────────────────────────
        self._statusbar.showMessage(tr(L, "status_idle"))

    # ── Utility ───────────────────────────────────────────────────────────────

    def _update_window_title(self):
        """Kept for compatibility; _retranslate_ui() is the canonical updater."""
        self.setWindowTitle(tr(self._lang, "app_title"))

    def _set_testing(self, active: bool):
        self._btn_single.setEnabled(not active)
        self._btn_all.setEnabled(not active)
        self._btn_refresh.setEnabled(not active)
        self._btn_stop.setEnabled(active)


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    # Verify dependencies before launching the GUI
    missing = []
    try:
        import psutil    # noqa: F401
    except ImportError:
        missing.append("psutil")
    try:
        import requests  # noqa: F401
    except ImportError:
        missing.append("requests")
    try:
        from PyQt5.QtWidgets import QApplication  # noqa: F401
    except ImportError:
        missing.append("PyQt5")

    if missing:
        print("Missing required packages. Install with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)

    app    = QApplication(sys.argv)
    app.setApplicationName("Disk Speed Tester")
    app.setApplicationVersion("3.0")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
