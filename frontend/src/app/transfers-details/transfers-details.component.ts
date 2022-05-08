import { Component, OnInit, TemplateRef, Input, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { Subject } from "rxjs";
import { HttpClient } from '@angular/common/http';
import { Color, ScaleType } from '@swimlane/ngx-charts';
import { NbDialogService } from '@nebular/theme';

@Component({
  selector: 'app-transfers-details',
  templateUrl: './transfers-details.component.html',
  styleUrls: ['./transfers-details.component.scss']
})
export class TransfersDetailsComponent implements OnInit {

  @ViewChild('cardCube', {static: true}) cardContainer!: ElementRef<HTMLElement>;
  @Input() subject!: Subject<string>;
  infos: string = "null";
  prev: string = "null";
  loading: boolean = true;
  process: boolean = false;
  detail: any;
  percent: any;

  sum: any;
  colorScheme: Color = { domain: ['#D13608', '#D17808'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };

  view: any = [400, 300];

  constructor(private httpClient: HttpClient, private dialogService: NbDialogService) { 
    // this.loadScripts();
  }

  ngOnInit(): void {
    this.subject.subscribe((text: string) => {
      this.infos = text;

      if (this.infos == "null") {
        this.loading = true;
      }
      else if (this.prev != this.infos) {
        this.process = true;
        const url = "http://127.0.0.1:5000/details/" + this.infos;
        this.httpClient
          .get(url)
          .subscribe(this.responseDetail,
                    err => console.error('Ops: ', err.message),
                    () => console.log('Completed Detail'),
          );
      }
    });
  }

  ngAfterViewInit() {
    console.log(this.cardContainer);
    // this.cubeAnimation();
  }
  
  private responseDetail = (data: any): any => { 
    console.log("Response", data);
    this.detail = data;
    this.prev = this.infos;
    this.loading = false;
    this.process = false;
    this.sum = [{"name": "OUT", "value": this.detail['from_sum']},
                {"name": "IN", "value": this.detail['to_sum']}];
    this.percent = Math.round((this.detail['to_sum'] * 100 / this.detail['from_sum']) - 100);
  }

  open(dialog: TemplateRef<any>) {
    this.dialogService.open(dialog, { context: this.detail });
  }

  /* Conditional Classes */
  // getTypeColor({ row, column, value }): any {
  getTypeColor( prop: any): any {
    let row = prop['row'];
    console.log("TYPE", row['name']);
    return {
      'in-color': row['name'] === "IN", 
      'out-color': row['name'] === "OUT"
    };
  }

}
