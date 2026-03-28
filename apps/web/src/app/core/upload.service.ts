import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_V1 } from './api-base';

/** Resposta de POST /api/v1/uploads após armazenamento (TICKET-006). */
export interface UploadResult {
  id: string;
  status: string;
  original_filename: string;
  size_bytes: number;
}

@Injectable({ providedIn: 'root' })
export class UploadService {
  private readonly http = inject(HttpClient);

  uploadFile(file: File): Observable<UploadResult> {
    const fd = new FormData();
    fd.append('file', file, file.name);
    return this.http.post<UploadResult>(`${API_V1}/uploads`, fd);
  }
}
