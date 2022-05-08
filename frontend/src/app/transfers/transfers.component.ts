import { Component, OnInit, ViewChild, ElementRef, Output, EventEmitter} from '@angular/core';
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

  card: any;
  width: any = 500;
  height: any = 500;
  diameter: any;
  view: any;
  circle: any;

  transfers: any = [];
  visibility: boolean = false;

  constructor(private httpClient: HttpClient) { }

  ngOnInit(): void {
    const url = "http://127.0.0.1:5000/transfers"
    this.httpClient
      .get(url)
      .subscribe(this.responseTransfers,
                 err => console.error('Ops: ', err.message),
                 () => console.log('Completed Transfers'),
      );
  }

  private responseTransfers = (data: any): any => {
    this.transfers = data;
    this.visibility = true;

    this.card = this.cardContainer.nativeElement;
    this.width = this.card.parentNode.clientWidth;
    this.height = this.card.parentNode.clientHeight;
    this.diameter = this.height;

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

    this.circle = CirclePack()
      .data(data)
      .sort((a: any, b: any) => b.value - a.value)
      .width(this.width)
      .height(this.height)
      .size('size')
      .excludeRoot(true)
      .color(function(d: any) {
        if (d.name == "IN") {
            return "rgba(209, 120, 8, 0.8)";
        } else if (d.name == "OUT") {
            return "rgba(209, 54, 8, 0.8)" ;
        } else { 
            return "rgba(0, 0, 0, 0.3)" ;
        }
       })
      .onClick(this.clicking)
      .padding(0)
      (this.card);
  }

  clicking = (data: any) => {
    if (data) {
      if (data.name == "IN") {this.onInfo.emit(data.__dataNode.parent.data.name)}
      else if (data.name == "OUT") {this.onInfo.emit(data.__dataNode.parent.data.name)}
      else {this.onInfo.emit(data.name);}
      this.circle.zoomToNode(data);
    } else {
      this.circle.zoomReset();
      this.onInfo.emit("null");
    }
  }

}