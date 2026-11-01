# M4 spike: Mac results (evidence copy)

This is an evidence-only copy for the planning repo. The source record is `docs/m4-spike.md` in the product repo on branch `m4-spike`, commit **`c3c3739f017a0c24623b481e569193f3c3e28570`** (parent `1673b97fb97d2612f42fa28c6fe07caa2a937bb3`, not pushed). The owner ran the steps on 1 Nov 2026 and pasted the Terminal output into the project thread. Everything below is copied from that output. Where something wasn't captured, it says **not captured**.

## Mac and tools
- MacBook Pro (Apple silicon), about 186 GiB free on `/` (step 0). `~/.android` didn't exist before the test.
- Every tool was installed user-local under `~/stargate-spike`:

| Item | Version | SHA-256 | Size |
|---|---|---|---|
| Temurin JDK tarball (aarch64 mac) | 17.0.21+9 | `78b08c7f5a0598242d5719c022e19479cb4a3aa45c37c19726a757a469ed1c15` | 177 MB (curl progress) |
| Command-line tools zip (mac arm64, 15859902) | 22.0 | `835b62a26162b229b441d1f6d4680383815a270809eb33522c0d480fa5002c4e` | 148 MB (curl progress) |
| platform-tools / adb | 37.0.1 (1.0.41) | not captured (installed through sdkmanager) | not captured |
| emulator | 37.2.13.0 (build 16740729) | not captured (installed through sdkmanager) | not captured |
| `system-images;android-34;default;arm64-v8a` package | not captured | package archive hash **not captured** | not captured |

## Images and APK

