const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('fourproDesktop', {
  login: (email, password) => ipcRenderer.invoke('auth:login', email, password),
  publishDataset: (payload) => ipcRenderer.invoke('desktop:publish-dataset', payload),
  publishDashboard: (payload) => ipcRenderer.invoke('desktop:publish-dashboard', payload),
});
