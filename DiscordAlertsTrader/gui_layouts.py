#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 11:54:36 2021
Migrated to tkinter/ttkbootstrap on Nov 13 2025

@author: adonay
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
from tkinter.ttk import Treeview

import ttkbootstrap as ttk_boot
from ttkbootstrap.constants import *

from . import gui_generator as gg

tip = "coma separed patterns, e.g. string1,string2"
tlp_date = "Date can be:\n-a date mm/dd/yyyy, mm/dd\n-a period: today, yesterday, week, biweek, month, mtd, ytd"


class LayoutBuilder:
    """Helper class to build tkinter layouts"""

    def __init__(self, parent):
        self.parent = parent
        self.widgets = {}

    def add_widget(self, key, widget):
        """Store widget reference by key for later access"""
        self.widgets[key] = widget
        return widget


def create_console_frame(
    parent, ttl="Discord messages from subscribed channels", key="-MLINE-__WRITE ONLY__"
):
    """Create console text display"""
    frame = ttk.Frame(parent)

    label = ttk.Label(frame, text=ttl)
    label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    text_widget = scrolledtext.ScrolledText(frame, width=120, height=20, wrap=tk.WORD)
    text_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

    return frame, text_widget, key


def create_trigger_alerts_frame(parent):
    """Create trigger alerts controls"""
    tp_chan = (
        "Select portfolios to trigger alert.\n'user' for your portfolio only. Will bypass false do_BTO and do_BTC and make the trade \n"
        + "'analysts' for the alerts tracker,\n'all' for both"
    )
    tp_trig = (
        "Click portfolio row number to prefill the STC alert. Alerts can look like\n"
        + "BTO: Author, BTO 1 AAA 115C 05/30 @2.5 PT 3.5TS30% PT2 4 SL TS40% -> '%' for percentage, TS for Trailing Stop\n"
        + "STC: Author, STC 1 AAA 115C 05/30 @3\n"
        + "Exit Update: Author, exit update AAA 115C 05/30 PT 80% SL 2\n"
        + "Exit Update: Author, exit update AAA 115C 05/30 isopen:no\n"
        + "Exit Update: Author, exit update AAA 115C 05/30 cancelAVG\n"
        + "Get quotes: Author, BTO 1 AAA 115C 05/30 @m"
    )

    frame = ttk.Frame(parent)
    widgets = {}

    # First row - main controls
    row1 = ttk.Frame(frame)
    row1.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    ttk.Label(row1, text="to portfolio:").pack(side=tk.LEFT, padx=2)

    widgets["_chan_trigg_"] = ttk.Combobox(
        row1, values=["both", "user", "analysts"], state="readonly", width=15
    )
    widgets["_chan_trigg_"].set("analysts")
    widgets["_chan_trigg_"].pack(side=tk.LEFT, padx=2)

    widgets["-toggle"] = ttk.Button(row1, text="▲", width=3)
    widgets["-toggle"].pack(side=tk.LEFT, padx=2)

    widgets["-subm-msg"] = ttk.Entry(row1, width=80)
    widgets["-subm-msg"].insert(
        0, "Author, STC 1 AAA 115C 05/30 @2.5 [click port row number to prefill]"
    )
    widgets["-subm-msg"].pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

    widgets["-subm-alert"] = ttk.Button(row1, text="Trigger alert", width=20)
    widgets["-subm-alert"].pack(side=tk.LEFT, padx=2)

    # Second row - alert action buttons
    row2 = ttk.Frame(frame)
    row2.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    widgets["-alert_to-"] = ttk.Label(row2, text="Change alert to:")
    widgets["-alert_to-"].pack(side=tk.LEFT, padx=2)

    button_configs = [
        ("-alert_BTO", "BTO", 10),
        ("-alert_STC", "STC", 10),
        ("-alert_STO", "STO", 10),
        ("-alert_BTC", "BTC", 10),
        ("-alert_exitupdate", "ExitUpdate", 15),
        ("-alert_quotes", "Get quotes", 15),
        ("-alert_plot", "Plot quotes", 15),
        ("-alert_tome", "author: me", 15),
        ("-alert_tomeshort", "author: me_short", 20),
        ("-alert_exits", "3 exits 1 SL", 15),
    ]

    for key, text, width in button_configs:
        widgets[key] = ttk.Button(row2, text=text, width=width)
        widgets[key].pack(side=tk.LEFT, padx=2)

    # Set initial visibility
    widgets["-alert_to-"].pack_forget()
    for key, _, _ in button_configs:
        widgets[key].pack_forget()

    return frame, widgets


