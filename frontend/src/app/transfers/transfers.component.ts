import { Component, OnInit, ViewChild, ElementRef, Input, Output, EventEmitter, AfterViewInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import CirclePack from 'circlepack-chart';
@Component({
  selector: 'app-transfers',
  templateUrl: './transfers.component.html',
  styleUrls: ['./transfers.component.scss']
})
export class TransfersComponent implements OnInit {
  @ViewChild('cardCircle', {static: true}) cardContainer!: ElementRef<HTMLElement>;
  @Output() onInfo: EventEmitter<string> = new EventEmitter<string>();
  @Input() public h: any;
  @Input() public w: any;


  card: any;
  width: any = 500;
  height: any = 500;
  diameter: any;
  view: any;
  circle1: any;

  transfers: any = [];
  visibility: boolean = false;

  constructor(private httpClient: HttpClient) { }

  ngOnInit(): void {
    console.log("Init de Transfers");
    // const url = "http://127.0.0.1:5000/transfers"
    // this.httpClient
    //   .get(url)
    //   .subscribe(this.responseTransfers,
    //              err => console.error('Ops: ', err.message),
    //              () => console.log('Completed Transfers'),
    //   );

    // this.responseTransfers(this.data);
  }

  ngAfterViewInit() {
    console.log("AfterInit de Transfers");
    const url = "http://127.0.0.1:5000/transfers"
    this.httpClient
      .get(url)
      .subscribe(this.responseTransfers,
                 err => console.error('Ops: ', err.message),
                 () => console.log('Completed Transfers'),
      );

    // this.responseTransfers(this.data);
  }

  private responseTransfers = (data: any): any => {
    this.transfers = data;
    console.log(`Transfers: ${this.transfers}`)
    this.visibility = true;

    this.card = this.cardContainer.nativeElement;
    // this.width = this.card.parentNode.clientWidth;
    this.width = this.w;
    // this.height = this.card.parentNode.clientHeight;
    this.height = this.h;
    this.diameter = this.height;
    console.log(`Width: ${this.width} - Height: ${this.height} - Diameter: ${this.diameter}`)
    console.log(`Screen Width: ${screen.availWidth} - Screen Height: ${screen.availHeight}`)
    console.log(`Inner Width: ${window.innerWidth} - Inner Height: ${window.innerHeight}`)

    const CHILDREN_PROB_DECAY = 1;
    const MAX_CHILDREN = 1000;
    const MAX_VALUE = 100;

    function genNode(name='Schema', probOfChildren=1): any {
      if (Math.random() < probOfChildren) {
        return {
          name,
          children: [...Array(Math.round(Math.random() * MAX_CHILDREN))]
            .map((_, i: any) => genNode(i, probOfChildren - CHILDREN_PROB_DECAY))
        }
      } else {
        return {
          name,
          value: Math.round(Math.random() * MAX_VALUE)
        }
      }
    }

    this.circle1 = CirclePack()
      .data(data)
      .sort((a: any, b: any) => b.value - a.value)
      .width(this.width)
      .height(this.height)
      .size('size')
      .excludeRoot(true)
      .color(function(d: any) {
        if (d.name == "IN") {
            // return "rgba(144, 213, 179, 0.4)";
            // return "rgba(144, 213, 213, 0.4)";
            // return "rgba(204, 255, 255, 0.2)"; // --> ESTE
            return "rgba(204, 242, 255, 0.6)"; // --> ESTE
        } else if (d.name == "OUT") {
            return "rgba(102, 217, 255, 0.6)"; // --> ESTE
            // return "rgba(254, 27, 37, 0.2)"; // --> ESTE
            // return "rgba(190, 217, 255, 0.4)";
            // return "rgba(209, 54, 8, 0.8)" ;
        } else { 
            return "rgba(0, 0, 0, 0.3)" ;
        }
       })
      .onClick(this.clicking)
      .padding(0)
      (this.card);

      console.log(`Circle: ${this.circle1}`)
  }

  clicking = (data: any) => {
    if (data) {
      if (data.name == "IN") {this.onInfo.emit(data.__dataNode.parent.data.name)}
      else if (data.name == "OUT") {this.onInfo.emit(data.__dataNode.parent.data.name)}
      else {this.onInfo.emit(data.name);}
      this.circle1.zoomToNode(data);
    } else {
      this.circle1.zoomReset();
      this.onInfo.emit("null");
    }
  }

}