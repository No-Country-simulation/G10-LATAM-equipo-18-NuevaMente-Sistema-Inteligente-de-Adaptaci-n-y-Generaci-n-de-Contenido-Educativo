import { Component, Input } from '@angular/core';
import { ContenidoAdaptado } from '../../core/models/adaptation.model';

@Component({
  selector: 'app-content-viewer',
  template: `
    <div class="viewer-card" *ngIf="contenido">
      <h2 class="main-title">{{ contenido.titulo }}</h2>
      <div class="intro-box">
        <p class="intro-text">{{ contenido.introduccion_contextualizada }}</p>
      </div>

      <div *ngIf="contenido.resumen_ejecutivo" class="section">
        <h3>📋 Resumen Ejecutivo</h3>
        <p>{{ contenido.resumen_ejecutivo }}</p>
      </div>

      <div *ngIf="contenido.secciones_tutorial" class="section">
        <div *ngFor="let sec of contenido.secciones_tutorial" class="tutorial-block">
          <h3>{{ sec.encabezado }}</h3>
          <p>{{ sec.contenido }}</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .viewer-card { background: #ffffff; padding: 2rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-top: 2rem; }
    .main-title { font-size: 1.5rem; font-weight: 800; color: #0f172a; margin-bottom: 1rem; }
    .intro-box { background: #f0f9ff; border-left: 4px solid #0284c7; padding: 1rem 1.25rem; border-radius: 6px; margin-bottom: 1.5rem; }
    .intro-text { font-size: 1.05rem; color: #0369a1; line-height: 1.6; font-style: italic; }
    .section { margin-top: 1.5rem; }
    .section h3 { font-size: 1.15rem; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem; }
    .tutorial-block { margin-bottom: 1.25rem; padding: 1rem; background: #f8fafc; border-radius: 8px; border: 1px solid #f1f5f9; }
  `]
})
export class ContentViewerComponent {
  @Input() contenido?: ContenidoAdaptado;
}
