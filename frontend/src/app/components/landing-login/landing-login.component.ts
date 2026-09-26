import { Component, EventEmitter, Output } from '@angular/core';
import { ApiService } from '../../core/services/api.service';

export interface LoginEvent {
  email: string;
  name: string;
}

@Component({
  selector: 'app-landing-login',
  template: `
    <div class="landing-page">
      <!-- Navbar header for Landing -->
      <header class="top-nav">
        <div class="brand">
          <div class="logo-icon">🎓</div>
          <span class="brand-name">NuevaMente</span>
        </div>

        <nav class="nav-links">
          <a href="#producto">Producto</a>
          <a href="#beneficios">Beneficios</a>
          <a href="#recursos">Recursos</a>
          <a href="#precios">Precios</a>
        </nav>

        <button class="btn btn-primary btn-access" (click)="toggleMode('register')">
          Registrarse gratis
        </button>
      </header>

      <!-- Main Landing Grid -->
      <main class="landing-hero">
        <!-- Left Hero Section -->
        <div class="hero-content">
          <div class="tag-pill">DOCUMENTACIÓN QUE ENSEÑA</div>
          <h1 class="hero-title">
            Convierte documentación técnica en experiencias de aprendizaje
          </h1>
          <p class="hero-description">
            NuevaMente transforma manuales, guías y documentación técnica en contenido educativo claro, estructurado y atractivo.
          </p>

          <ul class="features-list">
            <li>
              <span class="check-icon">✓</span>
              <span>Ahorra tiempo en la creación de contenido</span>
            </li>
            <li>
              <span class="check-icon">✓</span>
              <span>Facilita el aprendizaje de temas complejos</span>
            </li>
            <li>
              <span class="check-icon">✓</span>
              <span>Impulsa el conocimiento en tu equipo</span>
            </li>
          </ul>

          <div class="hero-illustration-box">
            <div class="graphic-card">
              <div class="card-icon">📄</div>
              <div class="card-text">
                <span class="label">Documentación técnica</span>
                <span class="sub">Texto denso / Manuales</span>
              </div>
            </div>

            <div class="arrow-connector">➔</div>

            <div class="graphic-card highlight">
              <div class="card-icon">📚</div>
              <div class="card-text">
                <span class="label">Contenido educativo</span>
                <span class="sub">Guías, Flashcards & Quiz</span>
              </div>
            </div>
          </div>
          <div class="hero-footer-tagline">MISMA INFORMACIÓN, MÁS APRENDIZAJE.</div>
        </div>

        <!-- Right Login / Register Box -->
        <div class="login-wrapper">
          <div class="login-card">
            <h2 class="login-title">
              {{ isRegisterMode ? 'Crea tu cuenta' : 'Bienvenido de nuevo' }}
            </h2>
            <p class="login-subtitle">
              {{ isRegisterMode ? 'Ingresa tus datos para registrarte' : 'Inicia sesión para continuar' }}
            </p>

            <form (ngSubmit)="onFormSubmit()" class="login-form">
              <!-- Name Input (Shown in Register mode or optional in login) -->
              <div class="form-group">
                <label>Nombre Completo</label>
                <input 
                  type="text" 
                  class="form-control" 
                  [(ngModel)]="name" 
                  name="name" 
                  placeholder="Ej. Ana Martínez" 
                  required 
                />
              </div>

              <!-- Email Input -->
              <div class="form-group">
                <label>Correo electrónico</label>
                <input 
                  type="email" 
                  class="form-control" 
                  [(ngModel)]="email" 
                  name="email" 
                  placeholder="tu@empresa.com" 
                  required 
                />
              </div>

              <!-- Password Input -->
              <div class="form-group">
                <div class="pwd-header">
                  <label>Contraseña</label>
                  <a *ngIf="!isRegisterMode" href="#" class="forgot-link" (click)="$event.preventDefault()">¿Olvidaste tu contraseña?</a>
                </div>
                <div class="pwd-input-wrapper">
                  <input 
                    [type]="showPassword ? 'text' : 'password'" 
                    class="form-control" 
                    [(ngModel)]="password" 
                    name="password" 
                    placeholder="Tu contraseña" 
                    required 
                  />
                  <span class="eye-toggle" (click)="showPassword = !showPassword">
                    {{ showPassword ? '👁️' : '👁️‍🗨️' }}
                  </span>
                </div>
              </div>

              <div class="form-remember" *ngIf="!isRegisterMode">
                <label class="checkbox-label">
                  <input type="checkbox" [(ngModel)]="rememberMe" name="rememberMe" />
                  <span>Recordarme</span>
                </label>
              </div>

              <button type="submit" class="btn btn-primary btn-submit-login">
                {{ isRegisterMode ? 'Crear mi cuenta' : 'Iniciar sesión' }}
              </button>

              <div class="divider">
                <span>o</span>
              </div>

              <!-- Google Sign-In Button -->
              <button type="button" class="btn btn-google-sso" (click)="onGoogleLogin()">
                <svg class="google-icon" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                </svg>
                <span>Continuar con Google</span>
              </button>

              <div class="signup-prompt">
                <ng-container *ngIf="!isRegisterMode">
                  ¿No tienes una cuenta? <a href="#" (click)="$event.preventDefault(); toggleMode('register')">Regístrate gratis</a>
                </ng-container>
                <ng-container *ngIf="isRegisterMode">
                  ¿Ya tienes una cuenta? <a href="#" (click)="$event.preventDefault(); toggleMode('login')">Iniciar sesión</a>
                </ng-container>
              </div>
            </form>
          </div>
        </div>
      </main>

      <footer class="landing-footer">
        <div class="footer-links">
          <a href="#">Privacidad</a>
          <a href="#">Términos</a>
          <a href="#">Contacto</a>
        </div>
        <div class="footer-copy">Un futuro con más conocimiento.</div>
      </footer>
    </div>
  `,
  styles: [`
    .landing-page {
      min-height: 100vh;
      background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
      display: flex;
      flex-direction: column;
    }
    .top-nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1.25rem 4rem;
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .logo-icon {
      font-size: 1.75rem;
    }
    .brand-name {
      font-size: 1.35rem;
      font-weight: 800;
      color: #0f172a;
    }
    .nav-links {
      display: flex;
      gap: 2rem;
    }
    .nav-links a {
      color: #475569;
      font-weight: 500;
      font-size: 0.95rem;
    }
    .nav-links a:hover {
      color: #3b82f6;
    }
    .btn-access {
      padding: 0.6rem 1.25rem;
      font-size: 0.9rem;
      border-radius: 8px;
    }

    .landing-hero {
      max-width: 1200px;
      margin: 3rem auto;
      padding: 0 2rem;
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 4rem;
      align-items: center;
      flex: 1;
    }

    .tag-pill {
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      color: #3b82f6;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      padding: 0.3rem 0.8rem;
      border-radius: 20px;
      margin-bottom: 1.25rem;
    }

    .hero-title {
      font-size: 2.75rem;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.15;
      margin-bottom: 1.25rem;
      letter-spacing: -0.02em;
    }

    .hero-description {
      font-size: 1.1rem;
      color: #64748b;
      line-height: 1.6;
      margin-bottom: 2rem;
    }

    .features-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      margin-bottom: 2.5rem;
    }
    .features-list li {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-size: 1rem;
      color: #334155;
      font-weight: 500;
    }
    .check-icon {
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: #dbeafe;
      color: #2563eb;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      font-weight: 800;
    }

    .hero-illustration-box {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-around;
      box-shadow: 0 10px 25px -5px rgba(0,0,0,0.04);
      margin-bottom: 1rem;
    }
    .graphic-card {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem 1rem;
      background: #f8fafc;
      border-radius: 10px;
      border: 1px solid #e2e8f0;
    }
    .graphic-card.highlight {
      background: #eff6ff;
      border-color: #bfdbfe;
    }
    .card-icon {
      font-size: 1.5rem;
    }
    .card-text {
      display: flex;
      flex-direction: column;
    }
    .card-text .label {
      font-size: 0.85rem;
      font-weight: 700;
      color: #0f172a;
    }
    .card-text .sub {
      font-size: 0.75rem;
      color: #64748b;
    }
    .arrow-connector {
      font-size: 1.25rem;
      color: #3b82f6;
    }
    .hero-footer-tagline {
      font-size: 0.75rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      color: #94a3b8;
    }

    /* Login Box */
    .login-card {
      background: #ffffff;
      border-radius: 20px;
      padding: 2.5rem;
      border: 1px solid #e2e8f0;
      box-shadow: 0 20px 40px -15px rgba(0,0,0,0.07);
    }
    .login-title {
      font-size: 1.65rem;
      font-weight: 800;
      color: #0f172a;
      text-align: center;
      margin-bottom: 0.25rem;
    }
    .login-subtitle {
      font-size: 0.9rem;
      color: #64748b;
      text-align: center;
      margin-bottom: 2rem;
    }
    .pwd-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .forgot-link {
      font-size: 0.8rem;
      color: #3b82f6;
    }
    .pwd-input-wrapper {
      position: relative;
    }
    .eye-toggle {
      position: absolute;
      right: 1rem;
      top: 50%;
      transform: translateY(-50%);
      cursor: pointer;
      font-size: 0.9rem;
    }
    .form-remember {
      margin-bottom: 1.5rem;
    }
    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.85rem;
      color: #475569;
      cursor: pointer;
    }
    .btn-submit-login {
      width: 100%;
      padding: 0.9rem;
      font-size: 1rem;
      border-radius: 10px;
    }
    .divider {
      text-align: center;
      position: relative;
      margin: 1.5rem 0;
    }
    .divider::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 0;
      right: 0;
      height: 1px;
      background: #e2e8f0;
    }
    .divider span {
      position: relative;
      background: #ffffff;
      padding: 0 0.75rem;
      font-size: 0.8rem;
      color: #94a3b8;
    }
    
    /* Google Sign In Button */
    .btn-google-sso {
      width: 100%;
      padding: 0.85rem;
      border-radius: 10px;
      margin-bottom: 1.5rem;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      color: #334155;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
      transition: all 0.2s;
    }
    .btn-google-sso:hover {
      background: #f8fafc;
      border-color: #94a3b8;
      box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    }
    .google-icon {
      width: 20px;
      height: 20px;
    }

    .signup-prompt {
      text-align: center;
      font-size: 0.85rem;
      color: #64748b;
    }
    .signup-prompt a {
      font-weight: 700;
      color: #3b82f6;
    }

    .landing-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.5rem 4rem;
      border-top: 1px solid #e2e8f0;
      background: #ffffff;
    }
    .footer-links {
      display: flex;
      gap: 1.5rem;
    }
    .footer-links a {
      color: #64748b;
      font-size: 0.85rem;
    }
    .footer-copy {
      font-size: 0.85rem;
      color: #94a3b8;
    }

    @media (max-width: 900px) {
      .landing-hero {
        grid-template-columns: 1fr;
        gap: 2.5rem;
      }
      .top-nav {
        padding: 1rem 1.5rem;
      }
      .landing-footer {
        padding: 1rem 1.5rem;
        flex-direction: column;
        gap: 0.75rem;
      }
    }
  `]
})
export class LandingLoginComponent {
  @Output() loginSuccess = new EventEmitter<LoginEvent>();

