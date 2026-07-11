# Chrome Sync Mechanics — why naive edits get reverted

This is the single most important thing to understand before reorganizing a
synced user's bookmarks. Get it wrong and every change vanishes on next launch.

## 1. Sync is cloud-led, not file-led

When the user is signed in with Chrome Sync enabled, the **server copy is the
source of truth**. On launch Chrome:

1. Connects to the sync server.
2. Downloads the server's bookmark state (if local mirror is stale).
3. **Merges** local `Bookmarks` with the server copy (dedup by URL/ID).

So if you edit `Bookmarks` offline and reopen, Chrome pulls the old cloud set
and merges → old + new coexist. Real case: cleaned to 381 locally, relaunched,
ended with **923** (547 old + 381 new, deduped). The cleanup "didn't take".

## 2. Editing Preferences to disable Sync does NOT work

Naive attempt: quit Chrome, set in `Preferences`:
```
sync.requested = False
google.services.consented_to_sync = False
sync.data_type_status_for_sync_to_signin.bookmarks = False
```
Then clear `Sync Data/LevelDB` and relaunch.

**Why it fails:** Chrome re-validates and restores its own sync state on
startup. `sync.requested` only controls whether the setup wizard pops, not
whether sync is on. The real per-type switch
(`data_type_status_for_sync_to_signin.bookmarks`) gets recomputed from the
account's signed-in state. Result: old bookmarks merge back anyway.

## 3. What actually works

The only reliable file-based path is to ensure Sync is **genuinely off**, so
there is nothing on the server to merge from.

Verify with `python3 -c "import json;d=json.load(open('Preferences'));..."`:
```
google.services.consented_to_sync == false
sync.requested == false
sync.data_type_status_for_sync_to_signin.bookmarks == false
```
If ALL three are false, the local `Bookmarks` file is authoritative and a write
will stick.

Then the procedure:
1. **Close Chrome normally** (see §5 — do NOT pkill).
2. Back up `Bookmarks` → `Bookmarks.bak.<tag>`.
3. Write the clean `Bookmarks` JSON (use `scripts/reorganize_bookmarks.py`).
4. Clear `Sync Data/LevelDB` (the local mirror of cloud state) so no stale
   server snapshot reappears.
5. Reopen Chrome normally. The clean set persists because the server has nothing
   to merge.

## 4. Re-enabling Sync without the old bookmarks returning

The user may later want Sync back. If they just flip it on, the **server still
holds the old 547** and will merge them in again.

Correct sequence:
1. `chrome://settings/syncSetup` → **Clear & reset** (wipes the server copy).
2. Turn Sync back on (ensure "Bookmarks" is checked).
3. Wait ~30s. The clean local set pushes up and becomes the new server truth.

## 5. Never force-kill Chrome

`pkill -x "Google Chrome"` or `kill -9` skips normal shutdown, which
serializes session state. Consequences:
- **Tab Groups are destroyed.** They are local-only session state (not synced,
  no standalone on-disk file). Bookmarks survive (written to disk) but Tab
  Groups vanish.
- Recovery: impossible from disk (session file is proprietary binary, no
  saved-groups file). Only manual rebuild from the still-open tabs.

Always close via normal exit. If AppleScript is blocked by macOS TCC
(`tell app "Google Chrome" to quit` fails), ask the user to quit manually.

## 6. Extension-based approach also fails in a sandbox

Calling `chrome.bookmarks` from an unpacked extension is the "proper" API path,
but in a constrained/macOS-sandboxed environment it is unreachable:
- `--load-extension` flag is silently dropped (sandbox or when Chrome already
  running).
- `Playwright`/`remote-debugging-port` + AppleScript are blocked by macOS TCC.
- Manual `chrome://extensions` load fails because `/tmp` is hidden from the
  file picker (moving to Desktop still resulted in 0 installed extensions).

Conclusion: in such environments, go through the file directly using §3, not
an extension.
