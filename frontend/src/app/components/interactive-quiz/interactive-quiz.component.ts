import { Component, Input } from '@angular/core';
import { QuizItem } from '../../core/models/adaptation.model';

@Component({
  selector: 'app-interactive-quiz',
  template: `
    <div class="quiz-container" *ngIf="quizzes && quizzes.length > 0">
      <h3 class="title">🧠 Quiz Interactivo con Retroalimentación Instantánea</h3>
      <div *ngFor="let q of quizzes; let qIdx = index" class="quiz-card">
        <h4 class="question">{{ qIdx + 1 }}. {{ q.pregunta }}</h4>
        <div class="options-list">
          <button 
            *ngFor="let opt of q.opciones"
            class="option-btn"
            [class.selected]="selectedAnswers[qIdx] === opt"
            [class.correct]="submitted[qIdx] && opt === q.respuesta_correcta"
            [class.incorrect]="submitted[qIdx] && selectedAnswers[qIdx] === opt && opt !== q.respuesta_correcta"
            (click)="selectOption(qIdx, opt)"
          >
            {{ opt }}
          </button>
        </div>
        <button 
          *ngIf="selectedAnswers[qIdx] && !submitted[qIdx]"
          class="submit-btn"
          (click)="submitAnswer(qIdx)"
        >
          Validar Respuesta 🚀
        </button>

        <div *ngIf="submitted[qIdx]" class="feedback-box">
          <p class="feedback-title" [class.success]="selectedAnswers[qIdx] === q.respuesta_correcta">
            {{ selectedAnswers[qIdx] === q.respuesta_correcta ? '✅ ¡Correcto!' : '❌ Respuesta Incorrecta' }}
          </p>
          <p class="justification">💡 <strong>Justificación Didáctica:</strong> {{ q.justificacion_didactica }}</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .quiz-container { margin-top: 2rem; background: #ffffff; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; }
    .title { font-size: 1.25rem; font-weight: bold; color: #0f172a; margin-bottom: 1.5rem; }
    .quiz-card { background: #f8fafc; padding: 1.25rem; border-radius: 8px; margin-bottom: 1.5rem; border: 1px solid #cbd5e1; }
    .question { font-size: 1.05rem; font-weight: 700; color: #1e293b; margin-bottom: 1rem; }
    .options-list { display: flex; flex-direction: column; gap: 0.75rem; }
    .option-btn { width: 100%; text-align: left; padding: 0.85rem 1.25rem; border-radius: 6px; border: 1px solid #cbd5e1; background: white; font-size: 0.95rem; cursor: pointer; transition: all 0.2s ease; }
    .option-btn:hover { background: #f1f5f9; border-color: #94a3b8; }
    .option-btn.selected { border-color: #3b82f6; background: #eff6ff; font-weight: 600; }
    .option-btn.correct { background: #dcfce7 !important; border-color: #22c55e !important; color: #15803d; font-weight: bold; }
    .option-btn.incorrect { background: #fee2e2 !important; border-color: #ef4444 !important; color: #b91c1c; }
    .submit-btn { margin-top: 1rem; padding: 0.6rem 1.2rem; background: #2563eb; color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
    .submit-btn:hover { background: #1d4ed8; }
    .feedback-box { margin-top: 1rem; padding: 1rem; border-radius: 6px; background: white; border-left: 4px solid #3b82f6; }
    .feedback-title { font-weight: bold; font-size: 1rem; margin-bottom: 0.5rem; color: #dc2626; }
    .feedback-title.success { color: #16a34a; }
    .justification { font-size: 0.9rem; color: #334155; line-height: 1.4; }
  `]
})
export class InteractiveQuizComponent {
  @Input() quizzes: QuizItem[] = [];
  selectedAnswers: { [key: number]: string } = {};
  submitted: { [key: number]: boolean } = {};

  selectOption(qIdx: number, option: string): void {
    if (!this.submitted[qIdx]) {
      this.selectedAnswers[qIdx] = option;
    }
  }

  submitAnswer(qIdx: number): void {
    this.submitted[qIdx] = true;
  }
}
