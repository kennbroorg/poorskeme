import { Component, OnInit, TemplateRef, Input, ElementRef, ViewChild } from '@angular/core';
import { Subject } from "rxjs";
import { HttpClient } from '@angular/common/http';
import { Color, ScaleType } from '@swimlane/ngx-charts';
import { NbDialogService } from '@nebular/theme';

import { SingleSeries } from '@swimlane/ngx-charts';
import { ColumnMode, SelectionType } from '@swimlane/ngx-datatable/';
import { HighlightLoader, HighlightAutoResult } from 'ngx-highlightjs';

@Component({
  selector: 'app-trx-details',
  templateUrl: './trx-details.component.html',
  styleUrls: ['./trx-details.component.scss']
})
export class TrxDetailsComponent implements OnInit {

  @ViewChild('cardCube', {static: true}) cardContainer!: ElementRef<HTMLElement>;
  @Input() trx!: Subject<string>;
  // @Input() public h: any;

  h_table: any;
  hash: string = "null";
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
  colorScheme: Color = { domain: ['#CCF2FF', '#66D9FF'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };

  rows: any[] = [];
  selected: any[] = [];
  columns: any[] = [{ prop: 'name' }, { name: 'Company' }, { name: 'Gender' }];

  ColumnMode = ColumnMode;
  SelectionType = SelectionType;

  nodesConstructor: any;
  nodesFunctions: any;

  highlightedCode : any;
  response!: HighlightAutoResult;
  code!: string; 

  constructor(private httpClient: HttpClient, private hljsLoader: HighlightLoader) { }

  ngOnInit(): void {
    this.trx.subscribe((text: string) => {
      this.hash = text;
      console.log("TRX en trxdetails", this.hash);

      if (this.hash == "null") {
        // console.log(`Entro a Null con ${this.infos}`);
        this.loading = true;
        this.process = false;
      }
      else if (this.prev == this.hash) {
        this.loading = false;
        this.process = false;
      }
      else {
        // console.log(`Entro a Else con ${this.infos}`);
        this.loading = true;
        this.process = true;
        const url = "http://127.0.0.1:5000/trx_hash/" + this.hash;
        this.httpClient
          .get(url)
          .subscribe(this.responseDetail,
                    err => console.error('Ops: ', err.message),
                    () => console.log('Completed Detail'),
          );
      }
    });

    // this.h_table = this.h;
  }

  private responseDetail = (data: any): any => { 
    console.log("Response", data);
    this.detail = data;

    this.prev = this.hash;
    this.loading = false;
    this.process = false;

    this.nodesConstructor = [this.detail['constructor']];
    this.nodesFunctions = [this.detail['function']];
    this.code = this.detail['code']
    // console.log("TRX", this.detail['trx'], typeof(this.detail['trx']));
    // console.log("HASH", this.detail['constructor'], typeof(this.detail['constructor']));
  }

}