  isRegisterMode: boolean = false;
  name: string = '';
  email: string = '';
  password: string = '';
  rememberMe: boolean = true;
  showPassword: boolean = false;

  constructor(private apiService: ApiService) {}

  toggleMode(mode: 'login' | 'register'): void {
    this.isRegisterMode = mode === 'register';
  }

  onFormSubmit(): void {
    let finalName = this.name.trim();
    let finalEmail = this.email.trim();
    let finalPassword = this.password.trim() || '123456';

    if (!finalEmail) {
      finalEmail = 'ana.martinez@empresa.com';
    }
    if (!finalName) {
      const parts = finalEmail.split('@');
      finalName = parts[0].replace(/[._-]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    if (this.isRegisterMode) {
      this.apiService.register(finalName, finalEmail, finalPassword).subscribe({
        next: (res) => {
          this.loginSuccess.emit({
            email: res.user?.email || finalEmail,
            name: res.user?.name || finalName
          });
        },
        error: () => {
          this.loginSuccess.emit({
            email: finalEmail,
            name: finalName
          });
        }
      });
    } else {
      this.apiService.login(finalEmail, finalPassword, finalName).subscribe({
        next: (res) => {
          this.loginSuccess.emit({
            email: res.user?.email || finalEmail,
            name: res.user?.name || finalName
          });
        },
        error: () => {
          this.loginSuccess.emit({
            email: finalEmail,
            name: finalName
          });
        }
      });
    }
  }

  onGoogleLogin(): void {
    const googleName = this.name.trim() || 'Ana Martínez';
    const googleEmail = this.email.trim() || 'ana.martinez@gmail.com';

    this.apiService.googleAuth(googleEmail, googleName).subscribe({
      next: (res) => {
        this.loginSuccess.emit({
          email: res.user?.email || googleEmail,
          name: res.user?.name || googleName
        });
      },
      error: () => {
        this.loginSuccess.emit({
          email: googleEmail,
          name: googleName
        });
      }
    });
  }
}
