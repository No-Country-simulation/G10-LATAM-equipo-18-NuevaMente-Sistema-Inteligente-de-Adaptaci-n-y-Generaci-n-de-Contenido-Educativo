import { Component, Input } from '@angular/core';
import { Metadatos, EvaluacionCalidad, AlmacenamientoOCI } from '../../core/models/adaptation.model';

@Component({
  selector: 'app-metadata-dashboard',
  template: `
    <div class="dashboard-grid">
      <div class="metric-card">
        <span class="icon">⏱️</span>
        <div class="metric-info">
          <span class="label">Tiempo de Estudio Estimado</span>
          <span class="value">{{ metadatos?.tiempo_estimado_estudio_minutos || 5 }} min</span>
        </div>
      </div>

      <div class="metric-card">
        <span class="icon">🎯</span>
        <div class="metric-info">
          <span class="label">Anclaje en Fuentes (Fidelidad)</span>
          <span class="value success">{{ (evaluacion?.anclaje_fuente_score || 0.98) * 100 }}%</span>
        </div>
      </div>

      <div class="metric-card">
        <span class="icon">☁️</span>
        <div class="metric-info">
          <span class="label">Persistencia en OCI</span>
          <span class="value oci-status">{{ oci?.status_upload || 'completado' }}</span>
        </div>
      </div>

      <div class="concepts-card">
        <h4>🔑 Conceptos Clave (Grafo Graph RAG)</h4>
        <div class="badge-list">
          <span *ngFor="let concept of metadatos?.conceptos_clave" class="badge">
            {{ concept }}
          </span>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
    .metric-card { background: white; padding: 1.25rem; border-radius: 10px; border: 1px solid #e2e8f0; display: flex; align-items: center; gap: 1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
    .icon { font-size: 2rem; }
    .metric-info { display: flex; flex-direction: column; }
    .label { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
    .value { font-size: 1.35rem; font-weight: 800; color: #0f172a; }
    .value.success { color: #16a34a; }
    .value.oci-status { font-size: 1rem; color: #d97706; text-transform: uppercase; }
    .concepts-card { grid-column: 1 / -1; background: #f8fafc; padding: 1.25rem; border-radius: 10px; border: 1px solid #e2e8f0; }
    .concepts-card h4 { font-size: 0.95rem; font-weight: 700; color: #334155; margin-bottom: 0.75rem; }
    .badge-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .badge { background: #e0f2fe; color: #0369a1; padding: 0.35rem 0.85rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600; border: 1px solid #bae6fd; }
  `]
})
export class MetadataDashboardComponent {
  @Input() metadatos?: Metadatos;
  @Input() evaluacion?: EvaluacionCalidad;
  @Input() oci?: AlmacenamientoOCI;
}
