#!/usr/bin/env python
# coding: utf-8
"""
TrayNotifier

A simple tray notifier for Windows that detects when a document has changed. Tested on Windows 7, but should work
on XP and above. File changes are determined by taking a hash of the downloaded page and comparing to the last recorded
hash.

You must supply two icons in the same directory that represent its two states: alerting and non-alerting. By default,
it will look for icon_ok.png and icon_alert.png.

When a change is detected, a notification balloon is displayed and the notifier switches into alert mode. When alerting,
the icon will change to the alert icon. If the notifier should flash while alerting (true by default), it will 
change between the alert and standard icon.

Left-clicking the icon will open the page in a webbrowser; if the notifier is alerting, the alert will be cancelled.

Right-clicking the icon will close the application and remove it from the tray.
"""

import webbrowser
import hashlib
import urllib2
import os
import sys

import wx

LAST_HASH_FILENAME = 'last_hash.txt'
ICON_OK_FILENAME = 'icon_ok.png'
ICON_ALERT_FILENAME = 'icon_alert.png'

class TrayNotifier(wx.TaskBarIcon):

    def __init__(self, title, url, refresh_rate_milliseconds=60*60*1000, notification_timeout=10*1000, flash_on_alert=True):

        super(TrayNotifier, self).__init__()

        # Make sure we change the working directory so we can find the icon files and hash
        os.chdir(sys.path[0])

        # Set up alert state variables
        self.is_alerting = False

        self.flash_on_alert = flash_on_alert

        self.flash_state_alert = False

        self.blink_rate_msec = 500

        # Configure balloon title and url to check
        self.title = title

        self.url = url

        self.balloon_text = self.url

        # Set up icon
        self.icon_ok = wx.IconFromBitmap(wx.Bitmap(ICON_OK_FILENAME))

        self.icon_alert = wx.IconFromBitmap(wx.Bitmap(ICON_ALERT_FILENAME))

        self.SetIcon(self.icon_ok, title)

        # Set up mouse events
        self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.left_click)

        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.right_click)

        # Set up notification pop-up timeout
        self.notification_timeout = notification_timeout

        # Configure timer defaults
        self.id = wx.NewId()

        self.refresh_rate_milliseconds = refresh_rate_milliseconds

        self.timer = None

        self.set_update_timer(self.refresh_rate_milliseconds)

        # Configure flash timer
        self.flash_timer = None

        if flash_on_alert:
            self.flash_timer_id = wx.NewId()

            self.flash_timer = wx.Timer(self, self.flash_timer_id)

            self.flash_timer.Start(self.blink_rate_msec)

            wx.EVT_TIMER(self, self.flash_timer_id, self.flash_icon)


    def set_notification_timeout(self, msecs):
        """Amount of time in msecs that the notification bubble will stay visible.
        WX will clamp the timeout between 10 and 30 seconds
        
        """
        self.notification_timeout = msecs

    def set_update_timer(self, msecs):

        self.refresh_rate_milliseconds = msecs

        try:
            self.timer.Stop()
        except:
            pass

        self.timer = wx.Timer(self, self.id)

        self.timer.Start(self.refresh_rate_milliseconds)

        wx.EVT_TIMER(self, self.id, self.timer_update)

    def left_click(self, ev):
        if self.is_alerting:
            self.toggle_alert()
        webbrowser.open(self.url)

    def right_click(self, ev):
        self.close()

    def timer_update(self, ev):
        if not self.is_alerting:
            msg = ""
            try:
                f = urllib2.urlopen(self.url)
                h = self.generate_hash(f.read())
                if self.check_page_updated(h):
                    self.toggle_alert()
                    msg = self.balloon_text
            except urllib2.HTTPError, e:
                msg = 'HTTPError: ' + str(e.code)
            except urllib2.URLError, e:
                msg = 'URLError: ' + str(e.reason)
            except Exception, e:
                msg = 'Error: ' + str(e)
            
            if msg:
                self.ShowBalloon(self.title, msg, msec=self.notification_timeout)

    def close(self):
        self.timer.Stop()

        wx.CallAfter(self.Destroy)

    def toggle_alert(self):
        self.is_alerting = not self.is_alerting

        if self.is_alerting:
            if self.flash_timer is not None:
                self.flash_timer.Start(self.blink_rate_msec)
            self.set_alert_icon()

        else:
            if self.flash_timer is not None:
                self.flash_timer.Stop()
            self.set_ok_icon()


    def set_alert_icon(self):
        self.SetIcon(self.icon_alert, self.title)

    def set_ok_icon(self):
        self.SetIcon(self.icon_ok, self.title)

    def flash_icon(self, ev):
        if self.is_alerting:
            if self.flash_state_alert:
                self.set_ok_icon()
            else:
                self.set_alert_icon()

            self.flash_state_alert = not self.flash_state_alert

    def generate_hash(self, string_to_hash):
        return hashlib.sha1(string_to_hash).hexdigest()

    def set_last_hash(self, new_hash):
        with open(LAST_HASH_FILENAME, 'w') as f:
            f.write(new_hash)

    def check_page_updated(self, new_hash):
        existing_hash = ''

        try:
            with open(LAST_HASH_FILENAME, 'r') as f:
                existing_hash = f.read()
        except:
            pass

        if existing_hash != new_hash:
            self.set_last_hash(new_hash)
            return True
        else:
            return False

if __name__ == '__main__':
    app = wx.App()
    notifier = TrayNotifier("Update notifier", "http://backstrip.net")
    app.MainLoop()
