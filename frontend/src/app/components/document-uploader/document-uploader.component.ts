import { Component, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-document-uploader',
  template: `
    <div class="uploader-card">
      <h3 class="title">📥 Carga de Documentación Técnica</h3>
      <div class="input-group">
        <label>Título del Documento:</label>
        <input 
          type="text" 
          [(ngModel)]="documentoTitulo" 
          placeholder="Ej: Introducción a la Arquitectura de Redes VCN en OCI" 
          class="text-input"
        />
      </div>

      <div class="input-group">
        <label>Contenido Técnico (PDF / Markdown / Texto):</label>
        <textarea 
          [(ngModel)]="documentoContenido" 
          rows="6" 
          placeholder="Pega aquí la documentación técnica, manual o paper científico..."
          class="textarea-input"
        ></textarea>
      </div>
    </div>
  `,
  styles: [`
    .uploader-card { background: #ffffff; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem; }
    .title { font-size: 1.15rem; font-weight: 700; color: #1e293b; margin-bottom: 1rem; }
    .input-group { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1rem; }
    label { font-size: 0.85rem; font-weight: 600; color: #475569; }
    .text-input, .textarea-input { padding: 0.75rem; border-radius: 6px; border: 1px solid #cbd5e1; font-size: 0.95rem; font-family: inherit; }
    .textarea-input { resize: vertical; }
  `]
})
export class DocumentUploaderComponent {
  documentoTitulo: string = 'Introduccion a la Arquitectura de Redes VCN en OCI';
  documentoContenido: string = 'La Virtual Cloud Network (VCN) es una red privada y personalizable configurada en Oracle Cloud Infrastructure. Similar a una red de centro de datos tradicional, la VCN ofrece control total sobre su entorno de red, incluyendo subredes publicas y privadas, tablas de enrutamiento, Internet Gateways, NAT Gateways y Security Lists para control de trafico mediante reglas de entrada (ingress) y salida (egress).';

  @Output() documentLoaded = new EventEmitter<any>();

  getDocumentData() {
    return {
      documento_titulo: this.documentoTitulo,
      documento_contenido: this.documentoContenido
    };
  }
}
