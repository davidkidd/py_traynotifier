py_traynotifier
===============

Tray notifier for Windows that detects when a document has changed and displays a notification. I wrote this because I needed to keep an eye on some log files stored served up on the network. 

Note that file changes are determined by taking a hash of the downloaded page and comparing to the last recorded
hash. It should only be used for simple, static pages.

You must supply two icons in the same directory that represent its two states: alerting and non-alerting. By default,
it will look for icon_ok.png and icon_alert.png.

When a change is detected, a notification balloon is displayed and the notifier switches into alert mode. When alerting,
the icon will change to the alert icon. If the notifier should flash while alerting (true by default), it will 
change between the alert and standard icon.

Left-clicking the icon will open the page in a webbrowser; if the notifier is alerting, the alert will be cancelled.

Right-clicking the icon will close the application and remove it from the tray.

Example:

    app = wx.App()
    notifier = TrayNotifier("Update notifier", "http://example.com/page_to_check.html")
    app.MainLoop()

By default, this will check the page every hour. To change the interval to 60 seconds:

    notifier = TrayNotifier("Update notifier", "http://example.com/page_to_check.html", refresh_rate_milliseconds=60*1000)

    