def create_portfolio_frame(parent, data_n_headers, font_body, font_header):
    """Create portfolio display with filters"""
    frame = ttk.Frame(parent)
    widgets = {}

    if data_n_headers[0] == []:
        values = []
    else:
        values = data_n_headers[0]

    # Filter row 1 - Include filters
    filter_frame1 = ttk.Frame(frame)
    filter_frame1.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    ttk.Label(filter_frame1, text="Include:  Authors:").pack(side=tk.LEFT, padx=2)
    widgets["port_filt_author"] = ttk.Entry(filter_frame1, width=15)
    widgets["port_filt_author"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="Date from:").pack(side=tk.LEFT, padx=2)
    widgets["port_filt_date_frm"] = ttk.Combobox(
        filter_frame1, values=["today", "week", "month"], state="readonly", width=10
    )
    widgets["port_filt_date_frm"].set("week")
    widgets["port_filt_date_frm"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="To:").pack(side=tk.LEFT, padx=2)
    widgets["port_filt_date_to"] = ttk.Combobox(
        filter_frame1, values=["today", "week", "month"], state="readonly", width=10
    )
    widgets["port_filt_date_to"].set("today")
    widgets["port_filt_date_to"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="Symbols:").pack(side=tk.LEFT, padx=2)
    widgets["port_filt_sym"] = ttk.Entry(filter_frame1, width=15)
    widgets["port_filt_sym"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="Channels:").pack(side=tk.LEFT, padx=2)
    widgets["port_filt_chn"] = ttk.Entry(filter_frame1, width=15)
    widgets["port_filt_chn"].pack(side=tk.LEFT, padx=2)

    # Filter row 2 - Exclude checkboxes
    filter_frame2 = ttk.Frame(frame)
    filter_frame2.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    ttk.Label(filter_frame2, text="Exclude: |").pack(side=tk.LEFT, padx=2)

    checkbox_configs = [
        ("-port-Closed", "Closed", False),
        ("-port-Open", "Open", False),
        ("-port-Canceled", "Canceled", True),
        ("-port-Rejected", "Rejected", True),
        ("-port-NegPnL", "Neg PnL", False),
        ("-port-PosPnL", "Pos PnL", False),
        ("-port-live PnL", "Live PnL", False),
        ("-port-stocks", "Stocks", True),
        ("-port-options", "Options", False),
        ("-port-bto", "BTO", False),
        ("-port-sto", "STO", False),
    ]

    for key, text, default in checkbox_configs:
        var = tk.BooleanVar(value=default)
        widgets[key] = ttk.Checkbutton(filter_frame2, text=text, variable=var)
        widgets[key].var = var
        widgets[key].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame2, text="| Authors:").pack(side=tk.LEFT, padx=2)
    widgets["port_exc_author"] = ttk.Entry(filter_frame2, width=15)
    widgets["port_exc_author"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame2, text="Channels:").pack(side=tk.LEFT, padx=2)
    widgets["port_exc_chn"] = ttk.Entry(filter_frame2, width=15)
    widgets["port_exc_chn"].pack(side=tk.LEFT, padx=2)

    # Update button
    update_frame = ttk.Frame(frame)
    update_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    widgets["_upd-portfolio_"] = ttk.Button(
        update_frame, text="Update", bootstyle="dark"
    )
    widgets["_upd-portfolio_"].pack(side=tk.LEFT, padx=2)

    # Table
    table_frame = ttk.Frame(frame)
    table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Create treeview with scrollbars
    tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
    tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

    widgets["_portfolio_"] = Treeview(
        table_frame,
        columns=data_n_headers[1],
        show="tree headings",
        yscrollcommand=tree_scroll_y.set,
        xscrollcommand=tree_scroll_x.set,
    )

    tree_scroll_y.config(command=widgets["_portfolio_"].yview)
    tree_scroll_x.config(command=widgets["_portfolio_"].xview)

    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    widgets["_portfolio_"].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configure columns
    widgets["_portfolio_"].column("#0", width=50, minwidth=50)  # Row number column
    for idx, heading in enumerate(data_n_headers[1]):
        widgets["_portfolio_"].heading(f"#{idx + 1}", text=heading)
        widgets["_portfolio_"].column(f"#{idx + 1}", width=100, minwidth=50)

    # Insert data
    for row_idx, row_data in enumerate(values):
        tag = "evenrow" if row_idx % 2 == 0 else "oddrow"
        widgets["_portfolio_"].insert(
            "", tk.END, text=str(row_idx + 1), values=row_data, tags=(tag,)
        )

    # Configure alternating row colors
    widgets["_portfolio_"].tag_configure("oddrow", background="white")
    widgets["_portfolio_"].tag_configure("evenrow", background="lightgray")

    return frame, widgets