| File | SHA-256 | Bytes |
|---|---|---|
| Stock `sdk/system-images/android-34/default/arm64-v8a/system.img` | `250ee9bb4e87b7beb5755a3b6984822bcf4335cd2d80701ac2e5ce9fb9da105d` | 1622147072 |
| Repacked `system-stargate-a.img` (Safari unpacked the .gz) | `58961c2024ab3506ed790bf156690cf2d4542889eb05b4afa688133c27cd20e5` | 1622147072 |
| Repacked `system-stargate-a.img.gz` (codespace copy) | `854a467577301c22e1b1e7cf1a5c311b57bbe214aa062db4d34043bb91e11f86` (from the spike manifest; the Mac copy was unpacked by Safari, so it wasn't re-hashed on the Mac) | 639251897 (codespace `ls -l`) |
| `stargate-launcher.apk` (Path B) | `81048cafae18d901b4aa34514c533522d1779f6ff22ce1476bde73de80a6150d` | 8619 |

The other files in the stock system-image folder on the Mac (from `ls -l`): `encryptionkey.img` 18874368, `kernel-ranchu` 12784248, `ramdisk.img` 1791657, `userdata.img` 1048576, `vendor.img` 96468992, plus `advancedFeatures.ini`, `build.prop`, `VerifiedBootParams.textproto`, `source.properties`, `package.xml`, `NOTICE.txt` and `data/`. Their hashes were **not captured**.

**Transfer:** the codespace file-explorer download produced 9-byte files for the image twice. A private forwarded port worked: `/usr/local/bin/python3 -m http.server 8765 --bind 127.0.0.1` in `/workspaces/m4-tools`, opened from the Ports tab.

## AVDs
`avdmanager create avd -n stargate-spike-{stock,a,b} -k "system-images;android-34;default;arm64-v8a" -d pixel_7 --force`. It printed "Could not load devices from …/devices.xml" for each, but all three AVDs were created. `config.ini` has `hw.device.name=pixel_7` and `hw.ramSize=2G` for each.

## Stock boot (passed)
```
emulator -avd stargate-spike-stock -no-snapshot -wipe-data > stock-boot.log 2>&1 &
adb devices                      -> emulator-5554 only
getprop sys.boot_completed       -> 1
emu avd name                     -> stargate-spike-stock
adb root; id; ro.build.type      -> uid=0(root) ... context=u:r:su:s0 / userdebug
emu kill; adb devices            -> empty
```

## Path A (passed with -sysdir)
AVD `stargate-spike-a`. It was booted only with `-no-snapshot -wipe-data`, and never with `-writable-system`.

1. **Attempt 1:** `emulator -avd stargate-spike-a -no-snapshot -wipe-data -system $SG/system-stargate-a.img`. The emulator exited at once: `ERROR | no init encryptionkey.img`, `FATAL | Encryption is requested but failed to create encrypt partition.`
2. **Attempt 2:** with the stock `encryptionkey.img` copied to `~/stargate-spike/`, the same command plus `-no-metrics` booted. The log said "Boot completed in 14525 ms" and `sys.boot_completed` read 1, with avd name `stargate-spike-a`. But `cat /system/stargate-marker.txt` gave **No such file or directory**, so this run did not boot the repacked image. This was observed on this Mac with emulator 37.2.13.0. It isn't claimed as general emulator behaviour.
3. **Attempt 3 (passed):** a sysdir of symlinks to every file in the stock system-image folder, with `system.img` replaced:
   ```
   mkdir -p patha-sysdir
   for f in $SG/sdk/system-images/android-34/default/arm64-v8a/*; do ln -sf "$f" patha-sysdir/; done
   rm patha-sysdir/system.img
   ln -s $SG/system-stargate-a.img patha-sysdir/system.img
   ls -l patha-sysdir/system.img  -> patha-sysdir/system.img -> /Users/gabriellporfirio/stargate-spike/system-stargate-a.img
   emulator -avd stargate-spike-a -sysdir $SG/patha-sysdir -no-snapshot -wipe-data -no-metrics > patha-boot2.log 2>&1 &
   ```
   Every adb command run after boot, in order:
   ```
   adb -s emulator-5554 wait-for-device
   adb devices                                   -> emulator-5554 only
   (loop) adb -s emulator-5554 shell getprop sys.boot_completed   -> loop exited (see note)
   grep -i "systemPath\|system.img" patha-boot2.log               -> no output
   adb -s emulator-5554 emu avd name             -> stargate-spike-a
   adb -s emulator-5554 shell 'cat /system/stargate-marker.txt; cat /stargate-marker.txt; ls / /system | grep -i stargate'
       -> selection=stargate-spike-a
          random=5c056da9fc167da1caf8d9c05d1040d1
          cat: /stargate-marker.txt: No such file or directory
          stargate-marker.txt
   adb -s emulator-5554 exec-out screencap -p > patha-screen.png
   adb -s emulator-5554 emu kill
   adb devices                                   -> empty
   ```
   No `install`, `push`, `remount` or `root` was run in this boot.
   - **Note:** in attempt 3 the separate `getprop sys.boot_completed` read-out was **not captured**. The wait loop exits either when it reads 1 or after 10 minutes. The marker read and the screenshot that follow depend on a running system.
   - `patha-screen.png` was **not shared**.

## Path B (passed)
```
emulator -avd stargate-spike-b -no-snapshot -wipe-data -no-metrics > pathb-boot.log 2>&1 &
adb devices                                     -> emulator-5554 only
(loop) getprop sys.boot_completed               -> loop exited
adb -s emulator-5554 install -r $SG/stargate-launcher.apk                                   -> Performing Streamed Install / Success
adb -s emulator-5554 shell cmd package set-home-activity com.stargate.launcher/.HomeActivity -> Success
adb -s emulator-5554 shell input keyevent KEYCODE_HOME
adb -s emulator-5554 exec-out screencap -p > home-b.png
adb -s emulator-5554 emu kill; adb devices      -> empty
```
The home screen shows "StarGate" and "Services: Files, Assistant": [m4-spike-path-b-home.png](m4-spike-path-b-home.png).

## Conclusion
Path A booted the repacked image, and its unique marker read back from the running system, with no install or push. So, per M4 §2, M4 takes Route A. Path B also works and stays the fallback.
