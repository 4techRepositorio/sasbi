import { Routes } from '@angular/router';

import { authGuard } from './core/auth.guard';
import { roleGuard } from './core/role.guard';

export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./pages/login/login.component').then((m) => m.LoginComponent) },
  {
    path: 'forgot-password',
    loadComponent: () =>
      import('./pages/forgot-password/forgot-password.component').then((m) => m.ForgotPasswordComponent),
  },
  {
    path: 'reset-password',
    loadComponent: () =>
      import('./pages/reset-password/reset-password.component').then((m) => m.ResetPasswordComponent),
  },
  {
    path: 'app',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/shell/shell.component').then((m) => m.ShellComponent),
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      {
        path: 'dashboard',
        data: { shellTitle: 'Dashboard' },
        loadComponent: () => import('./pages/dashboard/dashboard.component').then((m) => m.DashboardComponent),
      },
      {
        path: 'upload',
        canActivate: [roleGuard(['admin', 'analyst'])],
        data: { shellTitle: 'Upload' },
        loadComponent: () => import('./pages/upload/upload.component').then((m) => m.UploadComponent),
      },
      {
        path: 'datasets',
        data: { shellTitle: 'Catálogo' },
        loadComponent: () => import('./pages/datasets/datasets.component').then((m) => m.DatasetsComponent),
      },
      {
        path: 'ingestions',
        data: { shellTitle: 'Ingestões' },
        loadComponent: () => import('./pages/ingestions/ingestions.component').then((m) => m.IngestionsComponent),
      },
    ],
  },
  { path: '', pathMatch: 'full', redirectTo: 'app' },
  { path: '**', redirectTo: 'app' },
];
