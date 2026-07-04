import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';

// Fix __dirname for ES Module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function createWindow() {
    const win = new BrowserWindow({
        title: "Sofi AI",
        icon: path.join(__dirname, "icons/sofi.png"),
        width: 900,
        height: 600,
        minWidth: 700,
        minHeight: 500,
        frame: true,
        transparent: false,
        resizable: true,         // User can drag-resize
        maximizable: true,       // Enable OS maximizing
        fullscreenable: true,    // Enable OS fullscreen
        alwaysOnTop: false,
        hasShadow: false,
        roundedCorners: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
        }
    });

    win.loadURL('http://localhost:5173');
}

app.whenReady().then(createWindow);