# Continue with remaining functions in next part...


def create_traders_frame(parent, data_n_headers, font_body, font_header):
    """Create analysts portfolio/traders display with filters"""
    frame = ttk.Frame(parent)
    widgets = {}

    if data_n_headers[0] == []:
        values = []
    else:
        values = data_n_headers[0]

    # Filter row 1 - Include filters
    filter_frame1 = ttk.Frame(frame)
    filter_frame1.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    ttk.Label(filter_frame1, text="Include:  Authors:").pack(side=tk.LEFT, padx=2)
    widgets["track_filt_author"] = ttk.Entry(filter_frame1, width=12)
    widgets["track_filt_author"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="Date from:").pack(side=tk.LEFT, padx=2)
    widgets["track_filt_date_frm"] = ttk.Combobox(
        filter_frame1, values=["today", "week", "month"], state="readonly", width=10
    )
    widgets["track_filt_date_frm"].set("week")
    widgets["track_filt_date_frm"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="To:").pack(side=tk.LEFT, padx=2)
    widgets["track_filt_date_to"] = ttk.Combobox(
        filter_frame1, values=["today", "week", "month"], state="readonly", width=10
    )
    widgets["track_filt_date_to"].set("")
    widgets["track_filt_date_to"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="Symbols:").pack(side=tk.LEFT, padx=2)
    widgets["track_filt_sym"] = ttk.Entry(filter_frame1, width=12)
    widgets["track_filt_sym"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="Channels:").pack(side=tk.LEFT, padx=2)
    widgets["track_filt_chn"] = ttk.Entry(filter_frame1, width=12)
    widgets["track_filt_chn"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="DTE: min").pack(side=tk.LEFT, padx=2)
    widgets["track_dte_min"] = ttk.Entry(filter_frame1, width=8)
    widgets["track_dte_min"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="max").pack(side=tk.LEFT, padx=2)
    widgets["track_dte_max"] = ttk.Entry(filter_frame1, width=8)
    widgets["track_dte_max"].pack(side=tk.LEFT, padx=2)

    # Filter row 2 - Exclude checkboxes
    filter_frame2 = ttk.Frame(frame)
    filter_frame2.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    ttk.Label(filter_frame2, text="Exclude: |").pack(side=tk.LEFT, padx=2)

    checkbox_configs = [
        ("-track-Closed", "Closed", False),
        ("-track-Open", "Open", False),
        ("-track-NegPnL", "Neg PnL", False),
        ("-track-PosPnL", "Pos PnL", False),
        ("-track-live PnL", "Live PnL", False),
        ("-track-stocks", "Stocks", True),
        ("-track-options", "Options", False),
        ("-track-bto", "BTO", False),
        ("-track-sto", "STO", False),
    ]

    for key, text, default in checkbox_configs:
        var = tk.BooleanVar(value=default)
        widgets[key] = ttk.Checkbutton(filter_frame2, text=text, variable=var)
        widgets[key].var = var
        widgets[key].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame2, text="| Authors:").pack(side=tk.LEFT, padx=2)
    widgets["track_exc_author"] = ttk.Entry(filter_frame2, width=12)
    widgets["track_exc_author"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame2, text="Symbols:").pack(side=tk.LEFT, padx=2)
    widgets["track_exc_sym"] = ttk.Entry(filter_frame2, width=12)
    widgets["track_exc_sym"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame2, text="Channels:").pack(side=tk.LEFT, padx=2)
    widgets["track_exc_chn"] = ttk.Entry(filter_frame2, width=12)
    widgets["track_exc_chn"].pack(side=tk.LEFT, padx=2)

    # Update button
    update_frame = ttk.Frame(frame)
    update_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    widgets["_upd-track_"] = ttk.Button(update_frame, text="Update", bootstyle="dark")
    widgets["_upd-track_"].pack(side=tk.LEFT, padx=2)

    # Table
    table_frame = ttk.Frame(frame)
    table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

    tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
    tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

    widgets["_track_"] = Treeview(
        table_frame,
        columns=data_n_headers[1],
        show="tree headings",
        yscrollcommand=tree_scroll_y.set,
        xscrollcommand=tree_scroll_x.set,
    )

    tree_scroll_y.config(command=widgets["_track_"].yview)
    tree_scroll_x.config(command=widgets["_track_"].xview)

    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    widgets["_track_"].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configure columns
    widgets["_track_"].column("#0", width=50, minwidth=50)
    for idx, heading in enumerate(data_n_headers[1]):
        widgets["_track_"].heading(f"#{idx + 1}", text=heading)
        widgets["_track_"].column(f"#{idx + 1}", width=100, minwidth=50)

    # Insert data
    for row_idx, row_data in enumerate(values):
        tag = "evenrow" if row_idx % 2 == 0 else "oddrow"
        widgets["_track_"].insert(
            "", tk.END, text=str(row_idx + 1), values=row_data, tags=(tag,)
        )

    widgets["_track_"].tag_configure("oddrow", background="white")
    widgets["_track_"].tag_configure("evenrow", background="lightgray")

    return frame, widgets


