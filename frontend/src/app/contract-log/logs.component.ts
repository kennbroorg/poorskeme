import { Component, Input, ViewChild, ElementRef, AfterViewInit, OnChanges, SimpleChanges } from '@angular/core';
// import { Component, Input } from '@angular/core';
// import { trigger, state, style, transition, animate } from '@angular/animations';

@Component({
  selector: 'contract-logs',
  templateUrl: './logs.component.html',
  styleUrls: ['./logs.component.scss'],
  // animations: [
  //   trigger('slideInOut', [
  //     state('in', style({ transform: 'translateX(0)' })),
  //     transition(':enter', [
  //       style({ transform: 'translateX(-100%)' }),
  //       animate('200ms ease-in')
  //     ]),
  //     transition(':leave', [
  //       animate('200ms ease-out', style({ transform: 'translateX(-100%)' }))
  //     ])
  //   ])
  // ]
})
export class LogsComponent implements AfterViewInit, OnChanges {

  @ViewChild('scrollableCard') private scrollContainer!: ElementRef;

  // @Input() log!: boolean;
  @Input() data: string[] = [];
  isVisible = true;

  ngAfterViewInit() {
    this.scrollToBottom();
  }

  // Función para mantener el scroll en el fondo
  scrollToBottom(): void {
    // console.log("Container", this.scrollContainer);
    try {
      this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }

  ngOnChanges(changes: SimpleChanges) {
    // console.log(changes);
    if (changes['data']) {
      // setTimeout(() => this.scrollToBottom(), 100);
      console.log("DATA CAMBIO", this.data);
      this.scrollToBottom();
    }
  }

  toggleVisibility() {
    this.isVisible = !this.isVisible;
  }

}
