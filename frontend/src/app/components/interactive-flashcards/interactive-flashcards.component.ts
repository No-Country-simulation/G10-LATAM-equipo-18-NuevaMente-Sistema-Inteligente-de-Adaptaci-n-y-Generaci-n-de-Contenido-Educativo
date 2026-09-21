import { Component, Input } from '@angular/core';
import { FlashcardItem } from '../../core/models/adaptation.model';

@Component({
  selector: 'app-interactive-flashcards',
  template: `
    <div class="flashcards-container" *ngIf="items && items.length > 0">
      <h3 class="title">🎴 Flashcards Didácticas de Memorización</h3>
      <div class="cards-grid">
        <div 
          *ngFor="let card of items; let i = index" 
          class="card-wrapper"
          (click)="toggleCard(i)"
        >
          <div class="card" [class.flipped]="flippedState[i]">
            <div class="card-face card-front">
              <span class="card-tag">Pregunta / Concepto #{{ i + 1 }}</span>
              <p class="card-text">{{ card.frente }}</p>
              <span class="hint" *ngIf="card.pista_didactica">💡 Pista: {{ card.pista_didactica }}</span>
              <span class="flip-action">Haz clic para voltear 🔄</span>
            </div>
            <div class="card-face card-back">
              <span class="card-tag">Explicación Adaptada</span>
              <p class="card-text">{{ card.dorso }}</p>
              <span class="flip-action">Haz clic para volver 🔄</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .flashcards-container { margin-top: 2rem; }
    .title { font-size: 1.25rem; font-weight: bold; color: #1e293b; margin-bottom: 1rem; }
    .cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
    .card-wrapper { perspective: 1000px; cursor: pointer; min-height: 220px; }
    .card { width: 100%; height: 100%; position: relative; transform-style: preserve-3d; transition: transform 0.6s ease; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .card.flipped { transform: rotateY(180deg); }
    .card-face { position: absolute; width: 100%; height: 100%; backface-visibility: hidden; padding: 1.5rem; border-radius: 12px; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #e2e8f0; }
    .card-front { background-color: #ffffff; color: #0f172a; }
    .card-back { background-color: #eff6ff; color: #1e40af; transform: rotateY(180deg); }
    .card-tag { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #64748b; }
    .card-text { font-size: 1rem; font-weight: 600; line-height: 1.5; }
    .hint { font-size: 0.85rem; color: #d97706; font-style: italic; }
    .flip-action { font-size: 0.8rem; color: #94a3b8; text-align: right; }
  `]
})
export class InteractiveFlashcardsComponent {
  @Input() items: FlashcardItem[] = [];
  flippedState: { [key: number]: boolean } = {};

  toggleCard(index: number): void {
    this.flippedState[index] = !this.flippedState[index];
  }
}