def create_stats_frame(parent, data_n_headers, font_body, font_header):
    """Create statistics display with filters"""
    frame = ttk.Frame(parent)
    widgets = {}

    if data_n_headers[0] == []:
        values = []
    else:
        values = data_n_headers[0]

    # Filter row 1
    filter_frame1 = ttk.Frame(frame)
    filter_frame1.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    ttk.Label(filter_frame1, text="Include:  Authors:").pack(side=tk.LEFT, padx=2)
    widgets["stat_filt_author"] = ttk.Entry(filter_frame1, width=12)
    widgets["stat_filt_author"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="Date from:").pack(side=tk.LEFT, padx=2)
    widgets["stat_filt_date_frm"] = ttk.Entry(filter_frame1, width=10)
    widgets["stat_filt_date_frm"].insert(0, "week")
    widgets["stat_filt_date_frm"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="To:").pack(side=tk.LEFT, padx=2)
    widgets["stat_filt_date_to"] = ttk.Entry(filter_frame1, width=10)
    widgets["stat_filt_date_to"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="Symbols:").pack(side=tk.LEFT, padx=2)
    widgets["stat_filt_sym"] = ttk.Entry(filter_frame1, width=12)
    widgets["stat_filt_sym"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="Max $:").pack(side=tk.LEFT, padx=2)
    widgets["stat_max_trade_val"] = ttk.Entry(filter_frame1, width=10)
    widgets["stat_max_trade_val"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="Max qty:").pack(side=tk.LEFT, padx=2)
    widgets["stat_max_qty"] = ttk.Entry(filter_frame1, width=10)
    widgets["stat_max_qty"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="DTE: min").pack(side=tk.LEFT, padx=2)
    widgets["stat_dte_min"] = ttk.Entry(filter_frame1, width=8)
    widgets["stat_dte_min"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame1, text="max").pack(side=tk.LEFT, padx=2)
    widgets["stat_dte_max"] = ttk.Entry(filter_frame1, width=8)
    widgets["stat_dte_max"].pack(side=tk.LEFT, padx=2)

    # Filter row 2 - Exclude checkboxes
    filter_frame2 = ttk.Frame(frame)
    filter_frame2.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    ttk.Label(filter_frame2, text="Exclude: ").pack(side=tk.LEFT, padx=2)

    checkbox_configs = [
        ("-stat-NegPnL", "Neg PnL", False),
        ("-stat-PosPnL", "Pos PnL", False),
        ("-stat-stocks", "Stocks", True),
        ("-stat-options", "Options", False),
        ("-stat-bto", "BTO", False),
        ("-stat-sto", "STO", False),
    ]

    for key, text, default in checkbox_configs:
        var = tk.BooleanVar(value=default)
        widgets[key] = ttk.Checkbutton(filter_frame2, text=text, variable=var)
        widgets[key].var = var
        widgets[key].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame2, text="| Authors:").pack(side=tk.LEFT, padx=2)
    widgets["stat_exc_author"] = ttk.Entry(filter_frame2, width=12)
    widgets["stat_exc_author"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame2, text="Symbols:").pack(side=tk.LEFT, padx=2)
    widgets["stat_exc_sym"] = ttk.Entry(filter_frame2, width=12)
    widgets["stat_exc_sym"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame2, text="Channels:").pack(side=tk.LEFT, padx=2)
    widgets["stat_exc_chn"] = ttk.Entry(filter_frame2, width=12)
    widgets["stat_exc_chn"].pack(side=tk.LEFT, padx=2)

    # Update button
    update_frame = ttk.Frame(frame)
    update_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    widgets["_upd-stat_"] = ttk.Button(update_frame, text="Update", bootstyle="dark")
    widgets["_upd-stat_"].pack(side=tk.LEFT, padx=2)

    # Info text
    info_frame = ttk.Frame(frame)
    info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    info_text = (
        "PnL-actual = PnL from prices at the moment of alerted trade (as opposed to the prices claimed in the alert) \n"
        "diff = difference between actual and alerted, high BTO and low STC diffs is bad, alerts are delayed"
    )
    ttk.Label(info_frame, text=info_text, wraplength=800).pack(side=tk.LEFT, padx=2)

    # Table
    table_frame = ttk.Frame(frame)
    table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

    tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
    tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

    widgets["_stat_"] = Treeview(
        table_frame,
        columns=data_n_headers[1],
        show="tree headings",
        yscrollcommand=tree_scroll_y.set,
        xscrollcommand=tree_scroll_x.set,
    )

    tree_scroll_y.config(command=widgets["_stat_"].yview)
    tree_scroll_x.config(command=widgets["_stat_"].xview)

    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    widgets["_stat_"].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configure columns
    widgets["_stat_"].column("#0", width=50, minwidth=50)
    for idx, heading in enumerate(data_n_headers[1]):
        widgets["_stat_"].heading(f"#{idx + 1}", text=heading)
        widgets["_stat_"].column(f"#{idx + 1}", width=100, minwidth=50)

    # Insert data
    for row_idx, row_data in enumerate(values):
        tag = "evenrow" if row_idx % 2 == 0 else "oddrow"
        widgets["_stat_"].insert(
            "", tk.END, text=str(row_idx + 1), values=row_data, tags=(tag,)
        )

    widgets["_stat_"].tag_configure("oddrow", background="white")
    widgets["_stat_"].tag_configure("evenrow", background="lightgray")

    return frame, widgets


