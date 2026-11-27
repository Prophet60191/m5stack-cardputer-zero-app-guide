# Update an existing app without losing its data

The [official CardputerZero Template](https://github.com/CardputerZero/Template)
and [AppBuilder quickstart](https://github.com/CardputerZero/AppBuilder/blob/main/docs/QUICKSTART.md)
show how to start, build, and publish an app. This worked example covers what
happens after someone has installed it and saved something they want to keep.

**What you’ll verify:** the installer upgrades the same app, the running
scheduler comes from the newly installed package, and a saved alarm survives
both the upgrade and a rollback. These are three different checks.

## 1. Keep both installers and create a harmless record

Use a test device or a disposable build environment. You’ll need the exact
installed Tick & Bell installer and the candidate, both for Debian arm64.
The [Tick & Bell build instructions](case-studies/tick-bell.md) point to the
source. The versions in this example are **0.1.4-rev1 → 0.1.4-rev2**; use the
actual filenames and versions for your own test. No Store submission is needed.

Set the paths to the two files you have on the device:

```sh
old="$PWD/tick-bell_0.1.4_rev1_arm64.deb"
new="$PWD/tick-bell_0.1.4_rev2_arm64.deb"

dpkg-query -W -f='${Package} ${Version}\n' tick-bell
dpkg-deb -f "$old" Package Version Architecture
dpkg-deb -f "$new" Package Version Architecture
```

Both package names should be `tick-bell`, both architectures `arm64`, and
the old installer’s version should match the installed one. The candidate
must be newer by Debian’s version rules. Keep the existing launcher, executable
and state paths stable rather than renaming the app to work around an upgrade.

```sh
dpkg --compare-versions "$(dpkg-deb -f "$new" Version)" gt \
  "$(dpkg-query -W -f='${Version}' tick-bell)"
apt -s install "$new"
```

The version comparison succeeds silently. Read the simulation before proceeding.
For this example, expect only Tick & Bell to be upgraded. Stop if the plan
removes something, downgrades a package, or pulls in an unexpected dependency.

Open **Tick & Bell → Alarms**, create an alarm named **Example alarm** at
**7:30 AM**, and save it with **Enabled** set to **Off**. From 0.1.6 the form
has no Enabled row: save the alarm, then press Space on it in the list so its
row reads **Off**. A disabled alarm is
enough to test data preservation. Note the label, time and off state. If this is
a device you rely on, wait until there are no active timers, ringing or snoozed
alarms, or alarms due during the maintenance window. Closing the app does not
stop its scheduler.

## 2. Back up the state with the writer stopped

Close the app. Run the following as the logged-in device user, not with
`sudo`. This example uses the scheduler’s default state location. If you
configured a custom state directory for the service, use that directory.

```sh
umask 077
backup=$(mktemp -d "$HOME/tick-bell-upgrade.XXXXXX")
state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/tick-bell"

systemctl --user stop tick-bell.service
systemctl --user is-active tick-bell.service
```

Confirm it reports **inactive** before copying:

```sh
cp -p "$state_dir/state" "$backup/state.before" &&
cp -p "$old" "$backup/rollback.deb" &&
(
  cd "$backup" &&
  sha256sum state.before rollback.deb > SHA256SUMS &&
  sha256sum -c SHA256SUMS
)
```

If either file is missing or the backup fails, stop, restart the original
scheduler, and investigate before installing. Keep the backup private. For an
app with a database, use its documented consistent-backup method; copying a
live SQLite file by itself can miss committed changes in the write-ahead log.

## 3. Install, reopen, and prove the new build is running

After a clean dry run and verified backup, install the candidate. Review the
real package-manager prompt. Keep any local configuration you intend to retain.

```sh
sudo apt install "$new"
dpkg-query -W -f='${Version}\n' tick-bell
systemctl --user daemon-reload
systemctl --user start tick-bell.service
systemctl --user is-active tick-bell.service
```

The installed version should be **0.1.4-rev2**, and the user service should
report **active**. Check the actual process as well. A package upgrade can
replace a file on disk while a service keeps running the old executable.

```sh
pid=$(systemctl --user show -p MainPID --value tick-bell.service)
test "$pid" -gt 0 &&
  cmp -s "/proc/$pid/exe" /usr/bin/tick-bell-scheduler &&
  echo 'Running scheduler matches the installed binary'
```

Reopen Tick & Bell from **APPLaunch**. Go to **Alarms** and verify **Example
alarm**, **7:30 AM**, and **Off**. If the new build is installed but an old
process is still running or the alarm is wrong, stop and investigate. Avoid
using a second scheduler instance as a workaround.

## 4. Roll back without throwing away newer data

Close Tick & Bell and make sure no active or imminent alarms will be affected.
Stop the scheduler, then keep a separate copy of the current state. Do not
overwrite the earlier backup.

```sh
systemctl --user stop tick-bell.service
cp -p "$state_dir/state" "$backup/state.after"
(cd "$backup" && sha256sum -c SHA256SUMS)
apt -s install --allow-downgrades "$backup/rollback.deb"
```

If the simulation only downgrades Tick & Bell, repeat with
`sudo apt install --allow-downgrades "$backup/rollback.deb"`. Check the package
version, reload and start the scheduler, and repeat the process and alarm
checks. Expect **0.1.4-rev1** and the same saved alarm.

**Keep the current data when the old version can read it.** These two Tick & Bell
revisions use the same state format. For your app, check downgrade compatibility
before installing the old package. Restore `state.before` only if you actually
need that snapshot and accept losing changes made since it was taken. Stop the
writer before restoring and keep `state.after` for recovery.

Only for that recovery case, with the app closed and the scheduler confirmed
inactive, verify and replace the state file as the logged-in user:

```sh
(cd "$backup" && sha256sum -c SHA256SUMS) &&
  restored=$(mktemp "$state_dir/.restore.XXXXXX") &&
  cp -p "$backup/state.before" "$restored" &&
  mv -f "$restored" "$state_dir/state"
```

If any command fails, investigate before restarting. Otherwise start the
scheduler and repeat the alarm check.

## Verification and limits

The worked example was rehearsed in disposable Debian 13 arm64 with the two
actual packages and a disabled sample alarm. The upgrade and downgrade both
preserved the alarm and the original state bytes. The running executable was
checked after each installation, and a separate recovery test restored the
backup after a deliberate change to the fixture. The container ran the packaged
scheduler directly. It did not test APPLaunch, the physical keypad, audio, or
suspend behavior; check those separately on the intended device.

For a smaller, service-free version of the upgrade test, see
[First device app](first-device-app.md). If the app does not reopen, start with
[device app troubleshooting](device-app-troubleshooting.md).
