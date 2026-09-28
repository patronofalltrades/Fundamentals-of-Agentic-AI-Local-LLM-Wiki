# Run the offline proof

Use the macOS Terminal app. Read this guide before you disconnect. Codex may lose its connection while the Mac is offline.

## 1. Prepare private inputs while online

From the project folder, run:

```sh
cd "/Users/haniframadhan/Documents/ChatGPT/Fundamentals of Agentic AI project"
python3 scripts/prepare-offline-inputs.py
```

- This copies three private test-input files to local storage under `/private/tmp`.
- It checks that the copies occupy local disk blocks.
- It prints no question text.
- The first offline attempt failed because one private file was not on local disk.
- Repeat this step after a Mac restart or after clearing temporary files.

## 2. Decide whether to record video

Video is optional. The script saves a terminal log. The assignment also needs Obsidian screenshots.

For a macOS screen recording:

1. Press **Shift–Command–5**.
2. Select **Record Entire Screen**.
3. Set **Options → Save to** a local folder, such as Desktop.
4. Start the recording before you disconnect.
5. Show the Wi-Fi state, Ollama restart, new Terminal window, and final status.
6. Stop the recording after the run.

- The microphone is optional. You can speak to explain the steps.
- Test screen recording before the offline run.
- Keep the full video private. It can show the exact questions or unrelated notes.
- Review every frame before you share a short clip.
- See [Apple's screen-recording guide](https://support.apple.com/en-nz/102618).

Cursorful Pro Desktop can also record the full screen. Test that it saves a playable file locally before the offline run. The browser extension may omit Terminal and Ollama.

## 3. Disconnect and restart

1. Confirm that Ollama and `gemma4:e2b-mlx` are installed.
2. Turn Wi-Fi off. Disconnect Ethernet, tethering, and VPN.
3. Quit and reopen Ollama while offline.
4. Open a new Terminal window.

## 4. Run the script

```sh
cd "/Users/haniframadhan/Documents/ChatGPT/Fundamentals of Agentic AI project"
bash scripts/offline-proof.sh
```

The script:

- Stops if Wi-Fi is on or an external HTTPS check succeeds.
- Saves the connectivity result.
- Unloads Gemma and runs `search`.
- Ingests all three originals in a temporary workspace.
- Leaves the reviewed wiki pages in this project unchanged.
- Runs 35 code tests, four `ask` cases, and chat checks.
- Saves output, model identity, timing, and memory snapshots.
- Uses only `127.0.0.1` for model calls.

The run can take several minutes. Keep the Mac awake.

## 5. Check the result

- The last line gives a folder under `evidence/offline/`.
- Open its `status.txt` file.
- If it says `completed`, inspect the cited answers and transcript.
- While still offline, save a screenshot of Wi-Fi state and the final Terminal result as `offline-terminal.png` in that folder.
- If it says `failed`, keep the folder and read the error in `terminal.txt`. Fix the cause and repeat the run.

The script's `offline_proof` flag is only one check. The Wi-Fi state, failed external connection, fresh Terminal process, model reload, and saved outputs support the offline claim.
