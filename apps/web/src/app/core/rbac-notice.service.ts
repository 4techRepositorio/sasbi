import { Injectable, signal } from '@angular/core';

/** Aviso quando o roleGuard bloqueia uma rota (substitui query param frágil no URL). */
@Injectable({ providedIn: 'root' })
export class RbacNoticeService {
  readonly message = signal<string | null>(null);

  showAccessDenied(): void {
    this.message.set(
      'Não tem permissão para aceder a essa área. O seu papel neste tenant não inclui essa ação.',
    );
  }

  clear(): void {
    this.message.set(null);
  }
}
