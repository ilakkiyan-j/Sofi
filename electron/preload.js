import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
    // Future: send/receive messages to Python backend
    sendMessage: (msg) => ipcRenderer.send('message', msg),
    resizeWindow: (width, height) => ipcRenderer.send('resize-window', { width, height })
});


