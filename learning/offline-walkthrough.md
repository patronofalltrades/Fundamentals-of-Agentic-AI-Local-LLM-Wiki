# Step 12 — Run and record the offline proof

Read this guide before you disconnect. Use the macOS Terminal app for the test. Codex may lose its connection while the Mac is offline.

While still online, run the following command once from the project folder. It copies the three private test inputs to local-only storage under `/private/tmp`, checks that each copy occupies local disk blocks, and prints no question text. The first offline attempt stopped when macOS could not read a cloud-backed private file after disconnection. If you restart the whole Mac or clear temporary files, repeat this preparation before going offline.

```sh
cd "/Users/haniframadhan/Documents/ChatGPT/Fundamentals of Agentic AI project"
python3 scripts/prepare-offline-inputs.py
```

## Optional one-take video

Before disconnecting, press **Shift–Command–5**, choose **Record Entire Screen**, and set **Options → Save to** a local folder such as Desktop. The microphone is optional: if you turn it on, you can speak over the recording and briefly say what each command demonstrates. Silence is fine; the saved terminal log is the main proof. Start recording, then show Wi-Fi being turned off, Ollama being quit and reopened, the new Terminal window, and the full script run. Show the final `status.txt` result and stop the recording. Keep the original recording private at its local location. Review every frame before making any short version public; terminal questions can appear in a full-screen recording. Test screen recording permissions before the offline session. See [Apple's screen-recording instructions](https://support.apple.com/en-nz/102618) for the controls.

You can use **Cursorful Pro Desktop** instead if you have it. Select full-screen recording so Terminal and Ollama are visible. The Cursorful browser extension focuses on the browser and may crop the other apps. Before disconnecting, make a short test recording and confirm that Cursorful saves and exports a playable file locally; test microphone audio too if you want narration. Keep any recording that shows your private question text out of the public repository.

The video is optional. Still take the screenshots required for the assignment; the terminal log and saved run records are easier to inspect than video frames.

1. Keep the assignment folder on this Mac. Confirm that Ollama and `gemma4:e2b-mlx` are installed. Open Ollama.
2. Turn Wi-Fi off. Unplug Ethernet and disconnect any phone tethering or VPN. Quit and reopen Ollama while still offline. Open a new Terminal window.
3. In Terminal, run:

```sh
cd "/Users/haniframadhan/Documents/ChatGPT/Fundamentals of Agentic AI project"
bash scripts/offline-proof.sh
```

The script stops if Wi-Fi is on or if it can reach an external HTTPS site. It records the connectivity check. It then unloads Gemma and runs `search` without a loaded model. Next, it ingests all three originals in a temporary workspace. The reviewed wiki pages in this project are not replaced. It runs the code tests, four `ask` questions, and two chat sessions. It records the terminal output, model identity, timing, and memory snapshots. The Ollama client uses only `127.0.0.1` for model calls.

The run can take several minutes. Keep the Mac awake. The last line prints a folder under `evidence/offline/`. Check its `status.txt` file. A completed run still needs a human review of the cited answers and the saved transcript.

While still offline, take a screenshot that shows the Wi-Fi state and the completed Terminal result. Save it in the printed run folder as `offline-terminal.png`. Then reconnect and send me the run folder name. If the status is `failed`, keep the folder and send me the error from `terminal.txt`; we will fix the cause and repeat the offline run.

The script's `offline_proof` flag marks the runs made after its connectivity check. The flag alone does not prove disconnection. The Wi-Fi state, failed external connection, new Terminal process, model reload, and saved outputs are the supporting evidence.
