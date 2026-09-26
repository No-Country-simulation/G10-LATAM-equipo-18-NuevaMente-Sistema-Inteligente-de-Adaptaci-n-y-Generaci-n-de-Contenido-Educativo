import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { ApiService } from '../../core/services/api.service';
import { AdaptationRequest, AdaptationResponse } from '../../core/models/adaptation.model';

@Component({
  selector: 'app-stepper-creation',
  template: `
    <div class="stepper-wrapper">
      <!-- Breadcrumb Nav -->
      <div class="breadcrumb" *ngIf="currentStep === 2">
        <span class="crumb-link" (click)="goToStep(1)">Nuevo contenido</span>
        <span class="crumb-sep">›</span>
        <span class="crumb-active">Personalización</span>
      </div>

      <!-- Stepper Header (4 steps) -->
      <div class="stepper-header">
        <div class="step-item" [ngClass]="{'active': currentStep === 1, 'completed': currentStep > 1}" (click)="goToStep(1)">
          <div class="step-number">{{ currentStep > 1 ? '✓' : '1' }}</div>
          <span class="step-label">Documento</span>
        </div>
        <div class="step-line" [ngClass]="{'active': currentStep >= 2}"></div>

        <div class="step-item" [ngClass]="{'active': currentStep === 2, 'completed': currentStep > 2}" (click)="goToStep(2)">
          <div class="step-number">{{ currentStep > 2 ? '✓' : '2' }}</div>
          <span class="step-label">Personalización</span>
        </div>
        <div class="step-line" [ngClass]="{'active': currentStep >= 3}"></div>

        <div class="step-item" [ngClass]="{'active': currentStep === 3, 'completed': currentStep > 3}">
          <div class="step-number">{{ currentStep > 3 ? '✓' : '3' }}</div>
          <span class="step-label">Generación</span>
        </div>
        <div class="step-line" [ngClass]="{'active': currentStep >= 4}"></div>

        <div class="step-item" [ngClass]="{'active': currentStep === 4, 'completed': currentStep === 4}">
          <div class="step-number">4</div>
          <span class="step-label">Resultado</span>
        </div>
      </div>

      <!-- STEP 1: DOCUMENT UPLOADER -->
      <div *ngIf="currentStep === 1" class="step-content">
        <div class="step-heading">
          <div class="step-tag">NUEVO CONTENIDO</div>
          <h1 class="step-title">Crear nuevo contenido</h1>
          <p class="step-subtitle">Sube tu documento y define cómo quieres que se adapte.</p>
        </div>

        <div class="upload-card">
          <!-- Dropzone -->
          <div 
            class="dropzone"
            [ngClass]="{'dragover': isDragging}"
            (dragover)="onDragOver($event)"
            (dragleave)="onDragLeave($event)"
            (drop)="onDrop($event)"
            (click)="fileInput.click()"
          >
            <div class="upload-icon-circle">
              <span class="upload-icon">☁️</span>
            </div>
            <div class="dropzone-text">
              <h3>Arrastra tu documento aquí o haz clic para seleccionar</h3>
              <p>Formatos soportados: PDF, Markdown, TXT</p>
            </div>
            <input 
              #fileInput 
              type="file" 
              class="file-input-hidden" 
              accept=".pdf,.md,.markdown,.txt" 
              (change)="onFileSelected($event)" 
            />
          </div>

          <!-- File Selected Display -->
          <div *ngIf="selectedFile" class="file-item-badge">
            <div class="file-icon-box">📄</div>
            <div class="file-details">
              <div class="file-name">{{ selectedFile.name }}</div>
              <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
            </div>
            <button class="btn-remove-file" (click)="clearFile($event)">✕</button>
          </div>

          <!-- Requirements Box -->
          <div class="requirements-box">
            <h4>Requisitos del archivo</h4>
            <ul>
              <li><span class="check">✓</span> Máx. 50 MB</li>
              <li><span class="check">✓</span> Texto legible</li>
              <li><span class="check">✓</span> PDF, MD o TXT</li>
            </ul>
          </div>
        </div>

        <!-- Document Details Form -->
        <div class="doc-details-card">
          <div class="form-group">
            <label>Título del Documento</label>
            <input type="text" class="form-control" [(ngModel)]="documentTitle" placeholder="Ej. Introducción a OCI.pdf" />
          </div>

          <div class="form-group">
            <label>Contenido del Documento (Extraído / Textual)</label>
            <textarea class="form-control textarea-content" [(ngModel)]="documentContent" rows="5" placeholder="Pega el contenido o el texto extraído aquí..."></textarea>
          </div>
        </div>

        <div class="step-actions right-align">
          <button class="btn btn-primary btn-lg" (click)="goToStep(2)">
            Continuar ➔
          </button>
        </div>
      </div>

      <!-- STEP 2: PERSONALIZACIÓN -->
      <div *ngIf="currentStep === 2" class="step-content">
        <div class="step-heading">
          <div class="step-tag">CREAR</div>
          <h1 class="step-title">Personalización del contenido</h1>
          <p class="step-subtitle">Configura cómo deseas adaptar el material.</p>
        </div>

        <div class="personalization-grid">
          <!-- Form Panel (Left) -->
          <div class="form-panel">
            <h3 class="panel-header">Configura los detalles del contenido</h3>
            <p class="panel-sub">Estos ajustes nos permiten adaptar el material a tus necesidades y a tu audiencia.</p>

            <div class="form-group">
              <label>Perfil del destinatario</label>
              <select class="form-control" [(ngModel)]="perfilDestinatario">
                <option value="Principiante">Principiante / Transición de Carrera</option>
                <option value="Desarrollador Junior / Semi Senior">Desarrollador Junior / Semi Senior</option>
                <option value="Líder Técnico / Arquitecto">Líder Técnico / Arquitecto</option>
                <option value="Gestor / Ejecutivo (No Técnico)">Gestor / Ejecutivo (No Técnico)</option>
              </select>
              <span class="form-subtext">¿A quién va dirigido este contenido?</span>
            </div>

            <div class="form-group">
              <label>Formato pedagógico de salida</label>
              <select class="form-control" [(ngModel)]="formatoSalida">
                <option value="Guía Práctica Paso a Paso (Tutorial)">Guía Práctica Paso a Paso (Tutorial)</option>
                <option value="Flashcards de Memorización">Flashcards de Memorización</option>
                <option value="Quiz Interactivo con Justificaciones">Quiz Interactivo con Justificaciones</option>
                <option value="Resumen Ejecutivo (TL;DR)">Resumen Ejecutivo (TL;DR)</option>
              </select>
              <span class="form-subtext">¿En qué formato prefieres recibir el contenido?</span>
            </div>

            <div class="form-group">
              <label>Nicho / Contexto de aplicación</label>
              <select class="form-control" [(ngModel)]="nichoSector">
                <option value="General">General</option>
                <option value="Fintech & Servicios Financieros">Fintech & Servicios Financieros</option>
                <option value="Salud & Biotecnología">Salud & Biotecnología</option>
                <option value="E-commerce & Retail">E-commerce & Retail</option>
                <option value="Infraestructura en la Nube">Infraestructura en la Nube</option>
              </select>
              <span class="form-subtext">¿En qué contexto se aplicará este conocimiento?</span>
            </div>

            <div class="form-group">
              <label>Nivel de profundidad</label>
              <select class="form-control" [(ngModel)]="nivelDetalle">
                <option value="Didáctico">Didáctico</option>
                <option value="Técnico">Técnico</option>
                <option value="Ejecutivo">Ejecutivo</option>
              </select>
              <span class="form-subtext">¿Qué tan profundo debe ser el contenido?</span>
            </div>

            <div class="form-group">
              <label>{{ cantidadLabel }}</label>
              <input type="number" class="form-control" [(ngModel)]="cantidadGenerar" min="1" max="20" placeholder="Ej. 5" />
              <span class="form-subtext">Cantidad exacta de elementos o páginas a generar en la salida.</span>
            </div>

            <div class="form-group">
              <label>Instrucciones adicionales (opcional)</label>
              <textarea class="form-control" [(ngModel)]="instruccionesAdicionales" rows="3" placeholder="Ej. Incluir ejemplos prácticos, analogías, casos reales..."></textarea>
              <span class="form-subtext">Cuéntanos si tienes algún enfoque específico, ejemplos o estilo preferido.</span>
            </div>

            <div class="step-actions split">
              <button class="btn btn-secondary" (click)="goToStep(1)">Volver</button>
              <button class="btn btn-primary" (click)="startGeneration()">Generar contenido</button>
            </div>
          </div>

          <!-- Summary Side Panel (Right) -->
          <div class="summary-panel">
            <h3 class="summary-title">Resumen de configuración</h3>
            <p class="summary-sub">Así se generará tu contenido.</p>

            <div class="summary-list">
              <div class="summary-item">
                <span class="item-icon">👤</span>
                <div>
                  <div class="item-label">Perfil del destinatario</div>
                  <div class="item-value">{{ perfilDestinatario }}</div>
                </div>
              </div>

              <div class="summary-item">
                <span class="item-icon">📄</span>
                <div>
                  <div class="item-label">Formato pedagógico de salida</div>
                  <div class="item-value">{{ formatoSalida }}</div>
                </div>
              </div>

              <div class="summary-item">
                <span class="item-icon">🎯</span>
                <div>
                  <div class="item-label">Nicho / Contexto de aplicación</div>
                  <div class="item-value">{{ nichoSector }}</div>
                </div>
              </div>

              <div class="summary-item">
                <span class="item-icon">📊</span>
                <div>
                  <div class="item-label">Nivel de profundidad</div>
                  <div class="item-value">{{ nivelDetalle }}</div>
                </div>
              </div>

              <div class="summary-item">
                <span class="item-icon">🔢</span>
                <div>
                  <div class="item-label">Cantidad a generar</div>
                  <div class="item-value">{{ cantidadGenerar }} elementos</div>
                </div>
              </div>
            </div>

            <div class="info-alert-box">
              <span class="info-icon">📍</span>
              <span>Puedes revisar y ajustar estos parámetros antes de generar el contenido.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- STEP 3: GENERACIÓN EN CURSO -->
      <div *ngIf="currentStep === 3" class="step-content">
        <app-pipeline-progress 
          [progressPercentage]="progressVal" 
          [currentStage]="pipelineStage"
        ></app-pipeline-progress>
      </div>

      <!-- STEP 4: RESULTADO / VISOR -->
      <div *ngIf="currentStep === 4" class="step-content">
        <app-content-viewer 
          [contenido]="response?.contenido_adaptado"
          [metadatos]="response?.metadatos"
          [evaluacion]="response?.evaluacion_calidad"
          [oci]="response?.almacenamiento_oci"
          (backRequested)="goToStep(1)"
        ></app-content-viewer>
      </div>
    </div>
  `,
  styles: [`
    .stepper-wrapper {
      max-width: 1100px;
      margin: 0 auto;
    }

    .breadcrumb {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.85rem;
      margin-bottom: 1.5rem;
    }
    .crumb-link {
      color: #64748b;
      cursor: pointer;
    }
    .crumb-link:hover { color: #3b82f6; }
    .crumb-sep { color: #cbd5e1; }
    .crumb-active { color: #0f172a; font-weight: 700; }

    .stepper-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 2.5rem;
    }
    .step-item {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      cursor: pointer;
    }
    .step-number {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #ffffff;
      border: 2px solid #cbd5e1;
      color: #64748b;
      font-weight: 700;
      font-size: 0.85rem;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .step-item.active .step-number {
      background: #3b82f6;
      border-color: #3b82f6;
      color: #ffffff;
      box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
    }
    .step-item.completed .step-number {
      background: #3b82f6;
      border-color: #3b82f6;
      color: #ffffff;
    }
    .step-label {
      font-size: 0.88rem;
      font-weight: 600;
      color: #64748b;
    }
    .step-item.active .step-label {
      color: #0f172a;
      font-weight: 700;
    }
    .step-line {
      flex: 1;
      height: 2px;
      background: #e2e8f0;
      margin: 0 1rem;
    }
    .step-line.active {
      background: #3b82f6;
    }

    .step-tag {
      font-size: 0.75rem;
      font-weight: 700;
      color: #3b82f6;
      letter-spacing: 0.08em;
      margin-bottom: 0.25rem;
    }
    .step-title {
      font-size: 2.25rem;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.02em;
    }
    .step-subtitle {
      font-size: 1rem;
      color: #64748b;
      margin-bottom: 2rem;
    }

    /* Upload Box Step 1 */
    .upload-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 20px;
      padding: 2rem;
      margin-bottom: 2rem;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    }
    .dropzone {
      border: 2px dashed #cbd5e1;
      border-radius: 16px;
      padding: 3rem 2rem;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s;
      background: #f8fafc;
    }
    .dropzone:hover, .dropzone.dragover {
      border-color: #3b82f6;
      background: #eff6ff;
    }
    .upload-icon-circle {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: #eff6ff;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 1rem;
      font-size: 1.75rem;
    }
    .dropzone-text h3 {
      font-size: 1.1rem;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 0.25rem;
    }
    .dropzone-text p {
      font-size: 0.85rem;
      color: #64748b;
    }
    .file-input-hidden { display: none; }

    .file-item-badge {
      display: flex;
      align-items: center;
      gap: 1rem;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 12px;
      padding: 1rem;
      margin-top: 1.5rem;
    }
    .file-icon-box {
      font-size: 1.5rem;
    }
    .file-details {
      flex: 1;
    }
    .file-name {
      font-weight: 700;
      color: #1e40af;
      font-size: 0.95rem;
    }
    .file-size {
      font-size: 0.78rem;
      color: #3b82f6;
    }
    .btn-remove-file {
      background: none;
      border: none;
      color: #94a3b8;
      font-size: 1.1rem;
      cursor: pointer;
    }

    .requirements-box {
      margin-top: 1.75rem;
      padding-top: 1.25rem;
      border-top: 1px solid #f1f5f9;
    }
    .requirements-box h4 {
      font-size: 0.85rem;
      font-weight: 700;
      color: #475569;
      margin-bottom: 0.5rem;
    }
    .requirements-box ul {
      list-style: none;
      display: flex;
      gap: 2rem;
    }
    .requirements-box li {
      font-size: 0.85rem;
      color: #64748b;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }
    .requirements-box .check {
      color: #10b981;
      font-weight: 800;
    }

    .doc-details-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 20px;
      padding: 2rem;
      margin-bottom: 2rem;
    }
    .textarea-content {
      resize: vertical;
      min-height: 140px;
    }

    /* Personalization Step 2 */
    .personalization-grid {
      display: grid;
      grid-template-columns: 1.4fr 0.8fr;
      gap: 2rem;
    }
    .form-panel {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 20px;
      padding: 2rem;
    }
    .panel-header {
      font-size: 1.25rem;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 0.25rem;
    }
    .panel-sub {
      font-size: 0.85rem;
      color: #64748b;
      margin-bottom: 2rem;
    }

    .summary-panel {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 20px;
      padding: 2rem;
      height: fit-content;
    }
    .summary-title {
      font-size: 1.15rem;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 0.25rem;
    }
    .summary-sub {
      font-size: 0.82rem;
      color: #64748b;
      margin-bottom: 1.75rem;
    }
    .summary-list {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      margin-bottom: 2rem;
    }
    .summary-item {
      display: flex;
      align-items: flex-start;
      gap: 0.85rem;
    }
    .item-icon {
      font-size: 1.1rem;
      background: #eff6ff;
      padding: 0.4rem;
      border-radius: 8px;
    }
    .item-label {
      font-size: 0.75rem;
      color: #64748b;
      font-weight: 600;
    }
    .item-value {
      font-size: 0.9rem;
      font-weight: 700;
      color: #0f172a;
    }

    .info-alert-box {
      background: #f0f9ff;
      border: 1px solid #bae6fd;
      border-radius: 12px;
      padding: 1rem;
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      font-size: 0.82rem;
      color: #0369a1;
      line-height: 1.4;
    }

    .step-actions {
      display: flex;
      gap: 1rem;
      margin-top: 2rem;
    }
    .step-actions.right-align {
      justify-content: flex-end;
    }
    .step-actions.split {
      justify-content: space-between;
    }

    @media (max-width: 900px) {
      .personalization-grid {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class StepperCreationComponent implements OnInit {
  @Input() initialStep: number = 1;
  @Output() completed = new EventEmitter<{ request: AdaptationRequest; response: AdaptationResponse }>();

  currentStep: number = 1;

  // Step 1 State
  isDragging: boolean = false;
  selectedFile?: File;
  documentTitle: string = '';
  documentContent: string = '';

  // Step 2 State
  perfilDestinatario: string = 'Desarrollador Junior / Semi Senior';
  formatoSalida: string = 'Guía Práctica Paso a Paso (Tutorial)';
  nichoSector: string = 'General';
  nivelDetalle: string = 'Didáctico';
  cantidadGenerar: number = 5;
  instruccionesAdicionales: string = '';

  get cantidadLabel(): string {
    if (this.formatoSalida.includes('Flashcard')) {
      return 'Número de flashcards de memorización a generar';
    } else if (this.formatoSalida.includes('Quiz')) {
      return 'Número de preguntas de quiz interactivo a generar';
    } else if (this.formatoSalida.includes('TLDR') || this.formatoSalida.includes('Resumen')) {
      return 'Número de secciones de síntesis a generar';
    }
    return 'Número de pasos / páginas de la guía a generar';
  }

  // Step 3 State
  progressVal: number = 0;
  pipelineStage: string = 'Iniciando pipeline agéntico...';
  response?: AdaptationResponse;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    if (this.initialStep) {
      this.currentStep = this.initialStep;
    }
  }

  goToStep(step: number): void {
    this.currentStep = step;
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;
    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      this.handleFile(event.dataTransfer.files[0]);
    }
  }

  onFileSelected(event: any): void {
    if (event.target.files && event.target.files.length > 0) {
      this.handleFile(event.target.files[0]);
    }
  }

  handleFile(file: File): void {
    this.selectedFile = file;
    this.documentTitle = file.name;

    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext === 'txt' || ext === 'md' || ext === 'markdown') {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.documentContent = e.target?.result as string || '';
      };
      reader.readAsText(file);
    } else if (ext === 'pdf') {
      this.apiService.parsePdf(file).subscribe({
        next: (res) => {
          if (res.texto_extraido) {
            this.documentContent = res.texto_extraido;
          }
        },
        error: () => {
          console.log('Utilizando extractor para PDF');
        }
      });
    }
  }

  clearFile(event: MouseEvent): void {
    event.stopPropagation();
    this.selectedFile = undefined;
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024 * 1024) {
      return `${Math.round(bytes / 1024)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  startGeneration(): void {
    this.currentStep = 3;
    this.progressVal = 10;
    this.pipelineStage = 'Extracción de AST & Normalización de texto';

    const interval = setInterval(() => {
      this.progressVal += 15;
      if (this.progressVal === 25) {
        this.pipelineStage = 'Chunking semántico & FAISS Vector Indexing';
      } else if (this.progressVal === 55) {
        this.pipelineStage = 'Grafo Graph RAG & LangGraph Agent Orquestation';
      } else if (this.progressVal === 78) {
        this.pipelineStage = 'Google Gemini 1.5 Pro - Redacción Didáctica & Auditoría';
      } else if (this.progressVal >= 100) {
        this.progressVal = 100;
        clearInterval(interval);
      }
    }, 500);

    const payload: AdaptationRequest = {
      documento_titulo: this.documentTitle,
      documento_contenido: this.documentContent,
      perfil_destinatario: this.perfilDestinatario,
      formato_salida: this.formatoSalida,
      nicho_sector: this.nichoSector,
      nivel_detalle: this.nivelDetalle,
      cantidad_generar: this.cantidadGenerar,
      instrucciones_adicionales: this.instruccionesAdicionales
    };

    this.apiService.adaptContent(payload).subscribe({
      next: (res) => {
        setTimeout(() => {
          this.response = res;
          this.currentStep = 4;
          this.completed.emit({ request: payload, response: res });
        }, 2500);
      },
      error: () => {
        setTimeout(() => {
          this.response = this.apiService.generateMockResponse(payload);
          this.currentStep = 4;
          this.completed.emit({ request: payload, response: this.response });
        }, 2500);
      }
    });
  }
}