def create_chan_msg_frame(parent, chn, data_n_headers, font_body, font_header):
    """Create channel message history display"""
    frame = ttk.Frame(parent)
    widgets = {}

    if data_n_headers[0] == []:
        values = [["" * len(data_n_headers[1])]]
    else:
        values = data_n_headers[0]

    # Filter row
    filter_frame = ttk.Frame(frame)
    filter_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    ttk.Label(filter_frame, text="Filter:  Authors:").pack(side=tk.LEFT, padx=2)
    widgets[f"{chn}_filt_author"] = ttk.Entry(filter_frame, width=15)
    widgets[f"{chn}_filt_author"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame, text="Date from:").pack(side=tk.LEFT, padx=2)
    widgets[f"{chn}_filt_date_frm"] = ttk.Entry(filter_frame, width=10)
    widgets[f"{chn}_filt_date_frm"].insert(0, "week")
    widgets[f"{chn}_filt_date_frm"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame, text="To:").pack(side=tk.LEFT, padx=2)
    widgets[f"{chn}_filt_date_to"] = ttk.Entry(filter_frame, width=10)
    widgets[f"{chn}_filt_date_to"].pack(side=tk.LEFT, padx=2)

    ttk.Label(filter_frame, text="Message contains:").pack(side=tk.LEFT, padx=2)
    widgets[f"{chn}_filt_cont"] = ttk.Entry(filter_frame, width=20)
    widgets[f"{chn}_filt_cont"].pack(side=tk.LEFT, padx=2)

    # Update button
    update_frame = ttk.Frame(frame)
    update_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    widgets[f"{chn}_UPD"] = ttk.Button(update_frame, text="Update", bootstyle="dark")
    widgets[f"{chn}_UPD"].pack(side=tk.LEFT, padx=2)

    # Table
    table_frame = ttk.Frame(frame)
    table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

    tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
    tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

    widgets[f"{chn}_table"] = Treeview(
        table_frame,
        columns=data_n_headers[1],
        show="headings",
        yscrollcommand=tree_scroll_y.set,
        xscrollcommand=tree_scroll_x.set,
    )

    tree_scroll_y.config(command=widgets[f"{chn}_table"].yview)
    tree_scroll_x.config(command=widgets[f"{chn}_table"].xview)

    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    widgets[f"{chn}_table"].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configure columns
    for idx, heading in enumerate(data_n_headers[1]):
        widgets[f"{chn}_table"].heading(f"#{idx}", text=heading)
        widgets[f"{chn}_table"].column(f"#{idx}", width=100, minwidth=50)

    # Insert data
    for row_data in values:
        widgets[f"{chn}_table"].insert("", tk.END, values=row_data)

    return frame, widgets


