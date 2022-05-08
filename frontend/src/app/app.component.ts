import { Component } from '@angular/core';
import { Subject } from "rxjs";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  subject = new Subject<string>();

    ngOnInit(): void {
    this.subject.subscribe((text: string) => {
      console.log(`Received from child component: ${text}`);
    });
  }

  handleInfo = (info: string) => {
    this.subject.next(info);
  };
}
