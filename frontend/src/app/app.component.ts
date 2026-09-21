import { Component, ViewChild } from '@angular/core';
import { ApiService } from './core/services/api.service';
import { AdaptationRequest, AdaptationResponse } from './core/models/adaptation.model';
import { DocumentUploaderComponent } from './components/document-uploader/document-uploader.component';

@Component({
  selector: 'app-root',
  template: `
    <div class="app-container">
      <header class="navbar">
        <div class="brand">
          <span class="logo">🎓</span>
          <span class="title">NuevaMente</span>
          <span class="badge">Oracle ONE G10</span>
        </div>
      </header>

      <main class="content">
        <app-document-uploader #uploader></app-document-uploader>
        <app-parameter-config (configChanged)="onAdaptRequested($event)"></app-parameter-config>

        <div *ngIf="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Procesando con Graph RAG, RAG Híbrido y Google Gemini...</p>
        </div>

        <div *ngIf="response" class="results-section">
          <app-metadata-dashboard
            [metadatos]="response.metadatos"
            [evaluacion]="response.evaluacion_calidad"
            [oci]="response.almacenamiento_oci"
          ></app-metadata-dashboard>

          <app-content-viewer [contenido]="response.contenido_adaptado"></app-content-viewer>

          <app-interactive-flashcards 
            *ngIf="response.contenido_adaptado.items"
            [items]="response.contenido_adaptado.items"
          ></app-interactive-flashcards>

          <app-interactive-quiz
            *ngIf="response.contenido_adaptado.quizzes"
            [quizzes]="response.contenido_adaptado.quizzes"
          ></app-interactive-quiz>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .app-container { font-family: system-ui, -apple-system, sans-serif; background: #f8fafc; min-height: 100vh; }
    .navbar { background: #0f172a; color: white; padding: 1rem 2rem; display: flex; align-items: center; }
    .brand { display: flex; align-items: center; gap: 0.75rem; }
    .logo { font-size: 1.5rem; }
    .title { font-size: 1.25rem; font-weight: bold; }
    .badge { background: #38bdf8; color: #0f172a; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700; }
    .content { max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
    .loading-state { text-align: center; padding: 3rem; background: white; border-radius: 12px; margin-top: 2rem; border: 1px solid #e2e8f0; }
    .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #2563eb; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  `]
})
export class AppComponent {
  @ViewChild('uploader') uploader!: DocumentUploaderComponent;
  loading: boolean = false;
  response?: AdaptationResponse;

  constructor(private apiService: ApiService) {}

  onAdaptRequested(params: any): void {
    const docData = this.uploader.getDocumentData();
    const payload: AdaptationRequest = {
      ...docData,
      ...params
    };

    this.loading = true;
    this.response = undefined;

    this.apiService.adaptContent(payload).subscribe({
      next: (res) => {
        this.response = res;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error al solicitar adaptación:', err);
        this.loading = false;
      }
    });
  }
}