def create_account_frame(parent, bksession, font_body, font_header):
    """Create account information display"""
    frame = ttk.Frame(parent)
    widgets = {}

    if bksession is None:
        label = ttk.Label(frame, text="No brokerage API provided in config.ini")
        label.pack(padx=20, pady=20)
        return frame, widgets

    acc_inf, ainf = gg.get_acc_bals(bksession)
    pos_tab, pos_headings = gg.get_pos(acc_inf)
    if not len(pos_tab):
        pos_tab = [["No positions"]]
    ord_tab, ord_headings, _ = gg.get_orders(acc_inf)

    # Account info row
    info_frame = ttk.Frame(frame)
    info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    ttk.Label(
        info_frame, text="Account ID:", font=(font_body[0], font_body[1], "bold")
    ).pack(side=tk.LEFT, padx=5)
    ttk.Label(info_frame, text=ainf["id"]).pack(side=tk.LEFT, padx=5)

    ttk.Label(
        info_frame, text="Balance:", font=(font_body[0], font_body[1], "bold")
    ).pack(side=tk.LEFT, padx=5)
    widgets["acc_b"] = ttk.Label(info_frame, text="$" + str(ainf["balance"]))
    widgets["acc_b"].pack(side=tk.LEFT, padx=5)

    ttk.Label(info_frame, text="Cash:", font=(font_body[0], font_body[1], "bold")).pack(
        side=tk.LEFT, padx=5
    )
    widgets["acc_c"] = ttk.Label(info_frame, text="$" + str(ainf["cash"]))
    widgets["acc_c"].pack(side=tk.LEFT, padx=5)

    ttk.Label(
        info_frame, text="Funds:", font=(font_body[0], font_body[1], "bold")
    ).pack(side=tk.LEFT, padx=5)
    widgets["acc_f"] = ttk.Label(info_frame, text="$" + str(ainf["funds"]))
    widgets["acc_f"].pack(side=tk.LEFT, padx=5)

    # Update button
    update_frame = ttk.Frame(frame)
    update_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    widgets["acc_updt"] = ttk.Button(update_frame, text="Update", bootstyle="dark")
    widgets["acc_updt"].pack(side=tk.LEFT, padx=2)

    # Tables container
    tables_frame = ttk.Frame(frame)
    tables_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Positions frame
    pos_frame = ttk.Frame(tables_frame)
    pos_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)

    ttk.Label(
        pos_frame,
        text="Positions",
        font=(font_body[0], font_body[1], "bold", "underline"),
    ).pack(side=tk.TOP, pady=5)

    pos_scroll_y = ttk.Scrollbar(pos_frame, orient=tk.VERTICAL)
    pos_scroll_x = ttk.Scrollbar(pos_frame, orient=tk.HORIZONTAL)

    widgets["_positions_"] = Treeview(
        pos_frame,
        columns=pos_headings,
        show="headings",
        yscrollcommand=pos_scroll_y.set,
        xscrollcommand=pos_scroll_x.set,
    )

    pos_scroll_y.config(command=widgets["_positions_"].yview)
    pos_scroll_x.config(command=widgets["_positions_"].xview)

    pos_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    pos_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    widgets["_positions_"].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for idx, heading in enumerate(pos_headings):
        widgets["_positions_"].heading(f"#{idx}", text=heading)
        widgets["_positions_"].column(f"#{idx}", width=100)

    for row_data in pos_tab:
        widgets["_positions_"].insert("", tk.END, values=row_data)

    # Orders frame
    ord_frame = ttk.Frame(tables_frame)
    ord_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)

    ttk.Label(
        ord_frame,
        text="Orders",
        font=(font_header[0], font_header[1], "bold", "underline"),
    ).pack(side=tk.TOP, pady=5)

    ord_scroll_y = ttk.Scrollbar(ord_frame, orient=tk.VERTICAL)
    ord_scroll_x = ttk.Scrollbar(ord_frame, orient=tk.HORIZONTAL)

    widgets["_orders_"] = Treeview(
        ord_frame,
        columns=ord_headings,
        show="headings",
        yscrollcommand=ord_scroll_y.set,
        xscrollcommand=ord_scroll_x.set,
    )

    ord_scroll_y.config(command=widgets["_orders_"].yview)
    ord_scroll_x.config(command=widgets["_orders_"].xview)

    ord_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    ord_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    widgets["_orders_"].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for idx, heading in enumerate(ord_headings):
        widgets["_orders_"].heading(f"#{idx}", text=heading)
        widgets["_orders_"].column(f"#{idx}", width=100)

    for row_data in ord_tab:
        widgets["_orders_"].insert("", tk.END, values=row_data)

    return frame, widgets


