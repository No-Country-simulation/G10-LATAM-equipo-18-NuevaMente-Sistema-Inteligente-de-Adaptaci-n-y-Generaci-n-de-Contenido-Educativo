import { Component, Input } from '@angular/core';
import { FlashcardItem } from '../../core/models/adaptation.model';

@Component({
  selector: 'app-interactive-flashcards',
  template: `
    <div class="flashcards-section">
      <div class="section-header">
        <h3>🎴 Flashcards Didácticas ({{ items.length }})</h3>
        <span class="subtext">Haz clic en cada tarjeta para girarla y ver la respuesta.</span>
      </div>

      <div class="flashcards-grid">
        <div 
          *ngFor="let card of items; let i = index" 
          class="flashcard-card" 
          [ngClass]="{'flipped': flippedState[i]}"
          (click)="toggleFlip(i)"
        >
          <div class="card-inner">
            <!-- Front Face -->
            <div class="card-front">
              <div class="card-header-badge">Flashcard #{{ i + 1 }}</div>
              <div class="card-question">❓ {{ card.frente }}</div>
              <div *ngIf="card.pista_didactica" class="card-hint">
                💡 <strong>Pista:</strong> {{ card.pista_didactica }}
              </div>
              <div class="flip-instruction">Toca para voltear ➔</div>
            </div>

            <!-- Back Face -->
            <div class="card-back">
              <div class="card-header-badge back-badge">Respuesta Didáctica</div>
              <div class="card-answer">✨ {{ card.dorso }}</div>
              <div class="flip-instruction back-instruction">↺ Volver a la pregunta</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .flashcards-section {
      margin-top: 2rem;
      margin-bottom: 2rem;
    }
    .section-header {
      margin-bottom: 1.25rem;
    }
    .section-header h3 {
      font-size: 1.25rem;
      font-weight: 800;
      color: #0f172a;
    }
    .subtext {
      font-size: 0.85rem;
      color: #64748b;
    }

    .flashcards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.25rem;
    }

    .flashcard-card {
      perspective: 1000px;
      height: 220px;
      cursor: pointer;
    }

    .card-inner {
      position: relative;
      width: 100%;
      height: 100%;
      transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
      transform-style: preserve-3d;
      border-radius: 16px;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
    }

    .flashcard-card.flipped .card-inner {
      transform: rotateY(180deg);
    }

    .card-front, .card-back {
      position: absolute;
      width: 100%;
      height: 100%;
      backface-visibility: hidden;
      border-radius: 16px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      border: 1px solid #e2e8f0;
      background: #ffffff;
    }

    .card-front {
      background: #ffffff;
    }

    .card-back {
      background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
      border-color: #bfdbfe;
      transform: rotateY(180deg);
    }

    .card-header-badge {
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #3b82f6;
    }
    .back-badge {
      color: #1e40af;
    }

    .card-question {
      font-size: 1.05rem;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.4;
    }

    .card-hint {
      font-size: 0.8rem;
      color: #b45309;
      background: #fffbeb;
      padding: 0.4rem 0.75rem;
      border-radius: 8px;
    }

    .card-answer {
      font-size: 0.98rem;
      font-weight: 600;
      color: #1e3a8a;
      line-height: 1.5;
    }

    .flip-instruction {
      font-size: 0.75rem;
      font-weight: 700;
      color: #94a3b8;
      text-align: right;
    }
    .back-instruction {
      color: #3b82f6;
    }
  `]
})
export class InteractiveFlashcardsComponent {
  @Input() items: FlashcardItem[] = [];

  flippedState: { [key: number]: boolean } = {};

  toggleFlip(index: number): void {
    this.flippedState[index] = !this.flippedState[index];
  }
}
