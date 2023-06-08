import { Component, OnInit, TemplateRef, Input, Output, EventEmitter, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { Subject } from "rxjs";
import { HttpClient } from '@angular/common/http';
import { Color, ScaleType } from '@swimlane/ngx-charts';
import { NbDialogService } from '@nebular/theme';

import { SingleSeries } from '@swimlane/ngx-charts';
import { ColumnMode, SelectionType } from '@swimlane/ngx-datatable';

@Component({
  selector: 'app-transfers-details',
  templateUrl: './transfers-details.component.html',
  styleUrls: ['./transfers-details.component.scss']
})
export class TransfersDetailsComponent implements OnInit {

  @ViewChild('cardCube', {static: true}) cardContainer!: ElementRef<HTMLElement>;
  @Input() subject!: Subject<string>;
  @Input() public h: any;
  @Output() onTrx: EventEmitter<string> = new EventEmitter<string>();

  h_table: any;
  infos: string = "null";
  prev: string = "null";
  loading: boolean = true;
  process: boolean = false;
  detail: any;
  res_date: any;
  percent: any;
  perc: any;
  max: any;
  lp: any;

  sum: any;
  count: any;
  // colorScheme: Color = { domain: ['#D13608', '#D17808'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };
  colorScheme: Color = { domain: ['#CCF2FF', '#66D9FF'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };

  rows: any[] = [];
  selected: any[] = [];
  columns: any[] = [{ prop: 'name' }, { name: 'Company' }, { name: 'Gender' }];

  ColumnMode = ColumnMode;
  SelectionType = SelectionType;
  // view: any = [400, 300];

  constructor(private httpClient: HttpClient, private dialogService: NbDialogService) { 
    // this.loadScripts();
  }

  ngOnInit(): void {
    this.subject.subscribe((text: string) => {
      this.infos = text;
      // console.log(`Info: ${this.infos} = Prev: ${this.prev}`);

      if (this.infos == "null") {
        // console.log(`Entro a Null con ${this.infos}`);
        this.loading = true;
        this.process = false;
      }
      else if (this.prev == this.infos) {
        this.loading = false;
        this.process = false;
      }
      else {
        // console.log(`Entro a Else con ${this.infos}`);
        this.loading = true;
        this.process = true;
        const url = "http://127.0.0.1:5000/details/" + this.infos;
        this.httpClient
          .get(url)
          .subscribe(this.responseDetail,
                    err => console.error('Ops: ', err.message),
                    () => console.log('Completed Detail'),
          );
      }
      console.log(`LOADING: ${this.loading} - PROCESS: ${this.process}`)
    });

    this.h_table = this.h;
  }

  ngAfterViewInit() {
    // console.log(this.cardContainer);
    // this.cubeAnimation();

    // this.subject.subscribe((text: string) => {
    //   this.infos = text;
    //   console.log(`Info: ${this.infos}`);

    //   if (this.infos == "null") {
    //     this.loading = true;
    //   }
    //   // else if (this.prev != this.infos) {
    //   else {
    //     this.process = true;
    //     const url = "http://127.0.0.1:5000/details/" + this.infos;
    //     this.httpClient
    //       .get(url)
    //       .subscribe(this.responseDetail,
    //                 err => console.error('Ops: ', err.message),
    //                 () => console.log('Completed Detail'),
    //       );
    //   }
    //   console.log(`LOADING: ${this.loading} - PROCESS: ${this.process}`)
    // });
  }
  
  private responseDetail = (data: any): any => { 
    // console.log("Response", data);
    this.detail = data;

    this.res_date = this.TimelineConvert(this.detail['trans_vol'][0]['series']);
    this.detail['trans_vol'][0]['series'] = this.res_date;
    this.res_date = this.TimelineConvert(this.detail['trans_vol'][1]['series']);
    this.detail['trans_vol'][1]['series'] = this.res_date;

    // console.log(this.detail['trans_vol']);

    this.prev = this.infos;
    this.loading = false;
    this.process = false;
    this.sum = [{"name": "Deposit", "value": this.detail['from_sum']},
                {"name": "Withdraw", "value": this.detail['to_sum']}];
    this.count = [{"name": "Deposit", "value": this.detail['from_count']},
                  {"name": "Withdraw", "value": this.detail['to_count']}];
    // this.percent = Math.round((this.detail['to_sum'] * 100 / this.detail['from_sum']) - 100);
    this.percent = (this.detail['to_sum'] * 100 / this.detail['from_sum']) - 100;
    this.perc = Math.round(this.percent) + '%'
    this.max = Math.max(this.detail['from_sum'], this.detail['to_sum']);
    // console.log(`LOADING: ${this.loading} - PROCESS: ${this.process}`)
    if (this.percent > 0) {
      this.lp = "Profit"
    } else if (this.percent < 0) {
      this.lp = "Loss"
    } else {
      this.lp = "Without loss"
    }
  }

  open(dialog: TemplateRef<any>) {
    this.dialogService.open(dialog, { context: this.detail });
  }

  /* Conditional Classes */
  // getTypeColor({ row, column, value }): any {
  getTypeColor( prop: any): any {
    let row = prop['row'];
    // console.log("TYPE", row['name']);
    return {
      'in-color': row['name'] === "IN", 
      'out-color': row['name'] === "OUT"
    };
  }

  TimelineConvert(serie: any): SingleSeries {
    const res_conv: SingleSeries = [];

    for (const d of serie) {
      res_conv.push({
        name: new Date(d.name),
        value: d.value
      });
    }
    return res_conv;
  }

  onSelect(event: any) {
    // console.log('Event: select', event, this.selected);
    console.log('TRX: ', this.selected[0]['hash']);
    this.onTrx.emit(this.selected[0]['hash']);
  }

}
