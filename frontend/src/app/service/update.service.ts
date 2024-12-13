import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({providedIn: 'root'})
export class UpdateService {
  private updateSubject = new Subject<string>();
  update$ = this.updateSubject.asObservable();

  notifyProcess() {
    this.updateSubject.next('process');
  }

  notifyUpdate() {
    this.updateSubject.next('update');
  }
}