def update_acct_frame(bksession, widgets):
    """Update account information"""
    acc_inf, ainf = gg.get_acc_bals(bksession)
    pos_tab, _ = gg.get_pos(acc_inf)
    ord_tab, _, _ = gg.get_orders(acc_inf)

    widgets["acc_b"].config(text="$" + str(ainf["balance"]))
    widgets["acc_c"].config(text="$" + str(ainf["cash"]))
    widgets["acc_f"].config(text="$" + str(ainf["funds"]))

    # Update positions table
    widgets["_positions_"].delete(*widgets["_positions_"].get_children())
    for row_data in pos_tab:
        widgets["_positions_"].insert("", tk.END, values=row_data)

    # Update orders table
    widgets["_orders_"].delete(*widgets["_orders_"].get_children())
    for row_data in ord_tab:
        widgets["_orders_"].insert("", tk.END, values=row_data)


def create_config_frame(parent, fnt_h, cfg):
    """Create configuration panel - simplified version"""
    frame = ttk.Frame(parent)
    widgets = {}

    # Create scrollable canvas
    canvas = tk.Canvas(frame, highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Title
    title_label = ttk.Label(
        scrollable_frame,
        text="Session Configuration (change config.ini for permanent changes)",
        font=(fnt_h, 12, "bold"),
    )
    title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

    row = 1

    # General section
    ttk.Label(scrollable_frame, text="General Settings", font=(fnt_h, 10, "bold")).grid(
        row=row, column=0, sticky="w", padx=10, pady=5
    )
    row += 1

    var = tk.BooleanVar(value=cfg["discord"].getboolean("notify_alerts_to_discord"))
    widgets["cfg_discord.notify_alerts_to_discord"] = ttk.Checkbutton(
        scrollable_frame, text="Notify alerts to discord", variable=var
    )
    widgets["cfg_discord.notify_alerts_to_discord"].var = var
    widgets["cfg_discord.notify_alerts_to_discord"].grid(
        row=row, column=0, sticky="w", padx=20, pady=2
    )
    row += 1

    ttk.Label(scrollable_frame, text="Off market hours:").grid(
        row=row, column=0, sticky="w", padx=20, pady=2
    )
    widgets["cfg_general.off_hours"] = ttk.Entry(scrollable_frame, width=40)
    widgets["cfg_general.off_hours"].insert(0, cfg["general"]["off_hours"])
    widgets["cfg_general.off_hours"].grid(row=row, column=1, sticky="w", pady=2)
    row += 1

    # Long Trading section
    ttk.Separator(scrollable_frame, orient="horizontal").grid(
        row=row, column=0, columnspan=2, sticky="ew", pady=10
    )
    row += 1
    ttk.Label(scrollable_frame, text="Long Trading", font=(fnt_h, 10, "bold")).grid(
        row=row, column=0, sticky="w", padx=10, pady=5
    )
    row += 1

    # Add key configuration items (simplified for brevity)
    config_items = [
        (
            "cfg_general.do_BTO_trades",
            "Do BTO trades",
            "checkbox",
            cfg["general"].getboolean("Do_BTO_trades"),
        ),
        (
            "cfg_general.do_STC_trades",
            "Do STC trades",
            "checkbox",
            cfg["general"].getboolean("Do_STC_trades"),
        ),
        (
            "cfg_discord.authors_subscribed",
            "Authors subscribed:",
            "entry",
            cfg["discord"]["authors_subscribed"],
        ),
        (
            "cfg_order_configs.max_price_diff",
            "Max price diff:",
            "entry",
            cfg["order_configs"]["max_price_diff"],
        ),
        (
            "cfg_order_configs.trade_capital",
            "Trade capital ($):",
            "entry",
            cfg["order_configs"]["trade_capital"],
        ),
    ]

    for key, label, widget_type, default in config_items:
        if widget_type == "checkbox":
            var = tk.BooleanVar(value=default)
            widgets[key] = ttk.Checkbutton(scrollable_frame, text=label, variable=var)
            widgets[key].var = var
            widgets[key].grid(
                row=row, column=0, columnspan=2, sticky="w", padx=20, pady=2
            )
        else:
            ttk.Label(scrollable_frame, text=label).grid(
                row=row, column=0, sticky="w", padx=20, pady=2
            )
            widgets[key] = ttk.Entry(scrollable_frame, width=40)
            widgets[key].insert(0, default)
            widgets[key].grid(row=row, column=1, sticky="w", pady=2)
        row += 1

    # Save button
    ttk.Separator(scrollable_frame, orient="horizontal").grid(
        row=row, column=0, columnspan=2, sticky="ew", pady=10
    )
    row += 1
    widgets["cfg_button"] = ttk.Button(
        scrollable_frame, text="Save Configuration", bootstyle="success"
    )
    widgets["cfg_button"].grid(row=row, column=0, columnspan=2, pady=10)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    return frame, widgets


# Legacy compatibility functions
def layout_console(
    ttl="Discord messages from subscribed channels", key="-MLINE-__WRITE ONLY__"
):
    """Legacy wrapper for create_console_frame"""
    return None, key


def trigger_alerts_layout():
    """Legacy wrapper - returns empty layout, actual implementation uses create_trigger_alerts_frame"""
    return []


def layout_portfolio(data_n_headers, font_body, font_header):
    """Legacy wrapper - returns empty layout"""
    return []


def layout_traders(data_n_headers, font_body, font_header):
    """Legacy wrapper - returns empty layout"""
    return []


def layout_stats(data_n_headers, font_body, font_header):
    """Legacy wrapper - returns empty layout"""
    return []


def layout_chan_msg(chn, data_n_headers, font_body, font_header):
    """Legacy wrapper - returns empty layout"""
    return []


def layout_account(bksession, font_body, font_header):
    """Legacy wrapper - returns empty layout"""
    return [[]]


def update_acct_ly(bksession, window):
    """Legacy wrapper for updating account - no-op for now"""
    pass


def layout_config(fnt_h, cfg):
    """Legacy wrapper - returns empty layout"""
    return []
