# Burnstation
A free music distribution system

## Installation


#### Add Sources

    deb http://ftp.ccc.uba.ar/pub/linux/debian/debian/ squeeze main contrib non-free`

-------

#### Update & Install Dependencies

    sudo apt update && sudo apt install -y nano python-mysqldb python-ogg python-pyvorbis python-mutagen python-id3 python-dbus  python-dbus python-mutagen wodim genisoimage vorbis-tools sox eject mpg123 hal pmount python-pygame python-gst0.10 gstreamer0.10-alsa gstreamer0.10-plugins-base gstreamer0.10-plugins-base-apps gstreamer0.10-plugins-good gstreamer0.10-x mysql-server python-gtk2

-------

#### Setup & Permissions

`mkdir /var/spool/burnstation`

`mkdir /var/log/burnstation`

`chmod 777 /var/spool/burnstation`

`chmod 777 /var/log/burnstation`

`chmod 755 /usr/share/burnstation/burn.py`

`sudo mkdir /etc/burnstation/`

`sudo cp conf/burnstation2.conf /etc/burnstation/`

`chmod +x /usr/share/burnstation/bin/burnstation2`

-------

#### Gamepad Config

Define your gamepad in `/etc/burnstation/burnstation2.conf`

Use nano if you want:

`sudo nano /etc/burnstation/burnstation2.conf`

Save your work in nano by pressing `CTRL + O` then exit by pressing `CTRL + X`

-------

#### Start on boot/Autostart

```
mkdir ~/.icewm
echo "/usr/local/bin/burnstation2 loop &" > ~/.icewm/startup
chmod +x ~/.icewm/startup
```

-------

#### Disable Automatic USB Device Management

*Check /etc/fstab and comment out (disable) USB handling.*

*The config line might look similar to the following:*

> #/dev/sdb1       /media/usb0     auto    rw,user,noauto  0       0

