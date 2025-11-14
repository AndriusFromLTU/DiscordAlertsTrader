#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 18:18:43 2021
Migrated to tkinter/ttkbootstrap on Nov 13 2025

@author: adonay
"""

import os
import os.path as op
import queue
import re
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk

import matplotlib.pyplot as plt
import pandas as pd
import ttkbootstrap as ttk_boot
from ttkbootstrap.constants import *

from DiscordAlertsTrader import gui_generator as gg
from DiscordAlertsTrader import gui_layouts as gl
from DiscordAlertsTrader.brokerages import get_brokerage
from DiscordAlertsTrader.configurator import cfg, channel_ids
from DiscordAlertsTrader.discord_bot import DiscordBot
from DiscordAlertsTrader.message_parser import ordersymb_to_str, parse_trade_alert


def match_authors(author_str: str) -> str:
    """Author have an identifier in discord, it will try to find full author name"""
    if "#" in author_str:
        return author_str
    authors = []
    for chn in channel_ids.keys():
        fname = op.join(cfg["general"]["data_dir"], f"{chn}_message_history.csv")
        if op.exists(fname):
            at = pd.read_csv(fname)["Author"].unique()
            authors.extend(at)
    authors = list(dict.fromkeys(authors))

    authors += cfg["discord"]["authors_subscribed"].split(",")
    authors = [a for a in authors if author_str.lower() in a.lower()]
    if len(authors) == 0:
        author = author_str
    elif len(authors) > 1:
        author = author_str
    else:
        author = authors[0]
    return author


def split_alert_message(gui_msg):
    """Split alert message into author and message"""
    # extra comas
    if len(gui_msg.split(",")) > 2:
        splt = gui_msg.split(",")
        author = splt[0]
        msg = ",".join(splt[1:])
    # one coma
    elif len(gui_msg.split(",")) == 2:
        author, msg = gui_msg.split(",")
    # one colon
    elif len(gui_msg.split(":")) == 2:
        author, msg = gui_msg.split(":")
    # extra colons
    elif len(gui_msg.split(":")) > 2:
        splt = gui_msg.split(":")
        author = splt[0]
        msg = ":".join(splt[1:])
    # no colon or coma
    else:
        print("No colon or coma in message, author not found, assuming no author")
        author = "author"
        msg = gui_msg
    return author, msg


def get_live_quotes(symbol, tracker, max_delay=2):
    """Get live quotes for a symbol"""
    dir_quotes = cfg["general"]["data_dir"] + "/live_quotes"

    fquote = f"{dir_quotes}/{symbol}.csv"
    if not op.exists(fquote):
        quote = tracker.price_now(symbol, "both")
        if quote is None:
            return None, None
        return quote

    with open(fquote, "r") as f:
        quotes = f.readlines()

    now = time.time()
    get_live = False
    try:
        tmp = quotes[-1].split(",")  # in s
        if len(tmp) == 3:
            timestamp, bid, ask = tmp
        else:
            timestamp, ask = tmp
            bid = ask
        ask = ask.strip().replace("\n", "")
        quote = [ask, bid]
    except:
        print("Error reading quote", symbol, quotes[-1])
        get_live = True

    timestamp = eval(timestamp)
    if max_delay is not None:
        if now - timestamp > max_delay:
            get_live = True

    if get_live:
        quote = tracker.price_now(symbol, "both")
        if quote is None:
            return None, None
        return quote
    return quote


def quotes_plotting(symbol, trader=None, tracker=None):
    """Plot historical quotes for a symbol"""
    dir_quotes = cfg["general"]["data_dir"] + "/live_quotes"

    fquote = f"{dir_quotes}/{symbol}.csv"
    if not op.exists(fquote):
        return None

    quotes = pd.read_csv(fquote)

    quotes["date"] = pd.to_datetime(
        quotes["timestamp"], unit="s", utc=True
    ).dt.tz_convert("America/New_York")
    quotes["date"] = quotes["date"].dt.tz_localize(None)
    quotes["ask"] = quotes[" quote_ask"]
    quotes["bid"] = quotes[" quote"]

    quotes = quotes[quotes["date"].dt.date == datetime.now().date()]
    quotes = quotes[quotes["ask"] > 0]
    quotes.set_index("date", inplace=True)

    quotes[["ask", "bid"]].plot(alpha=0.5)

    for tt in [trader, tracker]:
        if tt is not None:
            tts = tt.portfolio[
                (tt.portfolio["Symbol"] == symbol)
                & (
                    pd.to_datetime(tt.portfolio["Date"]).dt.date
                    == datetime.now().date()
                )
            ]
            if len(tts):
                for ix, row in tts.iterrows():
                    if (
                        str(tt.__class__)
                        == "<class 'DiscordAlertsTrader.alerts_tracker.AlertsTracker'>"
                    ):
                        plt.plot(pd.to_datetime(row["Date"]), row["Price"], "go")
                        plt.text(
                            pd.to_datetime(row["Date"]),
                            row["Price"] * 1.009,
                            f"track:{row['Trader']}: {row['Type']}",
                            fontsize=12,
                            color="g",
                            rotation=45,
                        )
                        if not pd.isna(row["STC-Date"]):
                            plt.plot(
                                pd.to_datetime(row["STC-Date"]), row["STC-Price"], "ro"
                            )
                            plt.text(
                                pd.to_datetime(row["STC-Date"]),
                                row["STC-Price"] * 1.009,
                                f"track:{row['Trader']}: Closed",
                                fontsize=12,
                                color="red",
                                rotation=45,
                            )
                    else:
                        plt.plot(pd.to_datetime(row["Date"]), row["Price"], "go")
                        plt.plot(pd.to_datetime(row["Date"]), row["Price"], "kx")
                        plt.text(
                            pd.to_datetime(row["Date"]),
                            row["Price"] * 1.009,
                            f"port:{row['Trader']} {row['Type']}",
                            fontsize=12,
                            color="g",
                            rotation=45,
                        )
                        cols = [
                            c
                            for c in tts.columns
                            if c.startswith("STC") and c.endswith("-Date")
                        ]
                        for c in cols:
                            if pd.isna(row[c]):
                                continue
                            plt.plot(
                                pd.to_datetime(row[c]),
                                row[c.split("-")[0] + "-Price"],
                                "ro",
                            )
                            plt.plot(
                                pd.to_datetime(row[c]),
                                row[c.split("-")[0] + "-Price"],
                                "kx",
                            )
                            plt.text(
                                pd.to_datetime(row[c]),
                                row[c.split("-")[0] + "-Price"] * 1.009,
                                f"port:{row['Trader']}: Closed",
                                fontsize=12,
                                color="red",
                                rotation=45,
                            )
    plt.tight_layout()
    plt.title(symbol)
    plt.show(block=False)


class DiscordAlertsTraderGUI:
    def __init__(self):
        print("Initializing GUI...")

        # Create main window using ttkbootstrap
        self.root = ttk_boot.Window(themename="darkly")
        self.root.title("Discord Alerts Trader")
        self.root.geometry("1400x900")

        # Initialize data structures
        self.widgets = {}
        self.gui_data = {}
        self.port_exc = {
            "Closed": False,
            "Open": False,
            "NegPnL": False,
            "PosPnL": False,
            "live PnL": False,
            "stocks": True,
            "options": False,
            "bto": False,
            "stc": False,
            "Canceled": True,
            "Rejected": False,
        }
        self.track_exc = self.port_exc.copy()
        self.stat_exc = self.port_exc.copy()

        # Initialize brokerage session
        self.bksession = get_brokerage()
        bk_name = "None" if self.bksession is None else self.bksession.name
        self.root.title(f"Discord Alerts Trader - with broker {bk_name}")

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self.create_message_tabs()
        self.create_portfolio_tab()
        self.create_analysts_tab()
        self.create_stats_tab()
        if self.bksession is not None:
            self.create_account_tab()
        self.create_config_tab()

        # Create trigger alerts section at bottom
        self.create_trigger_section()

        # Initialize Discord bot
        print("Initializing Discord bot...")
        self.trade_events = queue.Queue(maxsize=20)
        self.alistner = DiscordBot(self.trade_events, brokerage=self.bksession, cfg=cfg)

        # Start background threads
        self.start_background_threads()

        # Start event loops
        self.root.after(100, self.check_events)

        print("GUI initialization complete!")

    def create_message_tabs(self):
        """Create message console tabs"""
        # Msgs Subs tab
        msgs_subs_frame, self.msgs_subs_text, _ = gl.create_console_frame(
            self.notebook, "Discord messages only from subscribed authors", "-MLINEsub-"
        )
        self.notebook.add(msgs_subs_frame, text="Msgs Subs")
        self.widgets["-MLINEsub-"] = self.msgs_subs_text

        # Msgs All tab
        msgs_all_frame, self.msgs_all_text, _ = gl.create_console_frame(
            self.notebook, "Discord messages from all the channels", "-MLINE-"
        )
        self.notebook.add(msgs_all_frame, text="Msgs All")
        self.widgets["-MLINE-"] = self.msgs_all_text

    def create_portfolio_tab(self):
        """Create portfolio tab"""
        print("Creating portfolio tab...")
        self.gui_data["port"] = gg.get_portf_data()
        port_frame, port_widgets = gl.create_portfolio_frame(
            self.notebook,
            self.gui_data["port"],
            ("Helvetica", 10),
            ("Helvetica", 11, "bold"),
        )
        self.notebook.add(port_frame, text="Portfolio")
        self.widgets.update(port_widgets)

        # Bind update button
        if "_upd-portfolio_" in port_widgets:
            port_widgets["_upd-portfolio_"].config(command=self.update_portfolio)

        # Bind checkboxes
        for key in self.port_exc.keys():
            checkbox_key = f"-port-{key}"
            if checkbox_key in port_widgets:
                port_widgets[checkbox_key].config(
                    command=lambda k=key: self.toggle_port_filter(k)
                )

    def create_analysts_tab(self):
        """Create analysts portfolio tab"""
        print("Creating analysts tab...")
        self.gui_data["trades"] = gg.get_tracker_data()
        track_frame, track_widgets = gl.create_traders_frame(
            self.notebook,
            self.gui_data["trades"],
            ("Helvetica", 10),
            ("Helvetica", 11, "bold"),
        )
        self.notebook.add(track_frame, text="Analysts Portfolio")
        self.widgets.update(track_widgets)

        # Bind update button
        if "_upd-track_" in track_widgets:
            track_widgets["_upd-track_"].config(command=self.update_analysts)

    def create_stats_tab(self):
        """Create statistics tab"""
        print("Creating stats tab...")
        self.gui_data["stats"] = gg.get_stats_data()
        stats_frame, stats_widgets = gl.create_stats_frame(
            self.notebook,
            self.gui_data["stats"],
            ("Helvetica", 10),
            ("Helvetica", 11, "bold"),
        )
        self.notebook.add(stats_frame, text="Analysts Stats")
        self.widgets.update(stats_widgets)

        # Bind update button
        if "_upd-stat_" in stats_widgets:
            stats_widgets["_upd-stat_"].config(command=self.update_stats)

    def create_account_tab(self):
        """Create account tab"""
        print("Creating account tab...")
        acc_frame, acc_widgets = gl.create_account_frame(
            self.notebook, self.bksession, ("Helvetica", 10), ("Helvetica", 11, "bold")
        )
        self.notebook.add(acc_frame, text="Account")
        self.widgets.update(acc_widgets)

        # Bind update button
        if "acc_updt" in acc_widgets:
            acc_widgets["acc_updt"].config(command=self.update_account)

    def create_config_tab(self):
        """Create configuration tab"""
        print("Creating config tab...")
        cfg_frame, cfg_widgets = gl.create_config_frame(self.notebook, "Helvetica", cfg)
        self.notebook.add(cfg_frame, text="Config")
        self.widgets.update(cfg_widgets)

        # Bind save button
        if "cfg_button" in cfg_widgets:
            cfg_widgets["cfg_button"].config(command=self.save_config)

    def create_trigger_section(self):
        """Create trigger alerts section at bottom"""
        trigger_frame, trigger_widgets = gl.create_trigger_alerts_frame(self.root)
        trigger_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.widgets.update(trigger_widgets)

        # Bind trigger button
        if "-subm-alert" in trigger_widgets:
            trigger_widgets["-subm-alert"].config(command=self.trigger_alert)

        # Bind toggle button
        if "-toggle" in trigger_widgets:
            trigger_widgets["-toggle"].config(command=self.toggle_alert_buttons)

    def toggle_alert_buttons(self):
        """Toggle visibility of alert action buttons"""
        toggle_btn = self.widgets.get("-toggle")
        if toggle_btn:
            current_text = toggle_btn.cget("text")
            new_text = "▼" if current_text == "▲" else "▲"
            toggle_btn.config(text=new_text)

            # Toggle visibility of action buttons
            visible = new_text == "▼"
            button_keys = [
                "-alert_to-",
                "-alert_BTO",
                "-alert_STC",
                "-alert_STO",
                "-alert_BTC",
                "-alert_exitupdate",
                "-alert_quotes",
                "-alert_plot",
                "-alert_tome",
                "-alert_tomeshort",
                "-alert_exits",
            ]

            for key in button_keys:
                if key in self.widgets:
                    if visible:
                        self.widgets[key].pack(side=tk.LEFT, padx=2)
                    else:
                        self.widgets[key].pack_forget()

    def update_portfolio(self):
        """Update portfolio display"""
        print("Updating portfolio...")
        dt, _ = gg.get_portf_data(self.port_exc)
        if "_portfolio_" in self.widgets:
            tree = self.widgets["_portfolio_"]
            # Clear existing data
            for item in tree.get_children():
                tree.delete(item)
            # Insert new data
            for row_idx, row_data in enumerate(dt):
                tag = "evenrow" if row_idx % 2 == 0 else "oddrow"
                tree.insert(
                    "", tk.END, text=str(row_idx + 1), values=row_data, tags=(tag,)
                )

    def update_analysts(self):
        """Update analysts portfolio display"""
        print("Updating analysts portfolio...")
        dt, _ = gg.get_tracker_data(self.track_exc)
        if "_track_" in self.widgets:
            tree = self.widgets["_track_"]
            for item in tree.get_children():
                tree.delete(item)
            for row_idx, row_data in enumerate(dt):
                tag = "evenrow" if row_idx % 2 == 0 else "oddrow"
                tree.insert(
                    "", tk.END, text=str(row_idx + 1), values=row_data, tags=(tag,)
                )

    def update_stats(self):
        """Update statistics display"""
        print("Updating stats...")
        dt, _ = gg.get_stats_data(self.stat_exc)
        if "_stat_" in self.widgets:
            tree = self.widgets["_stat_"]
            for item in tree.get_children():
                tree.delete(item)
            for row_idx, row_data in enumerate(dt):
                tag = "evenrow" if row_idx % 2 == 0 else "oddrow"
                tree.insert(
                    "", tk.END, text=str(row_idx + 1), values=row_data, tags=(tag,)
                )

    def update_account(self):
        """Update account information"""
        print("Updating account...")
        if self.bksession:
            gl.update_acct_frame(self.bksession, self.widgets)

    def toggle_port_filter(self, key):
        """Toggle portfolio filter"""
        checkbox_key = f"-port-{key}"
        if checkbox_key in self.widgets:
            self.port_exc[key] = self.widgets[checkbox_key].var.get()
            self.update_portfolio()

    def save_config(self):
        """Save configuration changes"""
        print("Saving configuration...")
        for k, widget in self.widgets.items():
            if k.startswith("cfg"):
                f1, f2 = k.replace("cfg_", "").split(".")
                if hasattr(widget, "var"):  # Checkbutton
                    cfg[f1][f2] = str(widget.var.get())
                elif isinstance(widget, (ttk.Entry, ttk.Combobox)):
                    cfg[f1][f2] = widget.get()
        print("Configuration saved!")

    def trigger_alert(self):
        """Trigger an alert manually"""
        msg_widget = self.widgets.get("-subm-msg")
        chan_widget = self.widgets.get("_chan_trigg_")

        if msg_widget and chan_widget:
            try:
                gui_msg = msg_widget.get()
                author, msg = split_alert_message(gui_msg)
                author = match_authors(author.strip())
                msg = msg.strip().replace("SPXW", "SPX")
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                chan = "GUI_" + chan_widget.get()

                new_msg = pd.Series(
                    {
                        "AuthorID": None,
                        "Author": author,
                        "Date": date,
                        "Content": msg,
                        "Channel": chan,
                    }
                )
                self.alistner.new_msg_acts(new_msg, from_disc=False)
                print(f"Alert triggered: {author} - {msg}")
            except Exception as e:
                print(f"Error triggering alert: {e}")

    def start_background_threads(self):
        """Start background update threads"""

        def update_portfolios_loop():
            while True:
                time.sleep(60)
                try:
                    self.root.after(0, self.update_portfolio)
                    time.sleep(2)
                    self.root.after(0, self.update_analysts)
                except:
                    pass

        threading.Thread(target=update_portfolios_loop, daemon=True).start()

        def run_discord_client():
            if len(cfg["discord"]["discord_token"]) < 50:
                str_prt = "Discord token not provided, no discord messages will be received. Add user token in config.ini"
                print(str_prt)
                self.trade_events.put([str_prt, "", "red"])
                return
            self.alistner.run(cfg["discord"]["discord_token"])

        threading.Thread(target=run_discord_client, daemon=True).start()

    def check_events(self):
        """Check for Discord events and update GUI"""
        try:
            while True:
                event_feedb = self.trade_events.get_nowait()
                text = event_feedb[0]

                # Determine if message is from subscribed author
                subs_auth_msg = False
                if len(event_feedb) > 1 and event_feedb[1] == "blue":
                    try:
                        author = event_feedb[0].split("\n\t")[1].split(":")[0]
                        chan = event_feedb[0].split(": \n\t")[0].split(" ")[-1]
                        auth_subs = cfg["discord"]["authors_subscribed"].split(",")
                        auth_subs = [i.split("#")[0].strip() for i in auth_subs]

                        if any(a == author for a in auth_subs):
                            subs_auth_msg = True
                    except:
                        pass

                # Update message consoles
                if "-MLINE-" in self.widgets:
                    self.widgets["-MLINE-"].insert(tk.END, text + "\n")
                    self.widgets["-MLINE-"].see(tk.END)

                if subs_auth_msg and "-MLINEsub-" in self.widgets:
                    self.widgets["-MLINEsub-"].insert(tk.END, text + "\n")
                    self.widgets["-MLINEsub-"].see(tk.END)

        except queue.Empty:
            pass
        finally:
            # Schedule next check
            self.root.after(100, self.check_events)

    def run(self):
        """Run the GUI main loop"""
        self.root.mainloop()


def gui():
    """Entry point for GUI"""
    app = DiscordAlertsTraderGUI()
    app.run()


if __name__ == "__main__":
    gui()
