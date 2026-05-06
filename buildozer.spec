[app]
title = Kids Lab
package.name = kidslab
package.domain = io.kidslab
source.dir = .
source.include_exts = py,png,jpg,ttf,wav,json
version = 0.1
requirements = python3,pygame,numpy
orientation = landscape
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 1
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
android.arch = armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
