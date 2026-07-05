# Sofi AI Assistant - Function Test Prompts

This document provides a comprehensive test suite of chat messages to verify all functions, registered tools, memory rules, and conversational traits of Sofi.

---

## 1. Conversational Chat & Personality (No Tools)
These prompts test whether Sofi responds naturally using her persona (sassy, warm, playful) without calling any tools.

| Prompt / Test Message | Expected Behavior |
| :--- | :--- |
| `Hello Sofi!` or `Hey there!` | Responds warmly/sassy without invoking tools. |
| `Who are you?` | Describes herself as Sofi, Ilakkiyan's personal AI assistant. |
| `What can you do?` | Summarizes her abilities (file management, searching, PC controls) in a sassy/playful tone. |
| `Who is your developer?` or `Who created you?` | Acknowledges she was created/developed for/by Ilakkiyan. |

---

## 2. PC & Device Controls (Device Automation)
These prompts test hardware integration, system metrics, and utility controls.

> [!WARNING]
> Testing **Lock System**, **Shutdown**, and **Restart** will affect your physical machine immediately. Use with caution.

| Functionality | Prompt / Test Message | Expected Tool Called |
| :--- | :--- | :--- |
| **System Info** | `What is my CPU and RAM usage right now?` or `Check my PC status.` | `get_system_info` |
| **Disk Space** | `How much hard drive space do I have left?` or `Show my disk space.` | `get_disk_space` |
| **Volume level** | `Set volume to 45 percent` or `Turn the volume down to 20` | `set_volume(level=45)` |
| **Mute Volume** | `Mute the sound` or `Turn off the audio` | `mute_volume` |
| **Brightness** | `Dim my screen to 30` or `Make the screen brighter (set it to 85)` | `set_brightness(level=30)` |
| **WiFi Control** | `Turn off my WiFi connection` | `wifi_off` |
| **WiFi Control** | `Turn on the WiFi` | `wifi_on` |
| **Bluetooth** | `Disable bluetooth` | `bluetooth_off` |
| **Bluetooth** | `Enable bluetooth` | `bluetooth_on` |
| **Recycle Bin** | `Empty the recycle bin for me` | `empty_recycle_bin` |
| **Screenshot** | `Take a screenshot of my screen` | `take_screenshot` |
| **Set Clipboard** | `Copy the text "Sofi is the best assistant ever" to my clipboard` | `set_clipboard(text="...")` |
| **Get Clipboard** | `What is currently copied in my clipboard?` | `get_clipboard` |
| **Lock System** | `Lock my PC right now` *(Will lock Windows)* | `lock_system` |
| **Restart PC** | `Restart my computer` *(Will reboot PC immediately)* | `restart` |
| **Shutdown PC** | `Shut down my computer` *(Will power off PC immediately)* | `shutdown` |

---

## 3. App Controls (Launching & Closing)
These prompts test Sofi's ability to fuzzy-match start menu links or store apps and close active tasks.

| Functionality | Prompt / Test Message | Expected Tool Called |
| :--- | :--- | :--- |
| **Launch App** | `Open Google Chrome` or `Start WhatsApp` | `launch_app(app_name="Google Chrome")` |
| **Launch App** | `Launch notepad` or `Start Spotify` | `launch_app(app_name="notepad")` |
| **Close App** | `Close notepad` or `Kill the chrome process` | `close_app(app_name="notepad")` |

---

## 4. File Management & Explorer
These prompts test file manipulations within Sofi's safe folder and opening directories.

> [!IMPORTANT]
> The `delete_file` command requires confirmation by design. Verify that Sofi asks you to confirm before she unlinks a file.

| Functionality | Prompt / Test Message | Expected Tool Called |
| :--- | :--- | :--- |
| **Create File** | `Create a file named test_log.txt` | `create_file(filename="test_log.txt")` |
| **Write File** | `Write "Sofi test pass!" into test_log.txt` | `write_file(filename="test_log.txt", content="...")` |
| **Append File** | `Append "Adding another log line." to test_log.txt` | `append_file(filename="test_log.txt", content="...")` |
| **Read File** | `Read the file test_log.txt` | `read_file(filename="test_log.txt")` |
| **List Files** | `List all files in my folder` | `list_files` |
| **Delete File** | `Delete test_log.txt` | Prompt confirmation $\rightarrow$ `delete_file` |
| **Open Folder** | `Open my downloads folder` | `open_path(path="downloads")` |
| **Open Folder** | `Open documents` or `Open my pictures folder` | `open_path(path="documents")` |

---

## 5. Web Search
These prompts test DuckDuckGo searches for current information.

| Functionality | Prompt / Test Message | Expected Tool Called |
| :--- | :--- | :--- |
| **Latest News** | `What is the latest news about Messi today?` | `search_web(query="Messi latest news")` |
| **Price / Shopping** | `How much is the iPhone 16 Pro Max?` | `search_web(query="iPhone 16 Pro Max price review buy")` |
| **Tutorial / Guide** | `How do I install Node.js step by step?` | `search_web(query="how to install Node.js step by step")` |
| **Code / Stack** | `Python code example for quicksort` | `search_web(query="Python code example for quicksort stackoverflow example github")` |
| **Videos** | `Watch a tutorial on building React apps on YouTube` | `search_web(query="React app tutorial site:youtube.com")` |

---

## 6. Context, Memory, & Continuation
These prompts test Sofi's ability to maintain state across messages, remember info from the context, and execute repetitions.

| Step | Prompt / Test Message | Expected Behavior |
| :--- | :--- | :--- |
| **1 (Remember)** | `My favorite color is green and I live in Chennai.` | Sofi remembers this (saved to context/memory). |
| **2 (Recall)** | `Where do I live and what color do I like?` | Recalls Chennai and green from context memory. |
| **3 (Action)** | `Take a screenshot.` | Executes `take_screenshot`. |
| **4 (Repeat)** | `Do it again.` or `Once more.` | Executes `take_screenshot` again (repeats last action). |
| **5 (Pronoun)** | `Open notepad.` then `Close it.` | Launch Notepad, then close it (resolving "it" to "notepad"). |
