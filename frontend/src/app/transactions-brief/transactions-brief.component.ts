import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Color, ScaleType } from '@swimlane/ngx-charts';

@Component({
  selector: 'app-transactions-brief',
  templateUrl: './transactions-brief.component.html',
  styleUrls: ['./transactions-brief.component.scss']
})
export class TransactionsBriefComponent implements OnInit {

  // TODO : Calculate screen dimension in app
  view: any = [600, 200];

  colorScheme: Color = { domain: ['#66D9FF', '#CCF2FF'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };

  trans: any = [];

  constructor(private httpClient: HttpClient) { 
  }

  ngOnInit(): void {
    const url = "http://127.0.0.1:5000/trans_info"
    this.httpClient
      .get(url)
      .subscribe(this.responseTransInfo,
                 err => console.error('Ops: ', err.message),
                 () => console.log('Completed Transaction Info'),
      );
  }

  private responseTransInfo = (data: any): any => {
    console.log(data);
    this.trans = data
  }

}
