import { Component } from '@angular/core';

@Component({
  selector: 'app-settings-placeholder',
  template: `
    <div class="da-card">
      <h1 class="da-card__title">Configurações</h1>
      <p class="da-card__sub">
        Área prevista no PDF <strong>Data Analytics Solution</strong> — preferências da organização e integrações
        chegam numa iteração seguinte.
      </p>
      <p class="da-muted">
        Por agora utilize <strong>Equipa</strong>, <strong>Auditoria</strong> e <strong>Cobrança</strong> no menu
        lateral.
      </p>
    </div>
  `,
})
export class SettingsPlaceholderComponent {}
