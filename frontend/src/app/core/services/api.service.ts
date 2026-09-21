import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AdaptationRequest, AdaptationResponse } from '../models/adaptation.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api/v1';

  constructor(private http: HttpClient) {}

  adaptContent(request: AdaptationRequest): Observable<AdaptationResponse> {
    return this.http.post<AdaptationResponse>(`${this.baseUrl}/adapt-content`, request);
  }

  checkHealth(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/health`);
  }
}
