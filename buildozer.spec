[app]

# (str) Title of your application
title = CaptchaSolver

# (str) Package name
package.name = captchasolver

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py is located
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to include (let empty to include all the files)
source.include_patterns = assets/*,images/*.jpg,images/*.png

# (list) List of inclusions using pattern matching (example: assets/*)
# source.include_patterns = assets/*

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,opencv,httpx,pillow,numpy

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (str) Android minimum API to use
android.minapi = 21

# (str) Android SDK version to use
android.sdk = 28

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (list) Features (added in python-for-android for android build)
# (list) List of features to enable/disable
android.features = androidx.appcompat, android.hardware.camera

# (str) The directory in which python-for-android should look for your application source code.
# source.include_exts = py

# (str) Extra file to include
# (list) Pattern of files to exclude (example: *.txt)
# android.wakelock = True

# (bool) If True, then a fixed Android launcher icon will be used
# Fixed launcher icon is overridden by 24x24 icon provided by buildozer.spec
# android.icon.custom = True

# (str) Custom launcher icon (32x32 image)
# customlauncher.icon = %(source.dir)s/data/icon.png

# (list) Custom java classes to add to the android project
# (list) Custom jar to include in classpath

# (list) android.add_custom_jars = /path/to/jar/file.jar

# (list) custom java classes
# (list) custom jar to include in classpath

# (list) extra dependencies for pythonforandroid to install
#android.p4a.extra_dependencies = pycryptodome, Pillow, google-api-python-client

# (str) Full name of the application (as it appears in the Android device launcher)
# full name = %(appname)s

# (str) The package domain to use (useful if you want to host multiple applications under the same package name)
# package.domain = %(package.domain)s

# (list) Additional requirements (these will be passed to p4a as arguments)
# android.additional_modules = yourmodule1, yourmodule2

# (str) Requirements list (these will be passed to p4a as arguments)
# additional requirements = yourmodule1, yourmodule2

# (str) Main Python file name (default is 'main.py')
# pythonfile = main.py

# (list) Additional jar to add to classpath
# android.add_jars = /path/to/jar/file.jar

# (list) Additional aars to add to classpath
# android.add_aars = /path/to/aar/file.aar

# (str) Android backup source APK
# backup source apk =

# (str) Main script file (default is 'main.py')
# android.p4a.mainfile = main.py

# (str) Android activity name (default is the same as package name)
# android.activity_name = captchasolver

# (list) Optional icon (all sizes)
#icon = %(source.dir)s/data/icon.png

# (list) Split apks (useful for large app)
#android.apksplits = %(source.dir)s/build/android/app
