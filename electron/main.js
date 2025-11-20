import { app, BrowserWindow } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';

// Fix __dirname for ES Module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function createWindow() {
    const win = new BrowserWindow({
        title: "Sofi AI",
        icon: path.join(__dirname, "icons/sofi.png"),
        width: 1200,
        height: 600,
        frame: true,            // No title bar
        transparent: false,       // Glass background
        resizable: false,
        alwaysOnTop: true,       // Floating orb
        hasShadow: false,
        roundedCorners: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
        }
    });

    win.loadURL('http://localhost:5173');
}

app.whenReady().then(createWindow);
