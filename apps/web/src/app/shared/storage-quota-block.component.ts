import { Component, computed, input } from '@angular/core';

import { formatBytes } from '../core/format-bytes';
import {
  groupStoragePercent,
  isGroupStorageNearLimit,
  isTenantStorageNearPlanLimit,
  isUserStorageNearLimit,
  tenantStoragePercent,
  userStoragePercent,
} from '../core/storage-usage';
import type { StorageContext } from '../core/tenant-context';

export type StorageQuotaVariant = 'compact' | 'card' | 'dash';
export type StorageQuotaMetaStyle = 'short' | 'verbose';

/**
 * Bloco reutilizável: barra + texto de quotas de armazenamento (tenant / utilizador / grupo).
 * Estilos globais: `.da-storage`, `.da-storage--compact`, `.da-storage--card`, `.da-storage--dash`.
 */
@Component({
  selector: 'app-storage-quota-block',
  template: `
    <div
      class="da-storage"
      data-testid="storage-quota-block"
      [attr.data-storage-warn]="tenantNearLimit() ? 'true' : null"
      [attr.data-user-quota-warn]="userNearLimit() ? 'true' : null"
      [attr.data-group-quota-warn]="groupNearLimit() ? 'true' : null"
      [class.da-storage--compact]="variant() === 'compact'"
      [class.da-storage--card]="variant() === 'card' || variant() === 'dash'"
      [class.da-storage--dash]="variant() === 'dash'"
      [class.da-storage--tenant-warn]="tenantNearLimit()"
      aria-label="Utilização de armazenamento"
    >
      @if (showLabel()) {
        <div class="da-storage__label">Armazenamento (organização)</div>
      }
      <div
        class="da-storage__bar"
        role="progressbar"
        [attr.aria-valuenow]="roundPct()"
        aria-valuemin="0"
        aria-valuemax="100"
        [attr.aria-label]="ariaBarLabel()"
      >
        <span class="da-storage__fill" [style.width.%]="tenantStoragePercent(storage())"></span>
      </div>
      <div class="da-storage__meta">
        @if (metaStyle() === 'verbose') {
          {{ formatBytes(storage().tenant_used_bytes) }} utilizados · limite {{ storage().tenant_limit_mb }} MB
        } @else {
          {{ formatBytes(storage().tenant_used_bytes) }} · limite {{ storage().tenant_limit_mb }} MB
        }
      </div>
      @if (tenantNearLimit()) {
        <p class="da-storage__warn-hint" role="status">Próximo do limite de armazenamento do plano.</p>
      }
      @if (userStoragePercent(storage()) !== null) {
        <div class="da-storage__sub-stack" [class.da-storage__sub-stack--warn]="userNearLimit()">
          <div class="da-storage__sub-title">O seu perfil</div>
          <div
            class="da-storage__sub-bar"
            role="progressbar"
            [attr.aria-valuenow]="roundUserBarPct()"
            aria-valuemin="0"
            aria-valuemax="100"
            [attr.aria-label]="userBarAria()"
          >
            <span
              class="da-storage__sub-fill"
              [class.da-storage__sub-fill--warn]="userNearLimit()"
              [style.width.%]="userBarWidth()"
            ></span>
          </div>
          <div class="da-storage__sub" [class.da-storage__sub--warn]="userNearLimit()">
            {{ formatBytes(storage().user_used_bytes) }} · limite {{ storage().user_limit_mb }} MB
            @if (userNearLimit()) {
              <span class="da-storage__inline-warn"> — próximo do limite.</span>
            }
          </div>
        </div>
      }
      @if (storage().group_name && groupStoragePercent(storage()) !== null) {
        <div class="da-storage__sub-stack" [class.da-storage__sub-stack--warn]="groupNearLimit()">
          <div class="da-storage__sub-title">{{ storage().group_name }}</div>
          <div
            class="da-storage__sub-bar"
            role="progressbar"
            [attr.aria-valuenow]="roundGroupBarPct()"
            aria-valuemin="0"
            aria-valuemax="100"
            [attr.aria-label]="groupBarAria()"
          >
            <span
              class="da-storage__sub-fill"
              [class.da-storage__sub-fill--warn]="groupNearLimit()"
              [style.width.%]="groupBarWidth()"
            ></span>
          </div>
          <div class="da-storage__sub" [class.da-storage__sub--warn]="groupNearLimit()">
            {{ formatBytes(storage().group_used_bytes ?? 0) }} · limite {{ storage().group_limit_mb }} MB
            @if (groupNearLimit()) {
              <span class="da-storage__inline-warn"> — próximo do limite.</span>
            }
          </div>
        </div>
      }
    </div>
  `,
})
export class StorageQuotaBlockComponent {
  readonly storage = input.required<StorageContext>();
  readonly variant = input<StorageQuotaVariant>('card');
  readonly metaStyle = input<StorageQuotaMetaStyle>('verbose');
  readonly showLabel = input(true);

  readonly formatBytes = formatBytes;
  readonly tenantStoragePercent = tenantStoragePercent;
  readonly userStoragePercent = userStoragePercent;
  readonly groupStoragePercent = groupStoragePercent;

  readonly roundPct = computed(() => Math.round(tenantStoragePercent(this.storage())));

  readonly tenantNearLimit = computed(() => isTenantStorageNearPlanLimit(this.storage()));

  readonly userNearLimit = computed(() => isUserStorageNearLimit(this.storage()));

  readonly groupNearLimit = computed(() => isGroupStorageNearLimit(this.storage()));

  readonly userBarWidth = computed(() => userStoragePercent(this.storage()) ?? 0);

  readonly groupBarWidth = computed(() => groupStoragePercent(this.storage()) ?? 0);

  readonly roundUserBarPct = computed(() => Math.round(this.userBarWidth()));

  readonly roundGroupBarPct = computed(() => Math.round(this.groupBarWidth()));

  readonly userBarAria = computed(() => {
    const st = this.storage();
    return `Armazenamento do seu perfil: ${formatBytes(st.user_used_bytes)} de ${st.user_limit_mb} MB`;
  });

  readonly groupBarAria = computed(() => {
    const st = this.storage();
    const name = st.group_name ?? 'Grupo';
    return `${name}: ${formatBytes(st.group_used_bytes ?? 0)} de ${st.group_limit_mb} MB`;
  });

  readonly ariaBarLabel = computed(() => {
    const st = this.storage();
    let s = `Espaço da organização: ${formatBytes(st.tenant_used_bytes)} de ${st.tenant_limit_mb} MB`;
    if (isTenantStorageNearPlanLimit(st)) {
      s += ' — próximo do limite do plano';
    }
    return s;
  });
}
