import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { DocumentUploaderComponent } from './components/document-uploader/document-uploader.component';
import { ParameterConfigComponent } from './components/parameter-config/parameter-config.component';
import { ContentViewerComponent } from './components/content-viewer/content-viewer.component';
import { InteractiveFlashcardsComponent } from './components/interactive-flashcards/interactive-flashcards.component';
import { InteractiveQuizComponent } from './components/interactive-quiz/interactive-quiz.component';
import { MetadataDashboardComponent } from './components/metadata-dashboard/metadata-dashboard.component';

@NgModule({
  declarations: [
    AppComponent,
    DocumentUploaderComponent,
    ParameterConfigComponent,
    ContentViewerComponent,
    InteractiveFlashcardsComponent,
    InteractiveQuizComponent,
    MetadataDashboardComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
