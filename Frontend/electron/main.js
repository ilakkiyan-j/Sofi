import { app, BrowserWindow } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';
import fs from 'fs';

// Fix __dirname for ES Module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let backendProcess = null;

function createWindow() {
    // Resolve path of packaged backend in Electron resources folder
    const backendPath = app.isPackaged
        ? path.join(process.resourcesPath, 'backend', 'backend.exe')
        : null;

    if (app.isPackaged && backendPath) {
        const logPath = path.join(app.getPath('userData'), 'backend_log.txt');
        const logStream = fs.createWriteStream(logPath, { flags: 'a' });
        logStream.write(`\n=== Started at ${new Date().toISOString()} ===\n`);
        logStream.write(`Executable: ${backendPath}\n`);

        backendProcess = spawn(backendPath, [], {
            cwd: path.dirname(backendPath),
            detached: false
        });

        backendProcess.stdout.on('data', (data) => {
            logStream.write(`[STDOUT] ${data}`);
        });

        backendProcess.stderr.on('data', (data) => {
            logStream.write(`[STDERR] ${data}`);
        });
    }

    const win = new BrowserWindow({
        title: "Sofi AI",
        icon: path.join(__dirname, "assets/sofi.ico"),
        width: 900,
        height: 600,
        minWidth: 700,
        minHeight: 500,
        frame: true,            
        transparent: false,       
        resizable: true,         // User can drag-resize
        maximizable: true,       // Enable OS maximizing
        fullscreenable: true,    // Enable OS fullscreen
        alwaysOnTop: false,      // Disabled so OS maximize button is active
        hasShadow: false,
        roundedCorners: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
        }
    });

    if (app.isPackaged) {
        win.loadFile(path.join(__dirname, '../dist/index.html'));
    } else {
        win.loadURL('http://localhost:5173');
    }
}

app.whenReady().then(createWindow);

// Kill the backend process cleanly on exit
app.on('will-quit', () => {
    if (backendProcess) {
        console.log("Killing backend process...");
        backendProcess.kill();
    }
});


